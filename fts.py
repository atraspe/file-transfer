import sys
from pathlib import Path

import argparse
import logging

# CSV
import csv

# FTP
import ftplib

line = '=' * 70

def prompt(header, ask, response_type='int', main_dict=None, menu_dict=None):
    # Function to prompt the user for an argument that was not passed when calling the program
    #
    # can accept 2 dictionaries:
    #   i) dictionary used for displaying menu for the user to choose from
    #   ii) main dictionary from the gateway_hosts.csv or MS_client_accounts.csv

    while True:
        try:
            print(f'{line}\n{header}\n{len(header) * "-"}\n')
            if main_dict or menu_dict:
                d = menu_dict if menu_dict else main_dict
                counter = 0

                for k,v in d.items():
                    end_with = '\t'
                    
                    if counter == 4:
                        end_with = '\n'
                        counter = -1
                    print(f'{k} : {v}', end=end_with)
                    counter += 1

            print()
            answer = input(f'{ask}')

            # if prompt is expecting an answer that is an integer or string
            if response_type == 'str':
                answer = str(answer)
            else:
                answer = int(answer)

            # if no dictionary is passed (e.g. Username), then return that user input        
            choice = answer

            if menu_dict:
                choice_tmp = menu_dict[answer]
                answer = choice_tmp
            if main_dict or menu_dict:
                choice = main_dict[answer]

        except (ValueError, KeyError) as err:
            print('\n!!! Invalid selection...\n')
        else:
            print()
            return choice


if __name__ == '__main__':
    prog_desc = 'purpose: transfer file to or from a host that is behind a UNIX gateway. unless specified (as binary), file will be treated as ASCII.'
    choice_text = 'Your choice: '
    action = {1 : 'download', 2 : 'upload'}
    
    parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
    parser.add_argument('file', help='file to be transferred')
    parser.add_argument('-b', '--binary', help='if not specified, file will be treated as ASCII', action='store_true')
    parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
    parser.add_argument('-u', '--username', help='Gateway username')
    parser.add_argument('-p', '--passcode', help='MobilePASS OHGate - IDLDAP.NET passcode')
    parser.add_argument('-i', '--instance', help='MS client instance')
    parser.add_argument('-a', '--action', help='download or upload')
    parser.add_argument('-v', '--verbose', help='explain what is being done', action='store_const', const=logging.INFO, dest='loglevel')
    parser.add_argument('-h', '--help', help='show this help message and exit', action='help')

    args = parser.parse_args()

    # Logging; does not include the levelname(severity) in the messages, only the date/time stamp and message
    logging.basicConfig(level=args.loglevel, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')

    print(line)
    logging.info(f'Executing {__file__}...')
    logging.info('Loading configuration...')

    # ms_non_ms = prompt('Connect to:\n-----------\n1) MS host\n2) Non-MS host\n\nYour choice: ')

    # =====================================================================================================================================
    # parse the csv (MS_client_accounts.csv) for client environment information
    filename = 'MS_client_accounts.csv'
    file = Path(filename)
    if not file.exists():
        print(f'{filename} does not exist!')
        logging.info('Terminating program...')
        sys.exit()
    
    csv_file = open(filename, newline='')
    reader = csv.reader(csv_file)

    # sample dictionary for storing client environment information
    # use instance as key when searching, value is a list of hostname, password and clientid, respectively
    # {'buaour1' : ['lit-vams-b102.gxsonline.net', '7Ey4s|Ms', 'UAOUR'], 'bcarmx1' : ['lit-vams-b102.gxsonline.net', '59K>oSgs', 'CARMX']}

    # parse the csv's header
    header_list = next(reader)

    # need separate dictionaries: first for the menu in the user prompt (if --instance is not invoked as a parameter),
    #                             second for the main dictionary
    instance_menu = {}
    client_accounts = {}
    counter = 1
    temp_list = []  # need to put all instances in a list first, then sort later on so they'll be in alphabetical order when shown in the menu

    for row in reader:
        temp_list.append(row[0].lower())
        client_accounts[row[0]] = [row[1], row[2], row[3]]
        counter += 1
    
    temp_list.sort()
    counter = 1

    for item in temp_list:
        instance_menu[counter] = item
        counter += 1
    
    # print(f'menu dict: {instance_menu}')
    # print(f'instances hosts: {client_accounts}')

    # =====================================================================================================================================
    # parse the csv (gateway_hosts.csv) for UNIX gateway information
    filename = 'gateway_hosts.csv'
    file = Path(filename)
    if not file.exists():
        print(f'{filename} does not exist!')
        logging.info('Terminating program...')
        sys.exit()
    
    csv_file = open(filename, newline='')
    reader = csv.reader(csv_file)

    # parse the csv's header
    header_list = next(reader)

    # need separate dictionaries for the user prompt menu (if --gateway is not invoked as a parameter) and the main gateway dictionary
    gateways_menu = {}
    gateway_hosts = {}
    counter = 1
    
    for row in reader:
        gateways_menu[counter] = row[0].lower()
        counter += 1
        gateway_hosts[row[0].lower()] = row[1]


    # =====================================================================================================================================
    
    # parser.add_argument('-b', '--binary', help='if not specified, file will be treated as ASCII', action='store_true')
    # parser.add_argument('-p', '--passcode', help='MobilePASS OHGate - IDLDAP.NET passcode')
    # parser.add_argument('-a', '--action', help='download or upload')
    
    # determine which parameters were not passed when calling the program
    
    if args.gateway:
        args.gateway = args.gateway.lower()

    # if no --gateway argument passed, or if not recognized
    if args.gateway in gateway_hosts.keys():
        args.gateway = gateway_hosts[args.gateway]
    elif args.gateway not in gateway_hosts.values():
        args.gateway = prompt(header='Gateway', ask=choice_text, main_dict=gateway_hosts, menu_dict=gateways_menu)

    # if no --username argument passed
    if not args.username:
        args.username = prompt(header='Username', ask='Enter username: ', response_type='str')

    # if no --instance argument passed
    if not args.instance:
        args.instance = prompt(header='Instance', ask=choice_text, main_dict= client_accounts, menu_dict=instance_menu)

    # if no --action argument passed
    if not args.action:
        args.action = prompt(header='Action', ask=choice_text, main_dict=action)

    print(f'Gateway: {args.gateway}')
    print(f'Server: {args.instance[0]}')
    print(f'Password: {args.instance[1]}')
    print(f'ClientID: {args.instance[2]}')

    # FTP
    ftp_host = 'lit-vabld-q023.gxsonline.net'
    # ftp_host = 'ohmg0005.ohctr.gxs.com'
    ftp_user = 'art'
    ftp_passwd = 'art123'


    print(line)
    logging.info(f'Connecting to {ftp_host}:21...')

    with ftplib.FTP(host=ftp_host) as ftp:
        try:
            ftp.login(user=ftp_user, passwd=ftp_passwd)
            logging.info('Connection established, waiting for welcome message...')
            # ftp.cwd('/qual/art/ot/otdev/dev5.3/art')
            ftp.getwelcome()
            logging.info('Logged in...')

            if args.binary:
                ftp.sendcmd('TYPE I')
            else:
                ftp.sendcmd('TYPE A')
            # ftp.retrlines('LIST')
            
            logging.info(f'Starting {args.action} of {args.file}')

            with open(args.file, 'w') as new_file:
                result = ftp.retrbinary(f'RETR {args.file}', new_file.write)
        except ftplib.all_errors as e:
            logging.info(f'FTP error: {e}')
        else:
            print('Disconnected from server')

    logging.info('end')
