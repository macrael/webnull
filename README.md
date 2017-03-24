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
`$ cp /etc/hosts dummyhosts`
`$ export DEV_MODE=1`

Testing
----------
* `$ brew install python`
* `$ easy_install pip`
* `$ pip install virtualenv`
* `$ virtualenv venv`
* `$ source venv/bin/activate`
* `$ pip install watchdog`
* `$ python -m unittest discover tests`
