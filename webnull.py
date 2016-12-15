#!/usr/bin/env python

import argparse
import urlparse
import re

SHIBBOLETH = "## webnull will only write below this line ##"
HOSTFILE_PATH = "/etc/hosts"

def arg_parser():
    parser = argparse.ArgumentParser(description='A tool for putting websites into a black hole.')
    parser.add_argument('sitename', help='The website to be blackholed. Will be stripped down to just the hostname')
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

        if hosts.find(SHIBBOLETH) == -1:
            hostfile.write("\n" + SHIBBOLETH + "\n\n")

        ip5null = "127.0.0.1\t"
        ip6null = "::1\t\t"

        for null in [ip5null, ip6null]:
            for www in ["", "www."]:
                hostfile.write(null + www + hostname + "\n")


if __name__ == "__main__":
    args = arg_parser().parse_args()

    nullify_site(args.sitename)
