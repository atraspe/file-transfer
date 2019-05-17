# file-transfer
Transfer file(s) to or from a host that is behind a UNIX gateway

## Description
This script is a simple template of automating the task of transferring files.
File transfer to a host that is behind a UNIX gateway requires authentication with the gateway prior to accessing the host itself. Arguments can be passed directly when calling the script - supports both the short and long version: e.g. --h or --help). If not, user will be prompted for the required information (e.g. username, server to connect to, file(s) to be transferred, etc.).
The script uses 3 different CSV files which has information about the gateway hosts, group of servers to access, and client information (client instance, hostname, FTP password, client ID).


## From The Author
My daily task at work involves a number of file transfers to and from hosts that are located behind a UNIX gateway. That means one action involves a 2-step process: 1) logging into the UNIX gateway and 2) logging into the host. If both at authenticated, then you may start the file transfer. This requires a lot of manual and repetitive work (e.g. specify which gateway to use, which FTP host to connect to, supply client-specific login info, directory to transfer files to/from, the files to be transferred, etc.), which is not only cumbersome but yep, it becomes boring. I thought of automating this task and this script definitely helped.
Oh btw, the script I'm using personally has my user credentials but this script is meant to ask you of those information.
You may ask, why not use one of those already available FTP tools? To which I say, well, where's the fun in that? :)

Disclaimer: I do not have any professional background in programming nor software engineering. That said, this is part of an initiative to get my hands dirty (coding!) to develop my technical skills and gain practical experience. Creating this script is part of an on-going effort to self study Python programming language. Just taking advantage of its use for automating some of my daily tasks and frankly, *shoulder shrug* I'm just having fun learning :) Those who might have a deeper understanding of Python may have a better (or more "Pythonic") way of doing this same task, so please be easy on me. Suggestions are definitely welcome and appreciated!

## How To Use
To clone, you'll need Git installed on your computer. This script was developed using Python 3.7 so the expectation is that you have at least the same version. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/atraspe/file-transfer.git

# Go into the repository
$ cd file-transfer

# Invoke -h/--help to see the command line arguments
$ python fts.py --help

# Sample arguments passed (--verbose recommended)
$ python fts.py -g ohio -u user1 -p xxxxx -m -i instance1 -a download --file file1 file2 --verbose
```

## Author
* Art Traspe


## License
[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments
* Thanks to my work colleagues who allowed me to bug them to test and improve this script :)