Webnull
======
A tool for putting hosts into a blackhole

Webnull is a command line tool that lets you easily stop your computer from being able to reach certain websites.

Usage: `sudo webnull deny example.com`

Above, example.com will be added to your hosts file and routed to localhost. The next time you try to visit example.com your browser won't be able to find it.

Later, `sudo webnull allow example` will re-allow access to the site for five minutes.

`sudo webnull allow -am` will allow access to all blocked sites until tomorrow morning.

See `webnull -h` for full usage.

Installation
--------------


Dev Mode
--------------
Dev Mode protects your live hostfile during development
```
$ cp /etc/hosts dummyhosts
$ export DEV_MODE=1
$ ./webnull.py allow ...
```

Testing
----------
```
$ brew install python
$ easy_install pip
$ pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
$ pip install watchdog
$ python setup.py test
```

This code has only been tested on macOS with python 2.7

It will only work on systems that use an /etc/hosts file.
