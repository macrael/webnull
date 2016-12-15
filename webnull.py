#!/usr/bin/env python

import argparse
import urlparse
import re
import signal
import sys
import time
import datetime

HOST_MATCHER = r'^([^#\n].*{0})'
COMMENTED_MATCHER = r'^#\s(.*{0})'

class ManagedHostfile:
    SHIBBOLETH = "## webnull will only write below this line ##"
    # HOSTFILE_PATH = "/etc/hosts" DEBUG
    HOSTFILE_PATH = "./fakehosts"

    def _head_and_tail(self):
        with open(self.HOSTFILE_PATH, "r") as hostfile:
            hosts = hostfile.read()
            parts = hosts.split(self.SHIBBOLETH)
            assert(len(parts) < 3)
            assert(len(parts) > 0)

            preroll = parts[0]
            managed = ""
            if len(parts) == 2:
                managed = parts[1]

            return preroll, managed

    def current_body(self):
        _, body = self._head_and_tail()
        return body

    def write_body(self, new_body):
        head, _ = self._head_and_tail()
        with open(self.HOSTFILE_PATH, "w") as hostfile:
            hostfile.write(head + self.SHIBBOLETH + new_body)


def arg_parser():
    parser = argparse.ArgumentParser(description='A tool for putting websites into a black hole.')
    parser.add_argument('sitename', help='The website to be blackholed. Will be stripped down to just the hostname')
    parser.add_argument('-e', '--enable', action='store_true', help='re-enables access to sitename')
    parser.add_argument('-t', '--time', help='sets the duration to enable a site for.', default=5, type=int)
    return parser

def parse_hostname(sitename):
    parsed_url = urlparse.urlparse(sitename)
    hostname = parsed_url.netloc
    if hostname == '':
        # If you pass in "facebook.com/foo" urlparse treats it all as the path
        match = re.match("[^\/]+", parsed_url.path)
        if match == None:
            print "ERROR: Unable to make the provided sitename into a hostname: " + parsed_url.path
            sys.exit(1)
        hostname = match.group(0)

    return hostname

def nullify_site(sitename):
    hostname = parse_hostname(sitename)

    hostfile = ManagedHostfile()
    managed = hostfile.current_body()

    null_matcher = HOST_MATCHER.format(hostname)
    neuter_matcher = COMMENTED_MATCHER.format(hostname)
    if re.search(null_matcher, managed, flags=re.MULTILINE) != None:
        # if it's not commented, we ignore it
        print hostname + " has already been sent to webnull"
        sys.exit(0)
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

    hostfile.write_body(managed)

def unblock_site(sitename):
    hostname = parse_hostname(sitename)

    hostfile = ManagedHostfile()
    managed = hostfile.current_body()

    if managed == "":
        print "Your hostsfile is not managed by webnull, we won't change anything"
        sys.exit(1)
    else:
        null_matcher = HOST_MATCHER.format(hostname)
        new_managed = re.sub(null_matcher, r'# \1', managed, flags=re.MULTILINE)

        hostfile.write_body(new_managed)

def reblock_timer(sitename, duration):
    unblock_site(sitename)

    def sigint_handler(signal, frame):
        nullify_site(sitename)
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    print sitename + " is enabled until " + str(datetime.datetime.now() + datetime.timedelta(minutes=duration))
    time.sleep(duration * 60)
    nullify_site(sitename)

if __name__ == "__main__":
    args = arg_parser().parse_args()

    if args.enable:
        reblock_timer(args.sitename, args.time)
    else:
        nullify_site(args.sitename)
