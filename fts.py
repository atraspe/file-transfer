import sys
from pathlib import Path
import argparse

# CSV
import csv

# FTP
import ftplib



prog_desc = 'purpose: transfer file to or from a host that is behind a UNIX gateway. unless specified (as binary), file will be treated as ASCII.'
line = '============================================================================'

parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
parser.add_argument('file', help='file to be transferred')
parser.add_argument('-b', '--binary', help='if not specified, file will be treated as ASCII', action='store_true')
parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
parser.add_argument('-u', '--username', help='Gateway username')
parser.add_argument('-p', '--passcode', help='MobilePASS OHGate - IDLDAP.NET passcode')
parser.add_argument('-i', '--instance', help='MS client instance')
parser.add_argument('-a', '--action', help='download or upload')
parser.add_argument('-v', '--verbose', help='explain what is being done', action='store_true')
parser.add_argument('-h', '--help', help='show this help message and exit', action='help')

args = parser.parse_args()


def prompt(header, ask, response_type='str', main_dict=None, temp_dict=None):
    while True:
        try:
            print(f'{line}\n{header}')
            if main_dict or temp_dict:
                d = temp_dict if temp_dict else main_dict

                for k,v in d.items():
                    print(f'{k} : {v}')

            answer = input(f'{ask}')
            choice = answer

            if response_type == 'int':
                answer = int(answer)

            if temp_dict:
                choice_tmp = temp_dict[answer]
                answer = choice_tmp
            if main_dict or temp_dict:
                choice = main_dict[answer]

        except (ValueError, KeyError) as err:
            print('\n!!! Invalid selection...\n')
            # print(err)
        else:
            print()
            return choice

print(line)

if args.verbose:
    print(f'Executing {__file__}...')
    print('Loading configuration...')

# ms_non_ms = prompt('Connect to:\n-----------\n1) MS host\n2) Non-MS host\n\nYour choice: ')

# =====================================================================================================================================
# parse the csv (MS_client_accounts.csv) for client environment information
filename = 'MS_client_accounts.csv'
csv_file = open(filename, newline='')
reader = csv.reader(csv_file)

# sample dictionary for storing client environment information
# use instance as key when searching, value is a list of hostname, password and clientid, respectively
# {'buaour1' : ['lit-vams-b102.gxsonline.net', '7Ey4s|Ms', 'UAOUR'], 'bcarmx1' : ['lit-vams-b102.gxsonline.net', '59K>oSgs', 'CARMX']}

# parse both header and the rest of the rows
header_list = next(reader)
client_accounts = { row[0] : [row[1], row[2], row[3]] for row in reader}

# =====================================================================================================================================
# parse the csv (gateway_hosts.csv) for UNIX gateway information
filename = 'gateway_hosts.csv'
csv_file = open(filename, newline='')
reader = csv.reader(csv_file)

header_list = next(reader)

# need separate dictionaries for the user prompt (if --gateway is not invoked as a parameter) and the main gateway dictionary
gateways_tmp = {}
gateway_hosts = {}
counter = 1
for row in reader:
    gateways_tmp[counter] = row[0].lower()
    counter += 1
    gateway_hosts[row[0].lower()] = row[1]

instance = {1 : 'baldis1', 2 : 'baldis2'}
action = {1 : 'download', 2 : 'upload'}

# determine parameters missing
# parser.add_argument('-b', '--binary', help='if not specified, file will be treated as ASCII', action='store_true')
# parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
# parser.add_argument('-u', '--username', help='Gateway username')
# parser.add_argument('-p', '--passcode', help='MobilePASS OHGate - IDLDAP.NET passcode')
# parser.add_argument('-i', '--instance', help='MS client instance')
# parser.add_argument('-a', '--action', help='download or upload')


# if no --gateway argument passed, or if not recognized
if args.gateway.lower() in gateway_hosts.keys():
    args.gateway = gateway_hosts[args.gateway.lower()]
elif args.gateway.lower() not in gateway_hosts.values():
    args.gateway = prompt(header='Gateway\n-------\n', ask='\nYour choice: ', response_type='int', main_dict=gateway_hosts, temp_dict=gateways_tmp)

if not args.username:
    args.username = prompt(header='Username\n--------\n', ask='Enter username: ')
# if not args.instance:
#     args.instance = prompt('Instance:\n---------\n1) instance1\n2) instance2\n\nYour choice: ', instance)
if not args.action:
    args.action = prompt('Action:\n-------\n', ask='\nYour choice: ', main_dict=action, response_type='int')

print(f"""Gateway: {args.gateway}
Server: {args.instance}
""")


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
        if args.binary:
            ftp.sendcmd('TYPE I')
        else:
            ftp.sendcmd('TYPE A')
        # ftp.retrlines('LIST')
        if args.verbose:
            print(f'Starting {args.action} of {args.file}')
        ftp.retrbinary(f'RETR {args.file}', open(args.file, 'wb').write)
    except ftplib.all_errors as e:
        print(f'FTP error: {e}')
    else:
        print('Disconnected from server')

print('end')
