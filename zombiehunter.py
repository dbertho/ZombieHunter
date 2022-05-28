import requests
import json
import tldextract
import validators
from bs4 import BeautifulSoup
import concurrent.futures
import argparse
import sys
import time
import random

domains = []
found_domains = set()

def queryWhois(domain):
    querystring = {"name":domain}
    apiKey = 'Your Gandi API key'
    url_api = "https://api.gandi.net/v5/domain/check"
    headers_api = {'authorization' : 'Apikey ' + apiKey}
    details = requests.request("GET", url_api, headers=headers_api, params=querystring)
    print("Checking availability: "+domain)
    result = json.loads(details.text)
    if result['products'][0]['status'] == "available":
        print(domain+" available!")
        domains.append(domain)

def is_available(domain):
    queryWhois(domain)

def extract_domain(url):
    extdomain = tldextract.extract(url)
    return extdomain.domain + "." + extdomain.suffix

def parse_website(site):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'accept-encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8', 'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1', 'referer': 'https://google.com/'}
    print("Testing "+site)
    try:
        source_code = requests.get('http://' + site, headers=headers, timeout=5)
        soup = BeautifulSoup(source_code.content, features="html.parser")

        for link in soup.find_all('script', src=True):
            domain = extract_domain(str(link.get('src')))
            if validators.domain(domain):
                found_domains.add(domain)

    except requests.exceptions.RequestException as e:
        print(site + ": Something's not right... skipping website")
        pass

def main():
    futures = []

    start_time = time.time()

    parser = argparse.ArgumentParser(description='Finds abandoned domain names still called for third-party scripts.')
    parser.add_argument('f', type=str, help='file containing domains to check (one domain per line)', metavar='FILE')
    parser.add_argument('-n', type=int, default=0, help='number of domains to check', metavar="INT")
    parser.add_argument("-r", default=False, action="store_true", help="option to randomize domains (if not set, "
                                                                    "the script will scan the list in order from top "
                                                                    "to bottom)")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    
    file_sites = args.f
    file = open(file_sites, "r")
    file_contents = file.read()
    sites_list = file_contents.splitlines()
    
    if args.r:
        random.shuffle(sites_list)

    number_sites = 0
    if args.n == 0:
        number_sites = len(sites_list)
    else:
        number_sites = args.n

    print("")
    print("---------------------------------------------------")
    print("Sites list: " + file_sites)
    if args.n == 0:
        print("Number of sites to be checked: " + str(number_sites) + ' (full list)')
    else:
        print("Number of sites to be checked: " + str(number_sites))
    print("Random check: " + str(args.r))
    print("---------------------------------------------------")
    print("")

    increment = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for site in sites_list:
            futures.append(
                executor.submit(parse_website, site)
            )
            increment += 1
            if increment >= number_sites:
                break
    
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executorWhois:
        for domain in found_domains:
            futures.append(
                executorWhois.submit(is_available(domain))
            )

    print("")
    print("Available domains:")
    print(domains)
    print("Execution time: ")
    print("%s seconds" % (time.time() - start_time))

if __name__ == "__main__":
    main()