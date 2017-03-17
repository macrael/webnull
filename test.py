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

    def check_test_file(self, test_case, save_success_case=False):
        test_case_name = re.sub(r'^__main__\.(.+)',r'\1', unittest.TestCase.id(self))
        file_path = os.path.join('./test_resources/', test_case_name + '.out')
        if save_success_case:
            with open(file_path, 'w') as f:
                f.write(test_case)
                print 'Wrote Success for ' + test_case_name
                print test_case
                self.assertTrue(False)
        else:
            with open(file_path, 'r') as f:
                success_case = f.read()
                self.assertEqual(test_case, success_case)

    def check_test_command(self, test_cmd, save_success_case=False):
        bodies = self.run_test_command(test_cmd)
        test_file = '\n'.join(bodies)
        self.check_test_file(test_file, save_success_case)

    # ------- Integration Tests --------
    def test_deny_new_site(self):
        deny_new_site_cmd = ['deny', 'facebook.com']
        self.check_test_command(deny_new_site_cmd)

    def test_deny_old_site(self):
        deny_old_site_cmd = ['deny', 'twitter.com']
        self.check_test_command(deny_old_site_cmd)

    def test_allow_old_site(self):
        allow_old_site_cmd = ['allow', 'twitter']
        self.check_test_command(allow_old_site_cmd)

    def test_allow_new_site(self):
        allow_new_site_cmd = ['allow', 'foobar']
        self.check_test_command(allow_new_site_cmd)

    def test_allow_all_sites(self):
        allow_all_cmd = ['allow', '-a']
        self.check_test_command(allow_all_cmd)

    # test that matches match multiple matches
    def test_allow_multi_match(self):
        deny_twitter_api_cmd = ['deny', 'api.twitter.com']
        allow_twitter_cmd = ['allow', 'twitter']
        self.run_test_command(deny_twitter_api_cmd)
        self.check_test_command(allow_twitter_cmd)

    # test times somehow

        # Get back: (commented out stuff, "daring is enabled until 2017-03-09 23:24:02.994630")
        # Get back: (uncommented out stuff, "")
        # let's just do file changes for now.


if __name__ == '__main__':
    unittest.main()
