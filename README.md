Webnull
======
A tool for putting hosts into a blackhole

Webnull is a command line tool that lets you easily stop your computer from being able to reach certain websites.

Usage: `sudo webnull [http://example.com/ | example.com]`

In the above example, example.com will be added to your hosts file and routed to localhost. The next time you try to visit example.com your browser won't be able to find it.

Dev Mode
--------------
`$ cp /etc/hosts dummyhosts`
`$ export DEV_MODE=1`
