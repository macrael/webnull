#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest
import time
import subprocess
import Queue

from watchdog.observers.fsevents import FSEventsObserver
from watchdog.events import FileSystemEventHandler

BASIC_HOSTFILE_PATH = './test_resources/basic_hostfile'

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, shared_queue):
        self.shared_queue = shared_queue
    def on_modified(self, event):
        print 'MODIFIED'
        with open(event.src_path, 'r') as hostfile:
            body = hostfile.read()
            self.shared_queue.put(body)


class WebnullTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hostfile_path = os.path.join(self.temp_dir, 'test_hostfile')
        shutil.copy2(BASIC_HOSTFILE_PATH, self.hostfile_path)
        print self.hostfile_path

    def tearDown(self):
        print 'Tearing Down'
        shutil.rmtree(self.temp_dir)


    # Run the given command
    # Every time the hostfile_path file changes, yeild the current version to the caller
    # Maybe also yeild the cmd output?
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
        env['TEST_DURATION'] = '0.05'
        process = subprocess.Popen(args, env=env)
        process.wait()
        time.sleep(.1) # if we just quit, the observer doesn't see the final file action.

        bodies = []
        while not shared_queue.empty():
            bodies.append(shared_queue.get())

        print 'back'
        observer.stop()
        observer.join()
        return bodies


    def test_deny_new_site(self):
        print 'New Site Add'
        deny_new_site_cmd = ['deny', 'facebook.com']
        bodies = self.run_test_command(deny_new_site_cmd)
        print 'denied?'
        self.assertTrue(True)
        # bodies.count == 1
        # and the body has to be the same as the example body.
        # Should be able to record this and play it back. save based on name of everything.

    def test_allow_old_site(self):
        print 'Old Site Allow'
        allow_old_site_cmd = ['allow', 'daring']
        self.run_test_command(allow_old_site_cmd)
        # Get back: (commented out stuff, "daring is enabled until 2017-03-09 23:24:02.994630")
        # Get back: (uncommented out stuff, "")
        # let's just do file changes for now.


if __name__ == '__main__':
    unittest.main()
