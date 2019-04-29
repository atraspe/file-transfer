import sys
from pathlib import Path
import argparse

# SSH
import base64
import paramiko

# FTP
import ftplib


prog_desc = 'purpose: transfer file to or from a host that is behind a UNIX gateway.'
line = '============================================================================'
gateway_desc = 'UNIX gateway to be used. Currently supported gateways are:\ngate-sn.avctr.gxs.com (Amstelveen)\n and gate-sn.ohctr.gxs.com (Ohio).'

parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
parser.add_argument('file', help='file to be transferred')
parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
parser.add_argument('-u', '--username', help='Gateway username')
parser.add_argument('-t', '--token', help='RSA SecurID token ID')
parser.add_argument('-i', '--instance', help='instance')
parser.add_argument('-a', '--action', help='download or upload')
parser.add_argument('-v', '--verbose', help='explain what is being done', action='store_true')
parser.add_argument('-h', '--help', help='show this help message and exit', action='help')#, default=argparse.SUPPRESS)

args = parser.parse_args()

gateway = {1 : 'gate-sn.ohctr.gxs.com', 2 : 'gate-sn.avctr.gxs.com'}
instance = {1 : 'baldis1', 2 : 'baldis2'}
action = {1 : 'download', 2 : 'upload'}

# sample dictionary for client accounts {'instance' : {'hostname' : 'x', 'ftp password' : 'abc', 'clientid' : 'XYZ'}}
client_accounts = {'buaour1' : {'hostname' : 'lit-vams-b102.gxsonline.net', 'password' : '7Ey4s|Ms', 'clientid' : 'UAOUR'}}

def ask(question, dict_val):
    while True:
        try:
            print(line)
            answer = int(input(question))
            choice = dict_val[answer]
        except (ValueError, KeyError):
            print('\n!!! Invalid selection...\n')
        else:
            print()
            return choice

print(line)

if args.verbose:
    print(f'Executing {__file__}...\n')
    # print('Gathering missing information...\n')

# ms_non_ms = ask('Connect to:\n-----------\n1) MS host\n2) Non-MS host\n\nYour choice: ')

if not args.gateway:
    args.gateway = ask('Gateway\n-------\n1) gate-sn.ohctr.gxs.com\n2) gate-sn.avctr.gxs.com\n\nYour choice: ', gateway)
if not args.instance:
    args.instance = ask('Instance:\n---------\n1) instance1\n2) instance2\n\nYour choice: ', instance)
if not args.action:
    args.action = ask('Action:\n-------\n1) download\n2) upload\n\nYour choice: ', action)

print(f"""Gateway: {args.gateway}
Server: {args.instance}
""")

# SSH
"""
key = paramiko.RSAKey(data=base64.b64decode(b'AAAAB3NzaC1kc3MAAACBAIWAZOeAHLpKxfdjeJ6VYeJRLPODV23aBJfAiOb7vAq39FElq4IJCQX80Ba5aVA4cAy9FOwwd+btnSj2ZOOazYtjI6RmAXN7ITRCuo+w+3GYlYH4JMVGDz0MGz5NbTgENWyf6Wygba5kFoQItYvc/uxsf5ekj9azeO0LW0okq/+bAAAAFQDMwX9xGV3Dr0y7+Tb0+A0UJwpZIwAAAIBt0dO7whKYI7ayY84gQ1/SN6pfZ++f3qiOT9G6o0goEPQ/UubDEAq2ucip0qumJjN5R+IEgJ02w4xrA8pPuwRjuI+iQcu+QClSE+3rxE02dvpjJr3cmmg7HfIHb91dfJoZaLPYS5YafcPd8nvHa8u68PcY524nrupem/pn1CQNTwAAAIA6eib1GWl7lAzKNpb8q633kCxJy2Ep+e+w+Jo8CCBGWtqJYTk/zS4zrf3LsxOiv+SzlsQWSeiAb8ShjxcpWpNvrHjnBhzJRFQVB+QngetO+0PU6PudGVdT+42G0zHUhUZRLXHAejaa2vEhfkITpaH2cN4OLXAC3spajdStzMLMmg=='))
client = paramiko.SSHClient()
client.get_host_keys().add('gate-sn.ohctr.gxs.com', 'ssh-rsa', key)
host = 'gate-sn.ohctr.gxs.com'
username = 'atraspe'
port = 22
password = '95099509819389'
client.connect(host, port, username, password)
stdin, stdout, stderr = client.exec_command('ls')
for line in stdout:
    print('... ' + line.strip('\n'))
client.close()
"""

# FTP
ftp_host = 'lit-vabld-q023.gxsonline.net'
ftp_user = 'art'
ftp_passwd = 'art123'


if args.verbose:
    print(f'{line}\nConnecting to {ftp_host}:21...')

with ftplib.FTP(host=ftp_host) as ftp:
    try:
        ftp.login(user=ftp_user, passwd=ftp_passwd)
        if args.verbose:
            print('Connection established, waiting for welcome message...')
        # ftp.cwd('/qual/art/ot/otdev/dev5.3/art')
        ftp.getwelcome()
        if args.verbose:
            print('Logged in...')
        # ftp.sendcmd()
        # ftp.retrlines('LIST')
        if args.verbose:
            print(f'Starting {args.action} of {args.file}')
        ftp.retrbinary(f'RETR {args.file}', open(args.file, 'wb').write)
    except ftplib.all_errors as e:
        print(f'FTP error: {e}')
    else:
        print('Disconnected from server')

print('end')
