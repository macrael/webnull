Webnull
======
A tool for putting hosts into a blackhole.

Webnull is a command line program that lets you stop your computer from being able to reach certain websites.

Usage: `sudo webnull deny example.com`

Above, example.com will be added to your hosts file and routed to localhost. The next time you try to visit example.com your browser won't be able to find it.

Later, `sudo webnull allow example` will re-allow access to the site for five minutes.

`sudo webnull allow -am` will allow access to all blocked sites until tomorrow morning.

See `webnull -h` for full usage.

Installation
--------------
`pip install webnull`


Usage
---------
```
$ sudo webnull deny example.com
$ sudo webnull deny https://example.com/foo/bar
$ sudo webnull allow example.com
$ sudo webnull allow -t 30 example.com
$ sudo webnull allow -a
$ sudo webnull allow -am
```


Development
=========

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

Releasing
-------------
```
$ python setup.py sdist bdist_wheel
$ twine upload dist/* [-r testpypi]
$ rm -rf dist/*
* tag the release
* bump the version number
```

This code has only been tested on macOS with python 2.7

It will only work on systems that use an /etc/hosts file.
