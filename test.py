#!/usr/bin/env python

import inspect
import os
import Queue
import re
import shutil
import subprocess
import tempfile
import time
import unittest

from watchdog.observers.fsevents import FSEventsObserver
from watchdog.events import FileSystemEventHandler

BASIC_HOSTFILE_PATH = './test_resources/basic_hostfile'
VIRGIN_HOSTFILE_PATH = './test_resources/virgin_hostfile'

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, shared_queue):
        self.shared_queue = shared_queue
    def on_modified(self, event):
        with open(event.src_path, 'r') as hostfile:
            body = hostfile.read()
            self.shared_queue.put(body)


class WebnullTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hostfile_path = os.path.join(self.temp_dir, 'test_hostfile')
        shutil.copy2(BASIC_HOSTFILE_PATH, self.hostfile_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # Run the given command
    # honetsly, best would be when the file changes, wait a fraction of a seonc and then send all new output and all new file
    # return when command exits.
    def run_test_command(self, cmd):
        observer = FSEventsObserver()
        shared_queue = Queue.Queue()
        handler = ChangeHandler(shared_queue)
        observer.schedule(handler, self.temp_dir)
        observer.start()

        args = ['./webnull.py'] + cmd
        env = os.environ.copy()
        if 'DEV_MODE' in env:
            del env['DEV_MODE']
        env['HOSTFILE_PATH'] = self.hostfile_path
        env['TEST_DURATION'] = '0.02'
        process = subprocess.Popen(args, env=env)
        process.wait()
        time.sleep(.09) # if we just quit, the observer doesn't see the final file action.

        bodies = []
        while not shared_queue.empty():
            bodies.append(shared_queue.get())

        observer.stop()
        observer.join()
        return bodies

    def check_test_file(self, test_case, work_in_progress=False):
        test_case_name = re.sub(r'^__main__\.(.+)',r'\1', unittest.TestCase.id(self))
        file_path = os.path.join('./test_resources/', test_case_name + '.out')
        if work_in_progress:
            with open(file_path, 'w') as f:
                f.write(test_case)
                print 'Wrote Success for ' + test_case_name
                print test_case
                self.assertTrue(False, msg="Test is still a work in progress.")
        else:
            with open(file_path, 'r') as f:
                success_case = f.read()
                self.assertEqual(test_case, success_case)

    def check_test_command(self, test_cmd, work_in_progress=False):
        bodies = self.run_test_command(test_cmd)
        test_file = '\n'.join(bodies)
        self.check_test_file(test_file, work_in_progress)

    # ------- Integration Tests --------
    # --- Deny ---
    def test_deny_new_site(self):
        deny_new_site_cmd = ['deny', 'facebook.com']
        self.check_test_command(deny_new_site_cmd)

    def test_deny_old_site(self):
        deny_old_site_cmd = ['deny', 'twitter.com']
        self.check_test_command(deny_old_site_cmd)

    def deny_new_hostname(self):
        deny_new_hostname_cmd = ['deny', 'https://news.ycombinator.com/item?id=13896065']
        self.check_test_command(deny_new_hostname_cmd)

    def test_deny_allowed_site(self):
        deny_old_cmd = ['deny', 'daringfireball.net']
        self.check_test_command(deny_old_cmd)

    def test_deny_allowed_site_partial(self):
        # What's the right behavior here?
        # TODO: questionable behavior here right now.
        deny_old_cmd = ['deny', 'daring']
        self.check_test_command(deny_old_cmd)

    def test_deny_fake_site(self):
        deny_fake_cmd = ['deny', 'foobar']
        # TODO: even *more* questionable behavior here.
        self.check_test_command(deny_fake_cmd)

    def test_deny_fake_site2(self):
        deny_fake_cmd = ['deny', '/foobar']
        self.check_test_command(deny_fake_cmd)

    def test_deny_first_site(self):
        shutil.copy2(VIRGIN_HOSTFILE_PATH, self.hostfile_path)
        first_site_cmd = ['deny', 'facebook.com']
        self.check_test_command(first_site_cmd)


    # --- Allow ---
    def test_allow_old_site(self):
        allow_old_site_cmd = ['allow', 'twitter']
        self.check_test_command(allow_old_site_cmd)

    def test_allow_old_url(self):
        allow_old_site_cmd = ['allow', 'http://twitter.com/gskinner/']
        self.check_test_command(allow_old_site_cmd)

    def test_allow_new_site(self):
        allow_new_site_cmd = ['allow', 'foobar']
        self.check_test_command(allow_new_site_cmd)

    def test_allow_all_sites(self):
        allow_all_cmd = ['allow', '-a']
        self.check_test_command(allow_all_cmd)

    def test_allow_allowed_site(self): # TODO: arguably we should note that it is already allowed...
        allow_allowed_cmd = ['allow', 'daring']
        self.check_test_command(allow_allowed_cmd)

    def test_allow_multi_match(self):
        deny_twitter_api_cmd = ['deny', 'api.twitter.com']
        allow_twitter_cmd = ['allow', 'twitter']
        self.run_test_command(deny_twitter_api_cmd)
        self.check_test_command(allow_twitter_cmd)


if __name__ == '__main__':
    unittest.main()
