# file-transfer
Transfer file to or from a host that is behind a UNIX gateway

## Description
This script is a simple template of automating that task.
The script needs certain arguments to be passed, or it not, user will be prompted for those information (e.g. username, server to connect to, file to transfer, etc.). Transferring files to a host that is sitting behind a UNIX gateway entails you to login to the gateway first before logging into the host itself to transfer your file. 
The script uses 3 CSV files, where you store information about the gateway hosts, group of servers you'd like to access, and then client information (client instance, hostname, FTP password, client ID).

## From The Author
My daily task at work involves a lot of transferring files to and from hosts that are sitting behind a UNIX gateway. That means one action involves a 2-step process, 1) logging into the UNIX gateway and 2) logging into the host itself, before you can even transfer the file(s). When you have to do this process a number of times in a day, it becomes cumbersome and yep, boring. I thought of automating this part of my job and it sure helped tremendously.

Disclaimer: I do not have any professional background in programming nor software engineering. That said, this is an initiative to get my hands dirty (coding!) to develop my technical skills and gain practical experience. Creating this script is part of an on-going effort to self study Python programming language. Just taking advantage of its use for everyday tasks and, just for fun! :) You, who has a deeper understanding of the said language might have a better (or more pythonic) way of doing this same task, so please be easy on me. Suggestions are definitely appreciated!

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
$ python fts.py upload.txt -g ohio -u user1 -m -i instance1 -a upload --verbose
```

## Author
* Art Traspe


## License
[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments
