#!/usr/bin/env python

import argparse
import datetime
import os
import re
import signal
import sys
import time
import urlparse

HOST_MATCHER = r'^([^#\n].*{0})'
COMMENTED_MATCHER = r'^#\s(.*{0})'

class ManagedHostfile:
    SHIBBOLETH = '\n## webnull will only write below this line ##\n'
    HOSTFILE_PATH = '/etc/hosts' if 'DEV_MODE' not in os.environ else 'dummyhosts'
    if 'HOSTFILE_PATH' in os.environ:
        HOSTFILE_PATH = os.environ['HOSTFILE_PATH']

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
        _, body = self._head_and_tail()
        return body

    def write_body(self, new_body):
        head, _ = self._head_and_tail()
        with open(self.HOSTFILE_PATH, 'w') as hostfile:
            hostfile.write(head + self.SHIBBOLETH + new_body)

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
        managed = re.sub(neuter_matcher, r'\1', managed, flags=re.MULTILINE)
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
    managed = hostfile.current_body()

    if managed == '':
        print 'Your hostsfile is not managed by webnull, we won\'t change anything'
        sys.exit(1)
    else:
        null_matcher = HOST_MATCHER.format(hostname)
        new_managed = re.sub(null_matcher, r'# \1', managed, flags=re.MULTILINE)

        hostfile.write_body(new_managed)

def unblock_all():
    hostfile = ManagedHostfile()
    managed = hostfile.current_body()

    if managed == '':
        print 'Your hostsfile is not managed by webnull, we won\'t change anything'
        sys.exit(1)
    else:
        new_managed = re.sub(r'^(.+)', r'# \1', managed, flags=re.MULTILINE)

        hostfile.write_body(new_managed)

def reblock_all():
    hostfile = ManagedHostfile()
    managed = hostfile.current_body()

    if managed == '':
        print 'Your hostsfile is not managed by webnull, we won\'t change anything'
        sys.exit(1)
    else:
        new_managed = re.sub(r'^#\s(.+)', r'\1', managed, flags=re.MULTILINE)

        hostfile.write_body(new_managed)

def reblock_timer(sitename, duration, all=False):
    if 'TEST_DURATION' in os.environ:
        duration = float(os.environ['TEST_DURATION'])

    if all:
        unblock_all()
    else:
        unblock_site(sitename)

    def cleanup():
        if all:
            reblock_all()
        else:
            nullify_site(sitename)

    def sigint_handler(signal, frame):
        cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    print sitename + ' is enabled until ' + str(datetime.datetime.now() + datetime.timedelta(minutes=duration))
    time.sleep(duration * 60)
    cleanup()

def enable_all(duration):
    reblock_timer('ALL_ARE_ENABLED', duration, all=True)


def deny_site(args):
    nullify_site(args.sitename)

def allow_site(args):
    if args.all:
        enable_all(args.time)
    else:
        reblock_timer(args.sitename, args.time)

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
