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

gateways = {1 : 'gate-sn.ohctr.gxs.com', 2 : 'gate-sn.avctr.gxs.com'}
servers = {1 : 'server1', 2 : 'server2'}
choice = lambda question : int(input(question))

print(line)
if args.verbose:
    print(f'Executing {__file__}...\n')
    print('Gathering missing information...\n')
    print('Gateway\n-------')
    if not args.gateway:
        args.gateway = gateways[choice('Gateway to use: ')]
    if not args.server:
        args.server = servers[choice('Server to connect to: ')]

print(args.gateway)
print(args.server)