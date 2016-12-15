#!/usr/bin/env python

import argparse
import urlparse
import re

SHIBBOLETH = "## webnull will only write below this line ##"
# HOSTFILE_PATH = "/etc/hosts"
HOSTFILE_PATH = "./fakehosts"

def arg_parser():
    parser = argparse.ArgumentParser(description='A tool for putting websites into a black hole.')
    parser.add_argument('sitename', help='The website to be blackholed. Will be stripped down to just the hostname')
    parser.add_argument('-e', '--enable', action='store_true', help='re-enables access to sitename')
    return parser

def parse_hostname(sitename):
    parsed_url = urlparse.urlparse(sitename)
    hostname = parsed_url.netloc
    if hostname == '':
        # If you pass in "facebook.com/foo" urlparse treats it all as the path
        match = re.match("[^\/]+", parsed_url.path)
        if match == None:
            print "ERROR: Unable to make the provided sitename into a hostname: " + parsed_url.path
            exit(1)
        hostname = match.group(0)

    return hostname

def nullify_site(sitename):

    hostname = parse_hostname(sitename)

    with open(HOSTFILE_PATH, "r+") as hostfile:
        hosts = hostfile.read()

        shib_loc = hosts.find(SHIBBOLETH)
        if shib_loc == -1:
            hostfile.write("\n" + SHIBBOLETH + "\n\n")
        else:
            host_loc = hosts.find("\t" + sitename + "\n", shib_loc)
            if host_loc != -1:
                print hostname + " has already been sent to webnull"
                exit(0)

        ip5null = "127.0.0.1\t"
        ip6null = "::1\t\t"

        for null in [ip5null, ip6null]:
            for www in ["", "www."]:
                hostfile.write(null + www + hostname + "\n")

def unblock_site(sitename):
    print "UNBLOCKING"
    hostname = parse_hostname(sitename)

    hosts = ""
    with open(HOSTFILE_PATH, "r+") as hostfile:
        hosts = hostfile.read()

    parts = hosts.split(SHIBBOLETH)
    if len(parts) != 2:
        print "Your hostsfile is not managed by webnull, we won't change anything"
        exit(1)
    else:
        preroll = parts[0]
        managed = parts[1]

        null_matcher = r'\n([^#\n].*' + re.escape(hostname) + r')'
        new_managed = re.sub(null_matcher, r'\n# \1', managed)

        with open(HOSTFILE_PATH, "w") as hostfile:
            hostfile.write(preroll + SHIBBOLETH + new_managed)


if __name__ == "__main__":
    args = arg_parser().parse_args()

    if args.enable:
        unblock_site(args.sitename)
    else:
        nullify_site(args.sitename)
