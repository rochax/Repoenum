[![Python 2.7|3.6](https://img.shields.io/badge/Python-2.7-blue.svg)](https://www.python.org/) [![Repoenum 2.0](https://img.shields.io/badge/Repoenum-2.0-brightgreen.svg)](https://rochax.github.io)



	   ▄████████    ▄████████    ▄███████▄  ▄██████▄          ▄████████ ███▄▄▄▄   ███    █▄    ▄▄▄▄███▄▄▄▄
	  ███    ███   ███    ███   ███    ███ ███    ███        ███    ███ ███▀▀▀██▄ ███    ███ ▄██▀▀▀███▀▀▀██▄
	  ███    ███   ███    █▀    ███    ███ ███    ███        ███    █▀  ███   ███ ███    ███ ███   ███   ███
	 ▄███▄▄▄▄██▀  ▄███▄▄▄       ███    ███ ███    ███       ▄███▄▄▄     ███   ███ ███    ███ ███   ███   ███
	▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ▀█████████▀  ███    ███      ▀▀███▀▀▀     ███   ███ ███    ███ ███   ███   ███
	▀███████████   ███    █▄    ███        ███    ███        ███    █▄  ███   ███ ███    ███ ███   ███   ███
	  ███    ███   ███    ███   ███        ███    ███        ███    ███ ███   ███ ███    ███ ███   ███   ███
	  ███    ███   ██████████  ▄████▀       ▀██████▀         ██████████  ▀█   █▀  ████████▀   ▀█   ███   █▀
	  ███    ███


## WARNING ##
```
 +---------------------------------------------------+
 | DEVELOPERS ASSUME NO LIABILITY AND ARE NOT        |
 | RESPONSIBLE FOR ANY MISUSE OR DAMAGE CAUSED BY    |
 | THIS PROGRAM                                      |
 +---------------------------------------------------+
```
### DESCRIPTION ###
```
Repoenum is a tool for enumeration Gitlab repositories misconfigured and that possibly expose sensitive data.
```
### INSTALL ###
```
$ git clone https://github.com/rochax/Repoenum

$ cd Repoenum

~/Repoenum $ pip install -r requirements.txt
```
### REQUIRIMENTS ###
```
setuptools
wheel
beautifulsoup4
six
future
tableprint
shodan
maxminddb
plotly
pandas
dash_table_experiments
dash_core_components
dash==0.28.5
dash-html-components==0.13.2
```
### USAGE ###
```
    Usage: ./repoenum.py [options]

    -s', 	'Usage shodan api'
    -f', 	'Usage csv file'
    -l', 	'Limit the server amount. Use after -s or -f option')
    -g', 	'Generate live table')
```
### EXAMPLE ###
Using a csv file to enumerate all repositories from the list. 
```
repoenum.py -f repos_servers.csv
```
Using a shodan API Key to enumerate just 50 repositories from the list. 
```
repoenum.py -s "SHODAN API KEY" -l 50
```
### Grabbing Gitlab Servers exposed ###
```
[+] SHODAN: http://shodan.io/search?query=title%3Agitlab

[+] CENSYS: https://censys.io/ipv4?q=80.http.get.title%3Agitlab

[+] Google Dorks: intitle:gitlab inurl:explore -gitlab.com/explore

```
##### Thnaks for help #####
[Fernando A. Damião](https://github.com/fadamiao)

