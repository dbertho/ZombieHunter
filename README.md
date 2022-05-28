# ZombieHunter

Finds abandoned domain names still called for third-party scripts.<br/>

usage: zombiehunter.py [-h] [-n INT] [-r] FILE

positional arguments:<br/>
  FILE        file containing domains to check (one domain per line)

optional arguments:<br/>
  -h, --help  show this help message and exit<br/>
  -n INT      number of domains to check<br/>
  -r          option to randomize domains (if not set, the script will scan the list in order from top to bottom)
