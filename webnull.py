#!/usr/bin/env python

import argparse
import datetime
import os
import re
import signal
import sys
import time
import urlparse

HOST_MATCHER = r'^([^#\n].*{0}.*)'
COMMENTED_MATCHER = r'^#\s(.*{0})'

class ManagedHostfile:
    SHIBBOLETH = '\n## webnull will only write below this line ##\n'
    HOSTFILE_PATH = '/etc/hosts' if 'DEV_MODE' not in os.environ else 'dummyhosts'
    if 'HOSTFILE_PATH' in os.environ:
        HOSTFILE_PATH = os.environ['HOSTFILE_PATH']

    def __init__(self):
        self.head, self.body = self._head_and_tail()

    def _head_and_tail(self):
        with open(self.HOSTFILE_PATH, 'r') as hostfile:
            hosts = hostfile.read()
            parts = hosts.split(self.SHIBBOLETH)
            assert(len(parts) < 3)
            assert(len(parts) > 0)

            preroll = parts[0]
            managed = ''
            if len(parts) == 2:
                managed = parts[1]

            return preroll, managed

    def current_body(self):
        return self.body

    def write_body(self, new_body):
        with open(self.HOSTFILE_PATH, 'w') as hostfile:
            hostfile.write(self.head + self.SHIBBOLETH + new_body)
            self.body = new_body

    # Returns a list of hostnames modified
    def transform_body(self, search_re, replacement_string):
        managed = self.current_body()

        matched_hostnames = None
        if managed == '':
            print 'Your hostsfile is not managed by webnull, we won\'t change anything'
            exit(1)
        else:
            lines = re.findall(search_re, managed, flags=re.MULTILINE)
            matched_hostnames = set(map(lambda line: re.match(r'^[^\t]+\t+([^\t]+)$', line).group(1), lines))
            if (len(matched_hostnames) != 0):
                new_managed = re.sub(search_re, replacement_string, managed, flags=re.MULTILINE)
                self.write_body(new_managed)

        return matched_hostnames

def parse_hostname(sitename):
    parsed_url = urlparse.urlparse(sitename)
    hostname = parsed_url.netloc
    if hostname == '':
        # If you pass in 'facebook.com/foo' urlparse treats it all as the path
        match = re.match(r'[^/]+', parsed_url.path)
        if match == None:
            print 'ERROR: Unable to make the provided sitename into a hostname: ' + parsed_url.path
            sys.exit(1)
        hostname = match.group(0)

    www_matcher = r'^www\.(.+)'
    if re.search(www_matcher, hostname) != None:
        hostname = re.sub(www_matcher, r'\1', hostname)

    return hostname

def nullify_site(sitename):
    hostname = parse_hostname(sitename)

    hostfile = ManagedHostfile()
    managed = hostfile.current_body()

    null_matcher = HOST_MATCHER.format(hostname)
    neuter_matcher = COMMENTED_MATCHER.format(hostname)
    if re.search(null_matcher, managed, flags=re.MULTILINE) != None:
        # if it's not commented, we ignore it
        print hostname + ' has already been sent to webnull'
        sys.exit(0)
    elif re.search(neuter_matcher, managed, flags=re.MULTILINE) != None:
        # if it's commented, we replace it
        hostfile.transform_body(neuter_matcher, r'\1')
    else:
        # if it's not there, we write it.
        ip5null = '127.0.0.1\t'
        ip6null = '::1\t\t'

        for null in [ip5null, ip6null]:
            for www in ['', 'www.']:
                managed += (null + www + hostname + '\n')

        hostfile.write_body(managed)

def unblock_site(sitename):
    hostname = parse_hostname(sitename)
    hostfile = ManagedHostfile()

    null_matcher = HOST_MATCHER.format(hostname)
    unblocked_hosts = hostfile.transform_body(null_matcher, r'# \1')

    if len(unblocked_hosts) == 0:
        print 'No host matches ' + sitename + '.'
        sys.exit(1)

    print 'Allowing access to:'
    print '\n'.join(unblocked_hosts)


def unblock_all():
    hostfile = ManagedHostfile()

    all_matcher = r'^(.+)'
    unblocked_hosts = hostfile.transform_body(all_matcher, r'# \1')
    print "Allowing access to all sites" # finally a reason to use python 3

def reblock_all():
    hostfile = ManagedHostfile()

    unblocked_matcher = r'^#\s(.+)'
    reblocked_hosts = hostfile.transform_body(unblocked_matcher, r'\1')

def reblock_timer(duration, cleanup_func):
    if 'TEST_DURATION' in os.environ:
        duration = float(os.environ['TEST_DURATION'])

    def sigint_handler(signal, frame):
        cleanup_func()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    print 'until ' + str(datetime.datetime.now() + datetime.timedelta(minutes=duration))
    time.sleep(duration * 60)
    cleanup_func()


def deny_site(args):
    nullify_site(args.sitename)

def allow_site(args):
    cleanup_func = None
    if args.all:
        unblock_all()
        cleanup_func = reblock_all
    else:
        unblock_site(args.sitename)
        cleanup_func = lambda: nullify_site(args.sitename)

    reblock_timer(args.time, cleanup_func)

def arg_parser():
    parser = argparse.ArgumentParser(description='A tool for putting websites into a black hole.')
    commands = parser.add_subparsers(title='commands', metavar='')

    deny = commands.add_parser('deny', description='Add a site to the black hole. It will become unreachable.', help='Add a site to the black hole. It will become unreachable.')
    deny.add_argument('sitename', help='The website to be blackholed. A URL will be stripped down correctly.')
    deny.set_defaults(func=deny_site)

    allow = commands.add_parser('allow', description='Allow access to a blackholed site for a spell.', help='Allow access to a blackholed site for a spell.')
    allow.add_argument('-t', '--time', help='sets the duration to enable a site for. Default is five minutes.', default=5, type=int)
    all_or_one = allow.add_mutually_exclusive_group(required=True)
    all_or_one.add_argument('-a', '--all', action='store_true', help='All blackholed hostnames will be granted access instead of a matching sitename.')
    all_or_one.add_argument('sitename', help='All blackholed hostnames that contain this string will be temporarlly granted access.', nargs='?')
    allow.set_defaults(func=allow_site)

    return parser

if __name__ == '__main__':
    if 'DEV_MODE' in os.environ:
        print 'Running in Development Mode'

    args = arg_parser().parse_args()
    args.func(args)
