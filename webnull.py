#!/usr/bin/env python

import argparse
import urlparse
import re

SHIBBOLETH = "## webnull will only write below this line ##"
HOSTFILE_PATH = "/etc/hosts"

HOST_MATCHER = r'^([^#\n].*{0})'
COMMENTED_MATCHER = r'^#\s(.*{0})'

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

    hosts = ""
    with open(HOSTFILE_PATH, "r") as hostfile:
        hosts = hostfile.read()

    parts = hosts.split(SHIBBOLETH)
    preroll = parts[0]
    managed = ""
    assert(len(parts) < 3)
    if len(parts) == 2:
        managed = parts[1]

    null_matcher = HOST_MATCHER.format(hostname)
    neuter_matcher = COMMENTED_MATCHER.format(hostname)
    if re.search(null_matcher, managed, flags=re.MULTILINE) != None:
        # if it's not commented, we ignore it
        print hostname + " has already been sent to webnull"
        exit(0)
    elif re.search(neuter_matcher, managed, flags=re.MULTILINE) != None:
        # if it's commented, we replace it
        managed = re.sub(neuter_matcher, r'\1', managed, flags=re.MULTILINE)
    else:
        # if it's not there, we write it.
        ip5null = "127.0.0.1\t"
        ip6null = "::1\t\t"

        for null in [ip5null, ip6null]:
            for www in ["", "www."]:
                managed += (null + www + hostname + "\n")

    with open(HOSTFILE_PATH, "w") as hostfile:
        hostfile.write(preroll + SHIBBOLETH + managed)

def unblock_site(sitename):

    hostname = parse_hostname(sitename)

    hosts = ""
    with open(HOSTFILE_PATH, "r") as hostfile:
        hosts = hostfile.read()

    parts = hosts.split(SHIBBOLETH)
    if len(parts) != 2:
        print "Your hostsfile is not managed by webnull, we won't change anything"
        exit(1)
    else:
        preroll = parts[0]
        managed = parts[1]

        null_matcher = HOST_MATCHER.format(hostname)
        new_managed = re.sub(null_matcher, r'# \1', managed, flags=re.MULTILINE)

        with open(HOSTFILE_PATH, "w") as hostfile:
            hostfile.write(preroll + SHIBBOLETH + new_managed)


if __name__ == "__main__":
    args = arg_parser().parse_args()

    if args.enable:
        unblock_site(args.sitename)
    else:
        nullify_site(args.sitename)
