import sys
from pathlib import Path
import argparse

prog_desc = 'Purpose: Transfer file to or from a host that is behind a UNIX gateway.'
line = '==============================================================================='
gateway_desc = 'UNIX gateway to be used. Currently supported gateways are:\ngate-sn.avctr.gxs.com (Amstelveen)\n and gate-sn.ohctr.gxs.com (Ohio).'

parser = argparse.ArgumentParser(description=prog_desc)
parser.add_argument('file', help='file to be transferred')
parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
parser.add_argument('-s', '--server', help='server to upload to or download from')
parser.add_argument('-t', '--token', help='RSA SecurID token ID')
parser.add_argument('-u', '--username', help='username')
parser.add_argument('-v', '--verbose', help='explain what is being done', action='store_true')

args = parser.parse_args()

gateway = {1 : 'gate-sn.ohctr.gxs.com', 2 : 'gate-sn.avctr.gxs.com'}
server = {1 : 'server1', 2 : 'server2'}

def ask(question):
    while True:
        try:
            choice = int(input(question))
        except:
            print('!!! Invalid selection...\n')
        else:
            return choice

print(line)

if args.verbose:
    print(f'Executing {__file__}...\n')
    print('Gathering missing information...\n')

if not args.gateway:
    print('\nGateway\n-------')
    args.gateway = gateway[ask('1) gate-sn.ohctr.gxs.com\n2) gate-sn.avctr.gxs.com\nGateway to use: ')]
if not args.server:
    print('\nServer\n------')
    args.server = server[ask('1) server1\n2) server2\nServer to connect to: ')]

print(f'Gateway: {args.gateway}')
print(f'Server: {args.server}')