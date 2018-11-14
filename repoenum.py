#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
import urllib2
import sys
import argparse
import ssl
import tableprint as tp
import pandas as pd
import shodan
from bs4 import BeautifulSoup
import dash
import dash_html_components as html
import dash_table_experiments as dt
from datetime import datetime
import maxminddb
from config import banner as Banners
from config.banner import Colors

class RepoEnumDash(dash.Dash):
    def interpolate_index(self, **kwargs):
        return '''<!DOCTYPE html>
<html>
    <head>
        {metas}
        <title>Repo Enum Results - Gitlab Servers</title>
        {css}
    </head>
    <body>
        {app_entry}
        <br>
        <footer>
            <small>Rendered at: {ts}</small>
            {config}
            {scripts}
        </footer>
    </body>
</html>'''.format(
metas=kwargs['metas'],
css=kwargs['css'],
app_entry=kwargs['app_entry'],
config=kwargs['config'],
scripts=kwargs['scripts'],
ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class EnumServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.title = ''
        self.signup = None
        self.public = None
        self.public_qtde = 0
        self.iso_code = None
        self.country = None

    def make_request(self, path='/'):
        _target_80 = "http://%s%s" % (self.host, path)
        _target_443 = "https://%s%s" % (self.host, path)
        _target_except = "http://%s:%i%s" % (self.host, self.port, path)

        if self.port == 80:
            target = _target_80
        elif self.port == 443:
            target = _target_443
        else:
            target = _target_except

        try:
            context = ssl._create_unverified_context()
            body = urllib2.urlopen(target, context=context, timeout=10)
            contents = body.read()
            return contents
        except urllib2.URLError, e:
            print Colors.RED + "\n Connection to %s on port %i and path %s failed (URL): %s" % (self.host, self.port, path, e)
        except ssl.SSLError, e:
             print Colors.RED + "\n Connection to %s on port %i and path %s failed (SSLError): %s" % (self.host, self.port, path, e)
        except socket.timeout:
            print Colors.RED + "\n Connection to %s on port %i and path %s failed" % (self.host, self.port, path)
        except socket.error, e:
            print Colors.RED + "\n Connection to %s on port %i and path %s failed (socket.error): %s" % (self.host, self.port, path, e)
        except Exception as e:
            print Colors.RED + "\n Connection to %s on port %i and path %s failed (generic error): %s" % (self.host, self.port, path, e)

    def consult_signup(self):
        # Request - Allow to create user?
        contents = self.make_request()

        if contents:
            soup = BeautifulSoup(contents, 'html.parser')

            try:
                if soup.body.find('h1').text:
                    self.title = soup.body.find('h1').text.encode('utf-8').strip()

                else:
                    soup.html.head.title.text
                    self.title = soup.html.head.title.text.encode('utf-8').strip()
            except:
                self.title = "Unknown Repository"

            if (not self.title) or (len(self.title) <= 0):
                self.title = "Unknown Repository"

            # Parser - repo allow to create user?
            if (soup.find_all("input", class_ = "btn-create btn") or soup.find_all("input", class_ = "btn-register btn")):
                self.signup = True

    def consult_public(self):
        # Request - Public projects
        contents = self.make_request('/explore/projects')

        if contents:
            soup = BeautifulSoup(contents, 'html.parser')
            # Parser - Public projects?
            public_repos = soup.find_all("span", class_ = "project-name")
            self.public_qtde = int(len(public_repos))
            if (self.public_qtde > 0):
                self.public = True

    def show_result(self):
        results = []
        results.append("%s:%i" % (host, port))
        results.append(self.iso_code)
        results.append(self.country)
        results.append(Colors.BLUE + 'YES' + Colors.DEFAULT if self.signup else Colors.RED + 'NO' + Colors.DEFAULT)
        results.append(Colors.BLUE + 'YES' + Colors.DEFAULT if self.public else Colors.RED + 'NO' + Colors.DEFAULT)

        headers = [
            Colors.BR_COLOUR + 'Repository' + Colors.DEFAULT,
            Colors.BR_COLOUR + 'Country Code' + Colors.DEFAULT,
            Colors.BR_COLOUR + 'Country Name' + Colors.DEFAULT,
            Colors.BR_COLOUR + 'Allow to create user' + Colors.DEFAULT,
            Colors.BR_COLOUR + 'Public Projects' + Colors.DEFAULT
        ]

        print Colors.WHITE + "\n [+] Repository Title:\t" + Colors.ORANGE + str(self.title) + Colors.DEFAULT
        tp.table([results], headers, width=20)

    def consult_geo(self):
       geodb = maxminddb.open_database('GeoLite2-Country.mmdb')
       s = geodb.get(self.host)
       try:
           self.iso_code = s['country']['iso_code']
       except:
           self.iso_code = "Null"
           
       try: 
           self.country = s['country']['names']['en']
       except:
           self.country = "Null"

class EnumResults:
    def __init__(self):
        self.output_filename = 'enum_results_%s.csv' % (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        self.server_buff = []

    def add(self, server):
        self.server_buff.append({
            'Title Gitlab' : str(server.title).decode('utf-8'),
            'Host': server.host,
            'Port' : str(server.port),
            'Country Code' : server.iso_code,
            'Country Name' : server.country,
            'Create User' : 'YES' if server.signup else 'NO',
            'Public Projects' : 'YES' if server.public else 'NO'
        })

    def persist_partial(self):
        last = self.server_buff[-1]
        enum_results = pd.DataFrame([last])
        enum_results.to_csv(self.output_filename + '_partial', mode='a', index=False, header=False, encoding='utf-8')

    def persist_file(self):
        enum_results = pd.DataFrame(self.server_buff, columns = ['Title Gitlab', 'Host', 'Port', 'Country Code', 'Country Name', 'Create User', 'Public Projects'])
        enum_results.to_csv(self.output_filename, mode='a', index=False, header=True, encoding='utf-8')

    def show_table(self):
        enum_results = pd.read_csv(self.output_filename)
        app = RepoEnumDash()
        app.scripts.config.serve_locally = True
        app.layout = html.Div([
            html.H4('Repo Enum Results - Gitlab Servers'),
            dt.DataTable(
                rows=enum_results.to_dict('records'),
                columns=enum_results.columns,
                editable=False,
                row_selectable=False,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='datatable'
            )
        ], className="container")
        app.run_server(debug=False)

    def finish_results(self):
        print Colors.YELLOW + Banners.bye + Colors.DEFAULT
        self.persist_file()
        self.show_table()


if __name__ == '__main__':
    print Colors.RED + Banners.welcome + Colors.DEFAULT

    parser = argparse.ArgumentParser(prog='reposcan.py',
                                    description=' [+] Obtaining a list of misconfigured repositories',
                                    epilog=' [+] Usage: python repoenum.py -f /home/user/repos_servers.csv',
                                    version="2.0")
    parser.add_argument('-s', dest="shodan", help='Usage shodan api')
    parser.add_argument('-f', dest="file", help='Usage csv file')
    parser.add_argument('-l', dest="limit", help='Limit the server amount')
    parser.add_argument('-g', dest="generate_table", help='Generate live table')
    args = parser.parse_args()
    
    if args.generate_table:
        file = args.generate_table
    
        try:
            with open(file, 'r') as f:
                servers = pd.read_csv(file)
            app = RepoEnumDash()
            app.scripts.config.serve_locally = True
            app.layout = html.Div([
                html.H4('Repo Enum Results - Gitlab Servers'),
                dt.DataTable(
                    rows=servers.to_dict('records'),
                    columns=servers.columns,
                    editable=False,
                    row_selectable=False,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='datatable'
                )
            ], className="container")
            app.run_server(debug=False)
            print Colors.YELLOW + Banners.bye + Colors.DEFAULT
            sys.exit(0)
        except Exception:
            print "Error to open the file: %s" % (file)
            print Colors.YELLOW + Banners.bye + Colors.DEFAULT
            sys.exit(2)
    
    
    if args.limit:
        try:
            limit = int(args.limit)
        except:
            parser.error('The limit must be a integer number')
    
        if limit <= 1:
            parser.error('The number must be greater than one')
    else:
        limit = None
    
    if not (args.shodan or args.file):
            parser.error('[!] An argument is required. Eg. -f, -s or -g!')
    
    if args.shodan:
        SHODAN_API_KEY = args.shodan
    
        try:
            api = shodan.Shodan(SHODAN_API_KEY)
            print(' [~] Checking Shodan.io API Key: %s' % SHODAN_API_KEY)
            results = api.search('Title:Gitlab', limit=limit)
            print(' [✓] API Key Authentication: SUCCESS')
            print(' [~] Number of present Gitlab Servers: %s' % results['total'])
            print('')
    
            servers = pd.DataFrame({'host': [], 'port': []})
            for result in results['matches']:
                servers = servers.append({'host': result['ip_str'], 'port': result['port']}, ignore_index=True)
            servers.to_csv('shodan.csv', mode='a', index=False, header=False, encoding='utf-8')
    
        except shodan.APIError as e:
            print(u' [✘] Error: %s' % e)
            sys.exit(2)
    else:
        file = args.file
    
        try:
            with open(file, 'r') as f:
                servers = pd.read_csv(file,
                                      names = ["host", "port"])
                servers = servers.loc[0:limit]
        except Exception:
            print "Error to open the file: %s" % (file)
            sys.exit(2)
    
    r = EnumResults()
    try:
        for index, row in servers.iterrows():
            host = row['host']
            port = int(row['port'])
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(5)
                client.connect((host, port))
                client.close()
            except socket.error, e:
                print Colors.RED + "\n [-] Connection to %s on port %s failed: %s" % (host, port, e) + Colors.DEFAULT
                continue
            except socket.timeout, e:
                print Colors.RED + "\n [-] Connection timed out to %s on port %s: %s" % (host, port, e) + Colors.DEFAULT
                continue

            elem = EnumServer(host, port)
            try:
                elem.make_request()
            except urllib2.URLError, e:
                print "\n [-] Connection to %s on port %s failed: %s" % (host, port, e)
                continue

            try:
                elem.consult_signup()
                elem.consult_public()
                elem.consult_geo()
                elem.show_result()
                r.add(elem)
                r.persist_partial()
            except urllib2.URLError, e:
                print "\n [-] Connection to %s on port %s failed: %s" % (host, port, e)
                continue
        r.finish_results()
    except KeyboardInterrupt:
        r.finish_results()
        exit()