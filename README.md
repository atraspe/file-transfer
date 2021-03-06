# file-transfer
Transfer file(s) to or from a host that is behind a UNIX gateway

## Description
File transfer to a host that is behind a UNIX gateway requires authentication with the gateway prior to accessing the host itself. Arguments can be passed directly when invoking the script - supports both the short and long version: e.g. --h or --help). If not, user will be prompted for the required information (e.g. Unix gate, server to connect to, file(s) to be transferred, etc.).
The script uses different CSV files that contain information about the gateway hosts, group of servers to access, and client information (client instance, hostname, FTP password, client ID).

File Transfer Protocol (FTP) is a standard network protocol used for the transfer of computer files between a client and server on a computer network. [Wikipedia](https://en.wikipedia.org/wiki/File_Transfer_Protocol)

A gateway is a network node that serves as an access point to another network. [Wikipedia](https://en.wikipedia.org/wiki/Default_gateway)

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
$ python fts.py -g ohio -s ms -i instance1 -a download --file file1 file2 --verbose
```

You can "personalize" this script by updating the JSON config file of the Unix gateway username and password, which the script will use by default. You can always override the JSON values by passing the --username argument.

## Motivation
Part of my daily job activities involve file transfers to and from hosts that are located behind a UNIX gateway. That means one action involves a 3-step process: 1) UNIX gate login, 2) remote host login, and finally 3) file transfer. This requires a lot of manual and repetitive work (e.g. specify which gateway to use, which FTP host to connect to, supply client-specific login info, directory to transfer files to/from, the files to be transferred, etc.). If it's just a host or two, that's fine but when we're talking about hundreds of them, it becomes cumbersome because you need to keep track of the different hostnames, credentials, and other necessary information. So it got me thinking, why not automate this task? This is the result of that curiosity. You may ask, why not use one of those already available FTP tools? To which I will say, well, where's the fun in that? :)

This script serves as a template with which you can adjust to how your environment is setup. I've set it up to store some of my credentials in the JSON file but this script is also meant to ask you of those information.

### What I've learned:
Disclaimer: I do not have any professional background in programming nor software engineering. That said, this is part of an initiative to get my hands dirty (coding!) to grow and build my technical skills and gain practical experience. Creating this script is part of an on-going effort to self study Python programming language - get the basics down and start building mini projects (and deliver value) to cement my learning. Just taking advantage of its use for automating some of my daily tasks and frankly, I'm just having fun learning :)
For those who might have a deeper understanding of Python may have a better (or more "Pythonic") way of doing this same task, please be easy on me. Suggestions are definitely welcome and appreciated!

Since this is my first real-world/automation project using Python, it's an understatement that I learned a ton! (Though probably in a few months when I learn more and I look back at my code, I'll ask myself, ugh, what was I doing?? LOL) And the fact that I'm actually using it makes it all the more worth it. Obviously I had to refactor my code multiple times since I'm also learning on the fly on most areas. But some of the major areas that stood out:

- Dictionaries. It is the best data structure specific to my needs here, in my opinion, since for every key I was able to pack a number of information by assigning a tuple for its value. For example, for every account instance (key), I set its value to a tuple of the instace ID, hostname, FTP password, and client ID. Also the fact that all the information from the CSV files are unordered, it was easier to just sort them out based on their keys, before printing them to the screen for a user menu.

- Argparse. This command-line parsing module in the Python standard library made it so much easier to work with user arguments (optional and/or required). Wasn't too difficult to implement to be honest (thanks to the Python HOWTOs Tutorial). The auto-generated help, usage messages, and error alerts are a plus as well. I'd imagine it requires more work when I would have to just use the sys.argv (I maybe wrong though). I will definitely use this more often for scripting work moving forward.

- Exception. It gets exciting when you're able to define your own/custom exceptions that serve your purpose, which I figured out how to do here (nothing complicated, just wanted to try it out). It was also cool to learn to selectively suppress/ignore some "expected" errors/behaviors using the contextlib.suppress() function, paired with the "with" statement. That is equivalent to using a try/except clause. It's lovely. It's beautiful :)

- OOP. Midway through development, I decided to take the OOP path. It's daunting at first but it was a nice introduction to putting the knowledge into practice. I know when I learn more about the power of OOP, I'll be able to better my initial approach.

- Reasearch and problem solving. Tons of it. The ability to scour the web and read through lots of articles/blogs on a specific topic that I'm not familiar with and solve the problem I'm faced with.

## Developer
* Art Traspe

## License
[The MIT License](https://choosealicense.com/licenses/mit/)

## Acknowledgments
* Thanks to Renmar Hernandez for the inspiration in creating this script
* Thanks to my work colleagues who allowed me to bug them to test and improve this script :)