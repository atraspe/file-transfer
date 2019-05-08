import sys
from pathlib import Path

import argparse, logging, math, getpass

# CSV
import csv

# FTP
import ftplib

line = '=' * 72

def prompt(header, ask, response_type='int', main_dict=None, menu_dict=None):
    # function to prompt the user for an argument that was not passed when calling the program
    #
    # can accept 2 dictionaries:
    #   i) dictionary used for displaying menu for the user to choose from
    #   ii) main dictionary from the gateway_hosts.csv or MS_client_accounts.csv

    while True:
        try:
            print(f'{line}\n{header}\n{len(header) * "-"}\n')
            if main_dict or menu_dict:
                d = menu_dict if menu_dict else main_dict
                # determine the length of the dictionary for right justification in the user prompt menu
                right_j = int(math.log10(len(d))) + 1   
                counter = 0

                for k,v in d.items():
                    end_with = '\t'
                    
                    if counter == 4:
                        end_with = '\n'
                        counter = -1
                    print(f'{str(k).rjust(right_j)} : {v}', end=end_with)
                    counter += 1

            if header == 'PIN + Passcode':
                answer = getpass.getpass(prompt=ask)
            else:
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

            if header == 'Instance':
                # instance id chosen from menu should be assigned to args.instance
                args.instance = choice_tmp

        except (ValueError, KeyError) as err:
            print('\n!!! Invalid selection...\n')
        else:
            print()
            return choice


if __name__ == '__main__':
    prog_desc = 'purpose: transfer file to or from a host that is behind a UNIX gateway. unless specified (as BINARY), file will be treated as ASCII.'
    choice_text = '\n\nYour choice: '
    action = {1 : 'download', 2 : 'upload'}
    
    parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
    parser.add_argument('file', help='file to be transferred')
    parser.add_argument('-b', '--binary', help='if not specified, file will be treated as ASCII', action='store_true')
    parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
    parser.add_argument('-u', '--username', help='Gateway username')
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
    # parse the csv (MS_client_accounts.csv) for client's environment information
    filename = 'MS_client_accounts.csv'
    file = Path(filename)
    if not file.exists():
        logging.info(f'{filename} does not exist!')
        logging.info('Terminating program...')
        sys.exit()
    
    csv_file = open(filename, newline='')
    reader = csv.reader(csv_file)

    # sample dictionary for storing client environment information
    # key = instance ID; value = a tuple of these values in order [hostname, FTP password, 5-char client ID]
    # {'buaour1' : ('lit-vams-b102.gxsonline.net', '7Ey4s|Ms', 'UAOUR'), 'bcarmx1' : ('lit-vams-b102.gxsonline.net', '59K>oSgs', 'CARMX')}

    # parse the csv's header
    header_list = next(reader)

    # need separate dictionaries: 1) the menu in the user prompt (if --instance not passed as an argument);
    #                             2) the main dictionary
    instance_menu = {}
    client_accounts = {}
    counter = 1
    temp_list = []  # need to put all instances in a list first, then sort later on so they'll be in alphabetical order when shown in the menu


    # create the main dictionary of client instances; also a temp list for all instances
    for row in reader:
        temp_list.append(row[0].lower())
        client_accounts[row[0]] = tuple([row[1], row[2], row[3]])
        counter += 1
    
    # it's not expected that the values in MS_client_accounts.csv are sorted,
    # so sort the (temp) list of instances prior to creating the user prompt menu dictionary
    temp_list.sort()
    counter = 1

    # create the dictionary for the user prompt menu; key = counter; value = instance
    for item in temp_list:
        instance_menu[counter] = item
        counter += 1
    
    # =====================================================================================================================================
    # parse the csv (gateway_hosts.csv) for UNIX gateway information
    filename = 'gateway_hosts.csv'
    file = Path(filename)
    if not file.exists():
        logging.info(f'{filename} does not exist!')
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

    if args.gateway and args.username and args.instance and args.action:
        logging.info('All required arguments passed')
     
    # determine which parameters were not passed when calling the program
    
    if args.gateway:
        args.gateway = args.gateway.lower()
    
    # if gateway passed is recognized
    if args.gateway in gateway_hosts.keys():
        args.gateway = gateway_hosts[args.gateway]
        logging.info(f'Gateway {args.gateway} recognized...')
    elif args.gateway not in gateway_hosts.values():
        # if gateway argument passed is not recognized, then prompt user for choice
        if args.gateway:
            logging.info(f'Unrecognized gateway: {args.gateway}')
        args.gateway = prompt(header='Gateway', ask=choice_text, main_dict=gateway_hosts, menu_dict=gateways_menu)

    # if no --username argument passed
    if not args.username:
        args.username = prompt(header='Username', ask='Enter username: ', response_type='str')

    if not args.instance:
        # if no --instance argument passed, obtain the FTPhost, FTPpwd and clientID from prompt function
        # it is also in prompt function that the args.instance will be updated with the user choice from the menu
        FTPhost, FTPpwd, clientID = prompt(header='Instance', ask=choice_text, main_dict=client_accounts, menu_dict=instance_menu)
    else:
        # if --instance argument passed, then look up for the values in the client_accounts dictionary
        FTPhost, FTPpwd, clientID = client_accounts[args.instance]

    # if no --action argument passed
    if not args.action:
        args.action = prompt(header='What do you want to do', ask=choice_text, main_dict=action)

    # prompt user for PIN + Passcode
    passcode = prompt(header='PIN + Passcode', ask='Enter PIN + Passcode: ', response_type='str')
    
    
    print(line)
    logging.info(f'Connecting to {args.gateway}...')

    with ftplib.FTP(host=args.gateway) as ftp:
        file_orig = args.file

        try:
            logging.info(f'Connected. Waiting for welcome message...')
            print(ftp.getwelcome())
            ftp.login(user=args.username, passwd=passcode)
            logging.info(f'User {args.username} logged in to {args.gateway}')
            
            ftp.sendcmd(f'USER {args.instance}@{FTPhost}')
            ftp.sendcmd(f'PASS {FTPpwd}')
            logging.info(f'Logged in to {FTPhost}')

            # by default, will use the aiprod{clientID}/implementor/{args.username} directory name
            logging.info(f'By default, will transfer files to/from aiprod<clientID>/implementor/<username> directory')

            ftp.cwd(f'aiprod{clientID}/implementor/{args.username}')
            logging.info(f'Changed directory to: aiprod{clientID}/implementor/{args.username}')            

            if args.binary:
                mode = 'Binary'
                ftp.sendcmd('TYPE I')
            else:
                mode = 'ASCII'
                ftp.sendcmd('TYPE A')
            logging.info(f'Switching to {mode} mode.')
            # ftp.retrlines('LIST')
            
            logging.info(f'Starting {args.action} of {file_orig}')

            with open(file_orig, 'w') as new_file:
                # result = ftp.retrbinary(f'RETR {file_orig}', new_file.write)
                ftp.retrlines(f'RETR {file_orig}', new_file.write)
                logging.info('File downloaded')
        except ftplib.all_errors as e:
            logging.info(f'FTP error: {e}')

            if args.action == 'download':
                # in case of failure, delete the local file
                logging.info('Download failed. Deleting local copy...')
                f = Path(file_orig)
                if f.exists():
                    f.unlink()

        else:
            ftp.close()
            logging.info('Goodbye')

    logging.info('End of program')
