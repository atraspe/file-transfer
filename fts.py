import sys
from pathlib import Path

import argparse, logging, math, getpass

# CSV
import csv

# FTP
import ftplib

line = '=' * 72

def ask_user(prompt, header=None, ask_again=None, response_type='int', main_dict=None, menu_dict=None, echo=True):
    # function to ask user for an argument that was not passed when calling the program
    #
    # can accept 2 dictionaries:
    #   i) dictionary used for displaying menu for the user to choose from
    #   ii) main dictionary from the gateway_hosts.csv or MS_client_accounts.csv

    while True:
        try:
            if header:
                print(f'{line}\n{header}\n{len(header) * "-"}\n')
            
            if main_dict or menu_dict:
                d = menu_dict if menu_dict else main_dict
                # determine the length of the dictionary for right justification in the user menu
                right_j = int(math.log10(len(d))) + 1   
                counter = 0

                for k,v in d.items():
                    end_with = '\n' if counter == 4 else '\t'
                    
                    if counter == 4:
                        # end_with = '\n'
                        counter = -1
                    
                    print(f'{str(k).rjust(right_j)} : {v}', end=end_with)
                    counter += 1

            if not echo:
                answer = getpass.getpass(prompt=prompt)
            else:
                # print()
                answer = input(f'{prompt}')
            
            # if ask_user is expecting an answer that is an integer or string
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

            if header == 'Managed Service Instance':
                # instance id chosen from menu should be assigned to args.instance
                args.instance = choice_tmp

        except (ValueError, KeyError) as err:
            print('\n!!! Invalid selection...\n')
        else:
            print()
            return choice

def parse_csv(filename, order=False):
    # function to store information from the csv file into a dictionary
    # will return a tuple of 2 dictionaries

    file = Path(filename)
    if not file.exists():
        logging.info(f'{filename} does not exist!')
        logging.info('Terminating script...')
        sys.exit()
    
    csv_file = open(filename, newline='')
    reader = csv.reader(csv_file)

    # parse the csv's header
    header_list = next(reader)

    # need separate dictionaries for 1) the menu in the user prompt, 2) the main dictionary
    menu_dict = {}
    main_dict = {}
    
    counter = 1
    temp_list = []  # if order is True, put all instances in a list, then sort later so they'll be in alphabetical order when shown in the menu

    for row in reader:
        val = row[0].lower()

        if order:
            # sample dictionary for storing client environment information
            # key = instance ID; value = a tuple of these values in order [hostname, FTP password, 5-char client ID]
            # {'buaour1' : ('lit-vams-b102.gxsonline.net', '7Ey4s|Ms', 'UAOUR'), 'bcarmx1' : ('lit-vams-b102.gxsonline.net', '59K>oSgs', 'CARMX')}
            temp_list.append(val)
            main_dict[row[0]] = tuple([row[1], row[2], row[3]])
        else:
            menu_dict[counter] = val
            main_dict[val] = row[1]
        
        counter += 1

    if order:
        # it's not expected that the values in MS_client_accounts.csv are sorted,
        # so sort the (temp) list of instances prior to creating the user prompt menu dictionary
        temp_list.sort()
        counter = 1
        for item in temp_list:
            menu_dict[counter] = item
            counter += 1

    # return both dictionaries as tuple
    return (main_dict, menu_dict)


if __name__ == '__main__':
    prog_desc = 'purpose: transfer file to/from a host that is behind a UNIX gateway. file will be transferred in Binary mode.'
    choice_text = '\n\nYour choice: '
    username_text = 'Enter username: '
    action = {1 : 'download', 2 : 'upload'}
    
    
    parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
    parser.add_argument('file', help='file to be transferred')
    parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
    parser.add_argument('-u', '--username', help='Gateway username')
    parser.add_argument('-p', '--passcode', help='IDLDAP.net password')
    parser.add_argument('-m', '--ms', help='transfer to Managed Services hosts', action='store_true')
    parser.add_argument('-i', '--instance', help='Managed Services client instance')
    parser.add_argument('-a', '--action', help='download or upload')
    parser.add_argument('-v', '--verbose', help='explain what is being done', action='store_const', const=logging.INFO, dest='loglevel')
    parser.add_argument('-h', '--help', help='show this help message and exit', action='help')

    args = parser.parse_args()

    # Logging; does not include the levelname(severity) in the messages, only the date/time stamp and message
    logging.basicConfig(level=args.loglevel, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')

    print(line)
    logging.info(f'Executing {__file__}...')
    logging.info('Loading configuration...')

    # =====================================================================================================================================
    # parse the csv file for UNIX gateway information
    gateway_hosts, gateways_menu = parse_csv('gateway_hosts.real.csv')
    
    # =====================================================================================================================================
    # parse the csv file for host options
    hosts_options, hosts_menu = parse_csv('servers.real.csv')

    # =====================================================================================================================================
    # parse the csv for MS clients' environment information
    client_accounts, instance_menu = parse_csv('MS_client_accounts.real.csv', order=True)

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
        # if gateway argument passed is not recognized, then ask user for choice
        if args.gateway:
            logging.info(f'Unrecognized gateway: {args.gateway}')
        args.gateway = ask_user(prompt=choice_text, header='Gateway', main_dict=gateway_hosts, menu_dict=gateways_menu)

    # if no --username argument passed
    if not args.username:
        args.username = ask_user(prompt=username_text, header='Gateway Username', response_type='str')

    # ask_user user for PIN + Passcode
    if not args.passcode:
        args.passcode = ask_user(prompt='Enter IDLDAP.net Password: ', header='IDLDAP.net Password', response_type='str', echo=False)

    # if --ms was not invoked in the argument, ask if user wants to transfer files to/from MS or non-MS host
    if not args.ms:
        FTPhost = ask_user(prompt='\nHost you want to transfer files to/from: ', header='Connect to', main_dict=hosts_options, menu_dict=hosts_menu)
        # update args.ms if user wants to connect to MS host; in preparation for next
        if FTPhost == 'Managed Services':
            args.ms = True


    if args.ms:
        # if user wants to transfer a file to/from a MS host (either --ms was invoked or was set to True from last condition)
        # but without --instance argument passed, ask user for MS instance
        if not args.instance:
            # obtain the FTPhost, FTPpwd and clientID from ask_user function
            # it is also in ask_user function that the args.instance will be updated with the user choice from the menu
            FTPhost, FTPpwd, clientID = ask_user(prompt=choice_text, header='Managed Service Instance', main_dict=client_accounts, menu_dict=instance_menu)
        else:
            # if --ms and --instance argument passed, then look up for the values in the client_accounts dictionary
            FTPhost, FTPpwd, clientID = client_accounts[args.instance]
    else:
        # if user wants to transfer a file to/from a non-MS host, ask for more details
        args.instance = ask_user(prompt=username_text, header=f'Credentials for {FTPhost}', response_type='str')
        FTPpwd = ask_user(prompt='Enter password: ', response_type='str', echo=False)
        FTPdir = ask_user(prompt='Enter directory (absolute path) on remote host: ', response_type='str')

    # update FTPUser
    FTPUser = args.instance

    print(f'ftp host: {FTPhost}')
    print(f'ftp user: {FTPUser}')
    print(f'ftp pwd: {FTPpwd}')

    # ask if user wants to download or upload file
    if not args.action:
        args.action = ask_user(prompt=choice_text, header='You want to', main_dict=action)
    
    
    print(line)
    logging.info(f'Connecting to {args.gateway}...')

    try:
        with ftplib.FTP(host=args.gateway) as ftp:
            file_orig = args.file

            try:
                logging.info(f'Connection established, waiting for welcome message...')
                print(ftp.getwelcome())
                logging.info('When prompted, please approve the sign-in request in your "VIP Access" mobile/desktop app...')
                ftp.login(user=args.username, passwd=args.passcode)
                logging.info(f'User {args.username} logged in to {args.gateway}')
                
                ftp.sendcmd(f'USER {FTPUser}@{FTPhost}')
                ftp.sendcmd(f'PASS {FTPpwd}')
                logging.info(f'Logged in to {FTPhost}')

                # by default, will use the aiprod{clientID}/implementor/{args.username} directory name
                logging.info(f'By default, will transfer files to/from aiprod<clientID>/implementor/<username> directory')
                logging.info('If uploading, directory will be created if non-existent')

                ftp.cwd(f'aiprod{clientID}/implementor/{args.username}')
                logging.info(f'Changed directory to: aiprod{clientID}/implementor/{args.username}')            

                logging.info('Switching to Binary mode.')
                ftp.sendcmd('TYPE I')
                logging.info(f'Starting {args.action} of {file_orig}')
                
                if args.action == 'download':
                    # downloading
                    with open(file_orig, 'wb') as new_file:
                        ftp.retrbinary(f'RETR {file_orig}', new_file.write)
                else:
                    # uploading
                    with open(file_orig, 'rb') as new_file:
                        ftp.storbinary(f'STOR {file_orig}', new_file)
                
                logging.info(f'File transfer successful, transferred {ftp.size(file_orig)} bytes')
            
            except ftplib.all_errors as e:
                logging.info(f'FTP error: {e}')

                if args.action == 'download':
                    local_file = Path(file_orig)
                    if local_file.exists():
                        # in case of failure, delete the local file
                        logging.info('Download failed. Deleting local copy...')
                        local_file.unlink()

            else:
                logging.info('No error encountered')
                ftp.close()
                logging.info('Connection closed')

    except ftplib.all_errors as e:
        logging.info('Error connecting to gateway...')
        logging.info(e)
        logging.info('Check that you\'re connected to the company\'s VPN')
        
    
    logging.info('Disconnected from server')
    logging.info('End of script, thank you!')
    print(line)
