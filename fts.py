"""
fts.py
------
Script to transfer file(s) to or from a host that is behind a UNIX gateway.

File transfer to a host that is behind a UNIX gateway requires
authentication with the gateway prior to accessing the host itself.
Arguments can be passed directly when calling the script - supports both
the short and long version: e.g. --h or --help). If not, user will be
prompted for the required information (e.g. Unix gate to use, gate username,
remote host, file(s) to be transferred, etc.). The script uses different CSV files
which has information about the gateway hosts, group of servers to access,
non-MS hosts, andMS client information (client instance, hostname, 
FTP password, client ID).
"""

import json
import argparse
import logging
import logging.config
import math
import getpass
import csv
import ftplib
import contextlib
import sys
from pprint import pprint
from pathlib import Path
from datetime import datetime

# global variables and constants
VERSION_NO = '1.0'
equal_sign_line = '=' * 72
dash_line = '-' * 47

curr_dir = Path()
LOG_DIR = curr_dir / 'logs'
CONFIG_DIR = curr_dir / 'config'
JSON_CONFIG = 'fts.json'

# FileHandler (asctime) will include the date and time stamps
FORMATTER = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
LOG_FILE = LOG_DIR / 'fts.log'


class Error(Exception):
    """Base class for exceptions"""
    pass


class EmptyInputError(Error):
    """Exception raised if user just pressed enter when prompted to input something"""
    pass


class GatewayConnectionError(Error):
    """

    Attributes:
    logger (logging.Logger object) - Object that handles the FileHandler and StreamHandler
    gate (str): Unix gate
    location (str): Unix gate location
    """

    def __init__(self, logger, gate, location):
        self.logger = logger
        self.logger.info(dash_line)
        self.logger.error(
            f'Error connecting to the {location.title()} Gate ({gate})')
        self.logger.warning('Possible causes:')
        self.logger.warning(
            '1. Incorrect IDLDAP.net credentials (username and/or password)')
        self.logger.warning('2. You\'re out of the company\'s network')
        self.logger.warning('3. "VIP Access" sign-in request timed out')
        self.logger.info(dash_line)
        raise TerminateTheScript(self.logger)


class RemoteHostConnectionError(Error):
    """Exception raised if unable to login to remote host most likely due to incorrect credentials

    Attributes:
    logger (logging.Logger object) - Object that handles the FileHandler and StreamHandler
    remote_user (str): Remote host username
    remote_host (str): Remote host
    """

    def __init__(self, logger, remote_user, remote_host):
        self.logger = logger
        self.remote_user = remote_user
        self.remote_host = remote_host

        self.logger.error(
            f'Host login incorrect! {self.remote_user}@{self.remote_host}')
        self.logger.warning(
            f'Please double check your credentials (username and/or password)...')
        raise TerminateTheScript(self.logger)


class WeGotOurselvesAQuitter(Error):
    """Exception raised if user wants to quit the script prematurely

    Attribute:
    logger(logging.Logger object) - Object that handles the FileHandler and StreamHandler
    """

    def __init__(self, logger):
        self.logger = logger

        print()
        self.logger.info(dash_line)
        self.logger.warning(
            'Ladies and gentlemen, we got ourselves a quitter!!!')
        self.logger.warning(
            'Quitter!! quitter! quitter... *fades in the background*')
        raise TerminateTheScript(self.logger)


class ConfigDoesNotExistError(Error):
    """Exception raised if one of the configuration directories and/or files does not exist

    Attributes:
    logger (logging.Logger object) - Object that handles the FileHandler and StreamHandler
    config (str) - Missing configuration (directory or file)
    """

    def __init__(self, logger, config):
        self.config = config
        self.logger = logger

        self.logger.error(f'{self.config} does not exist!')
        raise TerminateTheScript(self.logger)


class UploadFileDoesNotExistError(Error):
    """Exception raised if the file to be uploaded does not exist

    Attributes:
    logger(logging.Logger object) - Object that handles the FileHandler and StreamHandler
    file(Path object)
    """

    def __init__(self, logger, file, curr_dir):
        self.file = file
        self.curr_dir = curr_dir
        self.logger = logger

        self.logger.error(f'{self.file} does not exist in {self.curr_dir}')
        self.logger.info(dash_line)
        raise TerminateTheScript(self.logger)


class TerminateTheScript(Error):
    """Exception raised from the other custom exceptions to prematurely end the script

    Attribute:
    logger(logging.Logger object) - object that handles the FileHandler and StreamHandler"""

    def __init__(self, logger):
        self.logger = logger

        self.logger.warning('Terminating script...')
        self.logger.info('End of program')
        self.logger.info(f'Logged everything in {LOG_FILE}')
        self.logger.info('Thank you for using the script!')
        self.logger.info(f'SCRIPT LOG - End')
        self.logger.info(equal_sign_line)
        sys.exit()


class FtpConnection():

    def __init__(self, gateway, gate_location, gate_user, gate_pwd, server_grp, ms_instance, action, files, remote_host, remote_user, remote_pwd, remote_dir, logger):
        self.gateway = gateway
        self.gate_location = gate_location
        self.gate_user = gate_user
        self.gate_pwd = gate_pwd
        self.server_grp = server_grp
        self.ms_instance = ms_instance
        self.action = action
        self.files = files
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_pwd = remote_pwd
        # self.clientID = clientID
        self.remote_dir = remote_dir
        self.logger = logger
        self.host = f'MS host' if self.server_grp == 'ms' else f'non-MS host'

    def connect_and_transfer(self):
        self.logger.info(
            f'Connecting to the {self.gate_location.title()} Gate ({self.gateway})...')

        try:
            with ftplib.FTP(host=self.gateway) as ftp:
                self.logger.info(f'Connection established!')
                welcome = ftp.getwelcome()

                if welcome:
                    self.logger.info(
                        f'A message from the server:\n{welcome}')

                self.logger.info(
                    'When prompted, please approve the sign-in request in your "VIP Access" mobile/desktop app...')

                # update Class attribute with the ftp object
                self.ftp = ftp
                # login to unix gate
                self._login_to_gate()

        except ftplib.all_errors as e:
            raise GatewayConnectionError(
                self.logger, self.gateway, self.gate_location)

    def _login_to_gate(self):

        try:
            self.ftp.login(user=self.gate_user, passwd=self.gate_pwd)
            self.logger.info(f'User {self.gate_user} logged in')
            self._login_to_remote_host()

        except ftplib.all_errors:
            raise GatewayConnectionError(
                self.logger, self.gateway, self.gate_location)

    def _login_to_remote_host(self):
        # login to the chosen host (MS or non-MS)
        try:
            self.logger.info(f'Logging in to the {self.host}...')
            self.ftp.sendcmd(f'USER {self.remote_user}@{self.remote_host}')
            self.ftp.sendcmd(f'PASS {self.remote_pwd}')
            self.logger.info(
                f'Logged in: {self.remote_user}@{self.remote_host}')
            self._transfer_files()
            self.ftp.close()
            self.logger.info('FTP connection closed')
            self.logger.info('Disconnected from server')

        except ftplib.all_errors:
            raise RemoteHostConnectionError(
                self.logger, self.remote_user, self.remote_host)

    def _transfer_files(self):
        if self.server_grp == 'ms':
            self.logger.info(
                f'By default, transferring files to/from {self.remote_dir}')

        try:
            self.logger.info(f'Currently in {self.ftp.pwd()}')
            self.logger.info(f'Changing directory to: {self.remote_dir}')
            changed_dir = False
            self.ftp.cwd(self.remote_dir)
            changed_dir = True

            self.logger.info('Switching to Binary mode.')
            self.ftp.sendcmd('TYPE I')

            for next_file in self.files:
                downloaded = False
                uploaded = False
                self.logger.info(dash_line)
                self.logger.info(f'Starting {self.action} of {next_file}...')

                if self.action == 'download':
                    with open(next_file, 'wb') as new_file:
                        self.ftp.retrbinary(
                            f'RETR {next_file}', new_file.write)
                        downloaded = True
                else:
                    with open(next_file, 'rb') as new_file:
                        self.ftp.storbinary(f'STOR {next_file}', new_file)
                        uploaded = True

                if downloaded or uploaded:
                    self.logger.info(
                        f'File transfer successful, transferred {self.ftp.size(next_file)} bytes')
            self.logger.info(dash_line)

        except ftplib.all_errors:
            if not changed_dir:
                self.logger.error(
                    f'{self.remote_dir} does not exist in the remote host!')

            if self.action == 'download' and not downloaded:
                self.logger.error(
                    f'{next_file} does not exist in {self.remote_dir} !')
                # in case of download failure, delete the local file
                local_file = Path(next_file)
                if local_file.exists():
                    self.logger.info('Download failed. Deleting local copy...')
                    local_file.unlink()
            

            self.logger.info(dash_line)
            self.ftp.close()
            self.logger.info('FTP connection closed')
            self.logger.info('Disconnected from server')
            raise TerminateTheScript(self.logger)


def set_console_handler(level):
    """Function to set the StreamHandler
    
    Argument:
    level() - 
    """
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(level)
    return console_handler


def set_file_handler():
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(name, level=logging.DEBUG):
    global logger

    # create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # add handlers to the logger object
    logger.addHandler(set_console_handler(level))
    logger.addHandler(set_file_handler())

    logger.propagate = False

    return logger


def load_json_config(logger, file):
    """
    Function that retrieves values from the JSON configuration file

    Arguments:
    logger(logging.Logger object) - object that handles the FileHandler and StreamHandler
    file(str) - JSON configuration file
    """
    logger.info(f'Loading configuration from the JSON file ({JSON_CONFIG})...')

    json_file = Path(file)
    if not json_file.exists():
        raise ConfigDoesNotExistError(logger, json_file)

    with open(json_file) as f:
        data = json.load(f)

    json_gate_user = data['fts_config']['gateway']['username']
    json_gate_pwd = data['fts_config']['gateway']['password']
    csv_dir = data['fts_config']['csv']['csv_dir']
    csv_files = data['fts_config']['csv']['csv_files']
    csv_list = [value for x in range(len(csv_files))
                for key, value in csv_files[x].items()]
    log_dir = data['fts_config']['log']['log_dir']

    return json_gate_user, json_gate_pwd, csv_dir, csv_list, log_dir


def args_passed(args_list):
    """Function to filter out the arguments passed using filter()
    
    Argument:
    args_list (list): List of arguments to be filtered"""
    
    return list(filter(lambda x: bool(x), args_list))


def check_config(logger, csv_files):
    """Function that checks for existence of required directories (LOG_DIR and CONFIG_DIR),
    CSV files and other configuration files
    
    Arguments:
    logger(logging.Logger object) - object that handles the FileHandler and StreamHandler
    csv_files (list) - List of CSV files under CONFIG_DIR
    """

    logger.info('Checking configurations...')

    if not LOG_DIR.exists():
        raise ConfigDoesNotExistError(logger, f'{LOG_DIR} directory')

    if not CONFIG_DIR.exists():
        raise ConfigDoesNotExistError(logger, f'{CONFIG_DIR} directory')

    for file in csv_files:
        csv_file = CONFIG_DIR / file
        if not csv_file.exists():
            raise ConfigDoesNotExistError(logger, csv_file)

    logger.info('Configurations validated...')


def ask_user(logger, prompt, header=None, response_type='int', main_dict=None, menu_dict=None, echo=True, quit=True, column=4):
    """
    Function to ask user for information that wasn't passed as argument when calling the program.

    Parameters:
    prompt (str): The user will be prompted by this question
    header (bool): Determine whether header will be displayed; True for a 1-question prompt,
                    False for succeeding questions of a multi-question prompt
    response_type (str): Default response is of integer type; can also be string and list (e.g. args.file)
    main_dict (dict): Main dictionary to validate user input
    menu_dict (dict): Dictionary for values to be displayed in the user menu.
                        User choice will then be looked up against main dictionary
    echo (bool): Determine if user input will be displayed; True by default, False for password prompts
    quit (bool): Determine if user prompt will have the [Q/q]uit option
    column (int): Number of columns when displaying options to choose from; default 4

    Returns:
    tuple: The key and value from main dictionary
    """

    menu_choice = None
    prompt = f'{prompt} ([Q/q] to quit): ' if quit else f'{prompt}: '

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
                    end_with = '\n' if counter == column else '\t'

                    if counter == column:
                        counter = -1

                    print(f'{str(key).rjust(right_j)} : {value}', end=end_with)
                    counter += 1

            if not echo:
                # for passwords, do not echo user input
                answer = getpass.getpass(prompt=prompt)
            else:
                answer = input(f'{prompt}')

            if not answer:
                raise EmptyInputError

            if quit and answer.lower() == 'q':
                raise WeGotOurselvesAQuitter(logger)

            # depends on response_type parameter if expecting
            # an answer that is an integer or string
            if response_type == 'str':
                answer = str(answer)
            elif response_type == 'list':
                answer_tmp = answer
                answer = list()
                answer = answer_tmp.split()
            else:
                answer = int(answer)

            # if no dictionary is passed (e.g. Username), or for the 'MS Client ID'
            # just return that user input
            if (not main_dict and not menu_dict) or header == 'MS Client ID':
                main_value = answer
                # return main_value, menu_choice

            if menu_dict:
                # user input will be validated against eh menu dictionary first
                menu_choice = menu_dict[answer]
                answer = menu_choice
            if (main_dict or menu_dict) and not header == 'MS Client ID':
                # value will then be validated against main dictionary
                main_value = main_dict[answer]

        except (ValueError, KeyError):
            print('\n!!! Invalid selection...\n')

        except EmptyInputError:
            print('\n!!! Can\'t be empty. Please enter a valid value...\n')

        else:
            print()
            return main_value, menu_choice


def parse_csv(filename, logger, sort=False,):
    """
    Function to parse a CSV file and store its information into a dictionary

    Parameters:
    filename (str): CSV filename to be parsed
    sort (bool): If values need to be sorted prior to storing into menu dictionary

    Returns:
    tuple: A tuple of 2 dictionaries: one holds the main values while the other for the user menu
    """

    # global config_dir
    csv_file = CONFIG_DIR / f'{filename}'
    csv_file = open(csv_file, newline='')

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
            # value = a tuple of these values in order (instance, hostname, FTP password, 5-char client ID)
            # {
            #  'instance1' : ('id1', 'nipon01.internal.net', 'abc123', 'XRADI'),
            #  'instance2' : ('id2', 'hague01.internal.net', '59K>oSgs', 'MSXYZ')
            # }
            temp_list.append(val)
            main_dict[row[0]] = tuple([row[0], row[1], row[2], row[3]])
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

    logger.info(f'{csv_file.name} successfully loaded...')
    # return both dictionaries as tuple
    return (main_dict, menu_dict)


def check_if_existing(logger, files):
    """Function which checks if file(s) to be uploaded exist locally
    
    Attributes:
    logger (logging.Logger object) - Object that handles the FileHandler and StreamHandler
    files (list): File(s) to be uploaded
    """

    current_dir = Path().absolute()
    try:
        for item in files:
            x = Path(item)
            if not x.exists():
                raise UploadFileDoesNotExistError(logger, x, current_dir)
    except UploadFileDoesNotExistError:
        pass


def validate_or_ask_arg(logger, **kwargs):
    arg = kwargs.get('arg', None)
    header = kwargs.get('header', None)
    prompt = kwargs.get('prompt', None)
    response = kwargs.get('response_type', 'int')
    main_dict = kwargs.get('main_dict', None)
    menu_dict = kwargs.get('menu_dict', None)
    valid_dict = kwargs.get('valid_dict', None)
    echo = kwargs.get('echo', True)
    quit = kwargs.get('quit', True)
    other_value = None
    input_str = 'accepted'
    valid_arg = False
    arg_temp = None

    if arg:
        if valid_dict:
            arg = arg.lower()
            if arg in valid_dict.keys():
                unix_gate = valid_dict[arg]
                other_value = arg
                valid_arg = True
            elif arg in valid_dict.values():
                for key, value in valid_dict.items():
                    if value == arg:
                        other_value = key
                valid_arg = True

            if valid_arg:
                logger.info(f'{header.title()} {input_str}')
                # no need to prompt user since argument passed is already valid
                return unix_gate, other_value
            else:
                logger.warning(
                    f'{header.title()} passed ({arg}) is invalid...')
                # Nullify arg's value so it will be caught by the next condition
                arg = None

    if not arg:
        logger.info(f'User prompted for {header}')
        header = header.title() if header else header
        arg, other_value = ask_user(logger, prompt=prompt, header=header, response_type=response,
                                    main_dict=main_dict, menu_dict=menu_dict, echo=echo, quit=quit)
        input_str = 'selected' if main_dict or menu_dict else 'entered'

    arg_temp = arg if echo else '*' * len(arg)

    if type(arg) is list:
        # specifically for args.file since it's of type list
        arg_temp = ', '.join(arg)

    logger.info(f'{header} ({arg_temp}) {input_str}')

    if other_value and header.lower() != 'server group':
        return arg, other_value
    return arg


def main():
    """
    Main function where command line arguments are validated, user is asked of other necessary details,
    and FtpConnection object is created. It establishes the FTP connection and performs file transfer
    """

    global curr_dir, config_dir
    prog_desc = 'purpose: transfer file to/from a host that is behind a UNIX gateway. file(s) will be transferred in Binary mode.'
    choice_prompt = '\n\nYour choice'
    username_prompt = 'Enter username'
    passcode_prompt = 'Enter IDLDAP.net Password'
    password_prompt = 'Enter password'
    required_str = 'All required arguments passed'
    action = {1: 'download', 2: 'upload'}
    gateway_valid = False

    parser = argparse.ArgumentParser(description=prog_desc, add_help=False)

    parser.add_argument('-g', '--gateway', help='UNIX gateway to be used')
    parser.add_argument(
        '-u', '--username', help='Gateway username. will override the value from JSON file if this argument is passed')
    parser.add_argument(
        '-p', '--passcode', help='IDLDAP.net password. if -u argument is passed, user will be prompted')
    parser.add_argument('-s', '--server', choices=[
                        'ms', 'nonms'], help='transfer file(s) to either a Managed Services host or a non-MS host')
    parser.add_argument('-i', '--instance',
                        help='Managed Services (only) client instance')
    parser.add_argument(
        '-a', '--action', choices=['download', 'upload'], help='download or upload')
    parser.add_argument('-f', '--file', nargs='*',
                        help='file(s) to be transferred; separated by spaces')
    parser.add_argument('-v', '--verbose', help=f'explain what is being done. though everything is logged in {LOG_FILE}',
                        action='store_const', const=logging.DEBUG, dest='loglevel', default=logging.ERROR)
    parser.add_argument(
        '-h', '--help', help='show this help message and exit', action='help')

    args = parser.parse_args()

    # create a logger object (that has both FileHandler and StreamHandler)
    logger = get_logger(__name__, args.loglevel)

    logger.info(equal_sign_line)
    logger.info(f'SCRIPT LOG - Start')
    logger.info(f'{__file__} [ Version {VERSION_NO} ] script initiated...')

    json_gate_user, json_gate_pwd, csv_dir, csv_list, log_dir = load_json_config(
        logger, JSON_CONFIG)

    # check if all required CSV files exist
    check_config(logger, csv_list)

    # assign each CSV file to their respective variables
    gateway_csv, ms_client_csv, non_ms_servers_csv, server_group_csv = csv_list

    # =========================================================================
    # parse CSV files and load into dictionaries
    # UNIX gateway information
    gateway_hosts, gateways_menu = parse_csv(gateway_csv, logger)
    # server group option: MS or non-MS
    server_groups, server_menu = parse_csv(server_group_csv, logger)
    # non-MS host options
    non_ms_hosts_options, non_ms_hosts_menu = parse_csv(non_ms_servers_csv, logger)
    # MS clients' environment information
    client_accounts, instance_menu = parse_csv(ms_client_csv, logger, sort=True)

    # =========================================================================
    # determine which parameters were and were not passed when calling the program
    # then check for validity

    # if there is at least 1 argument passed
    if len(args_passed([args.gateway, args.username, args.passcode, args.server, args.action, args.file])):
        logger.info('Checking for validity of arguments passed...')

    unix_gate, gateway_location = validate_or_ask_arg(
        logger, arg=args.gateway, header='Unix gate', prompt=choice_prompt, main_dict=gateway_hosts, menu_dict=gateways_menu, valid_dict=gateway_hosts)

    if args.username:
        gate_username = validate_or_ask_arg(
            logger, arg=args.username, header='Gateway username', prompt=username_prompt, response_type='str', quit=False)
        # if user passed the Unix gate username, then user also needs to enter gate password so nullify json_gate_pwd
        json_gate_pwd = None
    elif json_gate_user:
        logger.info(
            f'Unix gate user ({json_gate_user}) taken from {JSON_CONFIG}')
        gate_username = json_gate_user

    if args.passcode or not json_gate_pwd:
        gate_passcode = validate_or_ask_arg(
            logger, arg=args.passcode, header='IDLDAP.net password', prompt=passcode_prompt, response_type='str', quit=False, echo=False)
    elif json_gate_pwd:
        logger.info(
            f'Unix gate password ({len(json_gate_pwd) * "*"}) taken from {JSON_CONFIG}')
        gate_passcode = json_gate_pwd

    if args.server == 'nonms':
        if args.instance:
            logger.warning(
                f'Non-MS connection doesn\'t need an instance ({args.instance}) parameter...')
            args.instance = None
        # all necessary arguments for non-MS connection passed
        if len(args_passed([args.gateway, args.username, args.passcode, args.action, args.file])) == 5:
            logger.info(required_str)
    elif args.server == 'ms':
        # all necessary arguments for MS connection passed
        if len(args_passed([args.gateway, args.username, args.passcode, args.instance, args.action, args.file])) == 6:
            logger.info(required_str)

    server_group = validate_or_ask_arg(
        logger, arg=args.server, header='Server group', prompt=choice_prompt, main_dict=server_groups, menu_dict=server_menu)

    if server_group == 'nonms':
        # user wants to tranfer file(s) to a non-MS host
        remote_host = validate_or_ask_arg(
            logger, header='Non-MS Host', prompt='\n\nTransfer files to/from', main_dict=non_ms_hosts_options, menu_dict=non_ms_hosts_menu)

        # ask for more details
        logger.info(
            'User prompted to enter credentials for remote host and file location')
        remote_user, temp_val = ask_user(
            logger, header=f'Credentials for {remote_host}',  prompt=username_prompt,  response_type='str', quit=False)
        remote_pwd, temp_val = ask_user(
            logger, prompt=password_prompt, response_type='str', echo=False, quit=False)
        remote_dir, temp_val = ask_user(logger,
                                        prompt='Enter directory (absolute path) on remote host', response_type='str')

    else:
        # user wants to tranfer file(s) to a MS host

        if args.instance:
            # if --instance argument passed, then look up for the values in the client_accounts dictionary
            try:
                remote_user, remote_host, remote_pwd, clientID = client_accounts[args.instance]
            except KeyError:
                logger.warning(
                    f'MS instance passed as an argument ({args.instance}) is unrecognized...')
                args.instance = None

        if not args.instance:
            # if user invoked --ms but without --instance argument passed,
            # or if user provided an unrecognized --instance, then ask user for it
            
            logger.info('User prompted to select a MS client ID from the list...')

            # extract all the unique MS Client IDs from the dictionary and display for user menu
            temp_list = list(set([ value[3] for key, value in client_accounts.items() ]))
            temp_list.sort()
            MS_clientID_menu = {}
            counter = 1
            for id in temp_list:
                MS_clientID_menu[counter] = id
                counter += 1

            temp_val, clientID = ask_user(logger, prompt=choice_prompt, header='MS Client ID', main_dict=client_accounts, menu_dict=MS_clientID_menu)

            # extract only the instances for the chosen MS client ID and display for user menu
            MS_client_menu = {}
            counter = 1
            for key,value in client_accounts.items():
                if value[3] == clientID:
                    MS_client_menu[counter] = key
                    counter += 1
            
            # extract the remote_user, remote_host, remote_pwd and clientID from client_accounts dictionary
            (remote_user, remote_host, remote_pwd, clientID), temp_val = ask_user(logger,
                                prompt=choice_prompt, header='Managed Services Instance', main_dict=client_accounts, menu_dict=MS_client_menu, column=7)
            
        # set remote_dir to default directory
        remote_dir = f'aiprod{clientID}/implementor/{gate_username}'

    # host = f'MS host' if server_group == 'ms' else f'non-MS host'
    logger.info(f'Credentials to use: {remote_user}@{remote_host}')

    # ask user of the action to take
    action = validate_or_ask_arg(
        logger, arg=args.action, header='Action', prompt=choice_prompt, main_dict=action)

    # if not specified in the argument, ask user for file(s) to transfer then split and append to a list
    files = validate_or_ask_arg(
        logger, arg=args.file, prompt=f'Please specify filename(s) separated by a space', header=f'Files to {action}', response_type='list')

    # prior to establishing FTP connection, check first if files exist locally;
    # exit if one or more files is missing
    if action == 'upload':
        logger.info('Validating if upload file(s) exists...')
        check_if_existing(logger, files)
        logger.info('All file(s) confirmed to exist')

    logger.info(equal_sign_line)

    # create a FtpConnection object
    FTP = FtpConnection(unix_gate, gateway_location, gate_username, gate_passcode,
                        server_group, args.instance, action, files, remote_host, remote_user, remote_pwd, remote_dir, logger)

    # establish connection with Unix gate, connect with chosen remote host
    # and proceed to transfer files
    # errors will be handled within the FtpConnection class
    FTP.connect_and_transfer()

    logger.info('End of program')
    logger.info(f'Logged everything in {LOG_FILE}')
    logger.info('Thank you for using the script!')
    logger.info(f'SCRIPT LOG - End')
    logger.info(equal_sign_line)


if __name__ == '__main__':

    # call the main function
    main()
