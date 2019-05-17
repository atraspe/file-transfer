"""
fts.py
------
Script to transfer file(s) to or from a host that is behind a UNIX gateway.

File transfer to a host that is behind a UNIX gateway requires
authentication with the gateway prior to accessing the host itself.
Arguments can be passed directly when calling the script - supports both
the short and long version: e.g. --h or --help). If not, user will be 
prompted for the required information (e.g. username, server to connect to,
file(s) to be transferred, etc.). The script uses 3 different CSV files
which has information about the gateway hosts, group of servers to access,
and client information (client instance, hostname, FTP password, client ID).
"""

import sys
import argparse
import logging
import math
import getpass
import csv
import ftplib
from pathlib import Path
from datetime import datetime

# some global variables
equal_sign_line = '=' * 72
dash_line = '-' * 47


def ask_user(prompt, header=None, response_type='int', main_dict=None, menu_dict=None, echo=True):
    """
    Function to ask user for information that wasn't passed as argument when calling the program.

    Parameters:
    prompt (str): The user will be prompted by this question
    header (bool): Determine whether header will be displayed; True for a 1-question prompt,
                    False for succeeding questions of a multi-question prompt
    response_type (str): Unless specified as 'str', response is expected to be an integer value
    main_dict (dict): Main dictionary to validate user input
    menu_dict (dict): Dictionary for values to be displayed in the user menu.
                        User choice will then be looked up against main dictionary
    echo (bool): Determine if user input will be displayed; True by default, False for password prompts

    Returns:
    str: The value from main dictionary
    """

    while True:
        try:
            # try until user inputs a valid selection from menu

            if header:
                print(f'{equal_sign_line}\n{header}\n{len(header) * "-"}\n')

            if main_dict or menu_dict:
                d = menu_dict if menu_dict else main_dict
                # determine the length of the dictionary for right justification in the user menu
                right_j = int(math.log10(len(d))) + 1
                counter = 0

                # diplay the user menu
                for key, value in d.items():
                    end_with = '\n' if counter == 4 else '\t'

                    if counter == 4:
                        # end_with = '\n'
                        counter = -1

                    print(f'{str(key).rjust(right_j)} : {value}', end=end_with)
                    counter += 1

            if not echo:
                # for passwords, do not echo user input
                answer = getpass.getpass(prompt=prompt)
            else:
                answer = input(f'{prompt}')

            # depends on response_type parameter if expecting
            # an answer that is an integer or string
            if response_type == 'str':
                answer = str(answer)
            else:
                answer = int(answer)

            # if no dictionary is passed (e.g. Username),
            # just return that user input
            choice = answer

            if menu_dict:
                # user input will be validated against eh menu dictionary first
                choice_tmp = menu_dict[answer]
                answer = choice_tmp
            if main_dict or menu_dict:
                # value will then be validated against main dictionary
                choice = main_dict[answer]

            if header == 'Managed Service Instance':
                # instance id chosen from menu should be assigned to args.instance
                args.instance = choice_tmp

        except (ValueError, KeyError) as err:
            print('\n!!! Invalid selection...\n')

        else:
            print()
            return choice


def parse_csv(filename, sort=False):
    """
    Function to parse a CSV file and store its information into a dictionary

    Parameters:
    filename (str): CSV filename to be parsed
    sort (bool): If values need to be sorted prior to storing into menu dictionary

    Returns:
    tuple: A tuple of 2 dictionaries: main and menu
    """

    file = Path(filename)
    if not file.exists():
        print(
            f'{date_time_stamp} - One of the configuration files ({filename}) does not exist!')
        print(f'{date_time_stamp} - Terminating script...')
        sys.exit()

    csv_file = open(filename, newline='')
    reader = csv.reader(csv_file)

    # parse the csv's header
    header_list = next(reader)

    # need separate dictionaries for 1) the menu in the user prompt, 2) the main dictionary
    menu_dict = {}
    main_dict = {}

    counter = 1

    # if sort is True, temporarily put all instances in a list,
    # then sort later so menu will be in alphabetical order
    temp_list = []

    for row in reader:
        val = row[0].lower()

        if sort:
            # sample dictionary for storing client environment information
            # key = instance ID
            # value = a tuple of these values in order [hostname, FTP password, 5-char client ID]
            # {
            #  'instance1' : ('nipon01.internal.net', 'abc123', 'XRADI'),
            #  'instance2' : ('hague01.internal.net', '59K>oSgs', 'MSXYZ')
            # }
            temp_list.append(val)
            main_dict[row[0]] = tuple([row[1], row[2], row[3]])
        else:
            menu_dict[counter] = val
            main_dict[val] = row[1]

        counter += 1

    if sort:
        # it's not expected that the values in MS_client_accounts.csv are sorted,
        # so sort the (temp) list of instances prior to creating the user prompt menu dictionary
        temp_list.sort()
        counter = 1
        for item in temp_list:
            menu_dict[counter] = item
            counter += 1

    # return both dictionaries as tuple
    return (main_dict, menu_dict)


# main program
if __name__ == '__main__':
    prog_desc = 'purpose: transfer file to/from a host that is behind a UNIX gateway. file will be transferred in Binary mode.'
    choice_text = '\n\nYour choice: '
    username_text = 'Enter username: '
    action = {1: 'download', 2: 'upload'}

    # if --verbose not invoked, then format date/time stamp similar to that of the verbose log
    date_time_stamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    parser = argparse.ArgumentParser(description=prog_desc, add_help=False)
    parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
    parser.add_argument('-u', '--username', help='Gateway username')
    parser.add_argument('-p', '--passcode', help='IDLDAP.net password')
    parser.add_argument('-m', '--managedservices',
                        help='transfer to Managed Services hosts', action='store_true')
    parser.add_argument('-i', '--instance',
                        help='Managed Services client instance')
    parser.add_argument('-a', '--action', help='download or upload')
    parser.add_argument('-f', '--file', nargs='*',
                        help='file(s) to be transferred')
    parser.add_argument('-v', '--verbose', help='explain what is being done',
                        action='store_const', const=logging.INFO, dest='loglevel')
    parser.add_argument(
        '-h', '--help', help='show this help message and exit', action='help')

    args = parser.parse_args()

    # Logging; does not include the levelname(severity) in the messages,
    # only the date/time stamp and message
    logging.basicConfig(
        level=args.loglevel, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')

    print(equal_sign_line)
    logging.info(f'Executing {__file__}...')
    print(f'{date_time_stamp} - Loading configuration...')

    # =========================================================================
    # parse the csv file for UNIX gateway information
    gateway_csv = 'gateway_hosts.real.csv'
    gateway_hosts, gateways_menu = parse_csv(gateway_csv)

    # =========================================================================
    # parse the csv file for host options
    servers_csv = 'servers.real.csv'
    hosts_options, hosts_menu = parse_csv(servers_csv)

    # =========================================================================
    # parse the csv for MS clients' environment information
    ms_client_csv = 'MS_client_accounts.real.csv'
    client_accounts, instance_menu = parse_csv(ms_client_csv, sort=True)

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
            print(f'{date_time_stamp} - Unrecognized gateway: {args.gateway}')

        args.gateway = ask_user(prompt=choice_text, header='Gateway',
                                main_dict=gateway_hosts, menu_dict=gateways_menu)

    # if no --username argument passed
    if not args.username:
        args.username = ask_user(
            prompt=username_text, header='Gateway Username', response_type='str')

    # ask_user user for PIN + Passcode
    if not args.passcode:
        args.passcode = ask_user(prompt='Enter IDLDAP.net Password: ',
                                 header='IDLDAP.net Password', response_type='str', echo=False)

    # if --ms was not invoked in the argument, ask if user wants to transfer files to/from a MS or non-MS host
    if not args.managedservices:
        FTPhost = ask_user(prompt='\n\nHost you want to transfer files to/from: ',
                           header='Connect to', main_dict=hosts_options, menu_dict=hosts_menu)
        # update args.managedservices if 'Managed Services' was chosen ; then ask for more information if needed
        if FTPhost == 'Managed Services':
            args.managedservices = True

    if args.managedservices:
        # if user wants to transfer a file to/from a MS host (either --ms was invoked or was set to True from last condition)
        # but without --instance argument passed, ask user for MS instance
        if not args.instance:
            # obtain the FTPhost, FTPpwd and clientID from ask_user function
            # it is also in ask_user function that the args.instance will be updated with the user choice from the menu
            FTPhost, FTPpwd, clientID = ask_user(
                prompt=choice_text, header='Managed Service Instance', main_dict=client_accounts, menu_dict=instance_menu)
        else:
            # if --ms and --instance argument passed, then look up for the values in the client_accounts dictionary
            try:
                FTPhost, FTPpwd, clientID = client_accounts[args.instance]
            except KeyError:
                print(
                    f'{date_time_stamp} - The MS instance {args.instance} passed as argument is unrecognized.')
                print(
                    f'{date_time_stamp} - Check MS_client_accounts.csv. If not there, please add client account info.')
                print(f'{date_time_stamp} - Exiting script...')
                print(equal_sign_line)
                sys.exit()

        # for MS hosts, set FTPdir to default directory
        FTPdir = f'aiprod{clientID}/implementor/{args.username}'

    else:
        # if user wants to transfer a file to/from a non-MS host, ask for more details
        args.instance = ask_user(
            prompt=username_text, header=f'Credentials for {FTPhost}', response_type='str')
        FTPpwd = ask_user(prompt='Enter password: ',
                          response_type='str', echo=False)
        FTPdir = ask_user(
            prompt='Enter directory (absolute path) on remote host: ', response_type='str')

    # update FTPUser
    FTPUser = args.instance

    # ask if user wants to download or upload file
    if args.action not in ['download', 'upload']:
        print(f'{date_time_stamp} - You passed an action argument that is not valid: {args.action}')
        args.action = None
    if not args.action:
        args.action = ask_user(
            prompt=choice_text, header='You want to', main_dict=action)


    # if not specified in the argument, ask user for file(s) to transfer
    if not args.file:
        temp_file = ask_user(
            prompt=f'Please specify filename(s) separated by a space: ', header=f'Files to {args.action}', response_type='str'
        )
        args.file = temp_file.split(' ')


    print(equal_sign_line)

    # initialize some flags prior to establishing connection to UNIX gateway
    logged_gateway = False

    # logged_host initially is True. will be used later in the exception
    # to display the host login error messages
    logged_host = True

    changed_dir = False

    downloaded = True
    uploaded = True

    print(f'{date_time_stamp} - Connecting to {args.gateway}...')

    with ftplib.FTP(host=args.gateway) as ftp:
        logging.info(f'Connection established, waiting for welcome message...')
        welcome = ftp.getwelcome()
        if welcome:
            logging.info(f'A message from the server\n{ftp.getwelcome()}')
        print(
            f'{date_time_stamp} - When prompted, please approve the sign-in request in your "VIP Access" mobile/desktop app...')

        try:
            # login to the chosen UNIX gateway
            ftp.login(user=args.username, passwd=args.passcode)
            print(
                f'{date_time_stamp} - User {args.username} logged in to UNIX gateway: {args.gateway}')
            logged_gateway = True

            # login to the chosen host (MS or non-MS)
            host = f'MS host' if args.managedservices else f'non-MS host'
            logging.info(f'Logging in to the {host}...')
            ftp.sendcmd(f'USER {FTPUser}@{FTPhost}')
            ftp.sendcmd(f'PASS {FTPpwd}')
            print(f'{date_time_stamp} - Logged in to {host}: {FTPUser}@{FTPhost}')
            logged_host = True

            if args.managedservices:
                # on MS hosts, by default, use the aiprod{clientID}/implementor/{args.username} directory
                logging.info(
                    f'By default, transferring files to/from aiprod<clientID>/implementor/<username> directory')

            logging.info(f'Currently in {ftp.pwd()}')
            print(f'{date_time_stamp} - Changing directory to: {FTPdir}')
            ftp.cwd(FTPdir)
            changed_dir = True

            logging.info('Switching to Binary mode.')
            ftp.sendcmd('TYPE I')

            for next_file in args.file:
                downloaded = False
                uploaded = False
                print(f'{date_time_stamp} - {dash_line}')
                print(f'{date_time_stamp} - Starting {args.action} of {next_file}')

                if args.action == 'download':
                    # downloading
                    with open(next_file, 'wb') as new_file:
                        ftp.retrbinary(f'RETR {next_file}', new_file.write)
                        downloaded = True
                else:
                    # uploading
                    with open(next_file, 'rb') as new_file:
                        ftp.storbinary(f'STOR {next_file}', new_file)
                        uploaded = True

                if downloaded or uploaded:
                    print(
                        f'{date_time_stamp} - File transfer successful, transferred {ftp.size(next_file)} bytes')

            print(f'{date_time_stamp} - {dash_line}')

        except ftplib.all_errors:
            if not logged_gateway:
                print(
                    f'{date_time_stamp} - Error connecting to the UNIX gateway {args.gateway}')
                print(
                    f'{date_time_stamp} - Please double check your IDLDAP.net credentials (username and/or password)...')
                print(
                    f'{date_time_stamp} - Also, check that you\'re connected to the company\'s VPN')

            if not logged_host:
                print(
                    f'{date_time_stamp} - Host login incorrect! {FTPUser}@{FTPhost} ')
                print(
                    f'{date_time_stamp} - Please double check your credentials (username and/or password) in {ms_client_csv}...')

            if not changed_dir:
                print('{date_time_stamp} - Changing directory error...')
                print(
                    f'{date_time_stamp} - Please check if {FTPdir} exists in the MS host...')

            if args.action == 'download' and not downloaded:
                # in case of download failure, delete the local file
                local_file = Path(next_file)
                if local_file.exists():
                    print(
                        f'{date_time_stamp} - Download failed. Deleting local copy...')
                    local_file.unlink()
                    print(f'{date_time_stamp} - {dash_line}')

        finally:
            # clean-up actions
            ftp.close()
            logging.info('FTP connection closed')
            logging.info('Disconnected from server')
            print(f'{date_time_stamp} - End of program')
            print(f'{date_time_stamp} - Thank you for using the script!')
            print(equal_sign_line)
