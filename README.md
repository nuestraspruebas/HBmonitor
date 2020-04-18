# hbmonitor3
Python 3 implementation of N0MJS HBmonitor for HBlink https://github.com/kc1awv/hbmonitor3

***This software is VERY, VERY, VERY new!***

Since Python 3 is the way of the future, I'm updating the HBmonitor code from Python 2 to Python 3.

__THIS SOFTWARE IS WORKING__, hopefully...

Questions, comments, and complaints can be forwarded to the DVSwitch group at [DVSwitch - HBlink Subgroup](https://dvswitch.groups.io/g/HBlink/topics)

If you would like to contribute to this effort, please submit updated code as a PR to this repository.

***73, KC1AWV***

---

***This is version of HBMonitor modified by SP2ONG 2019, 2020***

---

**Socket-Based Reporting for HBlink**

Over the years, the biggest request recevied for HBlink (other than call-routing/bridging tools) has been web-based diagnostics and/or statistics for the program.

I strongly disagree with including the amount of overhead this would require inside HBlink -- which still runs nicely on very modest resources. That it does this, and is in Python is a point of pride for me... Just let me have this one, ok? What I have done is added some hooks to HBlink, which will be expanded over time, whereby it listens on a TCP socket and provides the raw data necessary for a "web dashboard", or really any external logging or statistics gathering program.

HBmonitor is my take on a "web dashboard" for HBlink.

***THIS SOFTWARE IS VERY, VERY NEW***

Right now, I'm just getting into how this should work, what does work well, what does not... and I am NOT a web applications programmer, so yeah, that javascript stuff is gonna look bad. Know what you're doing? Help me!

It has now reached a point where folks who know what they're doing can probably make it work reasonably well, so I'm opening up the project to the public.

***GOALS OF THE PROJECT***

Some things I'm going to stick to pretty closely. Here they are:

+ HBmonitor be one process that includes a webserver
+ Websockets are used for pushing data to the browser - no long-polling, etc.
+ Does not provide data that's easily misunderstood

***0x49 DE N0MJS***

Copyright (C) 2013-2018  Cortney T. Buffington, N0MJS <n0mjs@me.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA


    cd /opt
    git clone https://github.com/sp2ong/HBmonitor.git
    cd HBmonitor
    chmod +x install.sh
    ./install.sh
    cp config-SAMPLE.py config.py
    edit config.py and change what you necessary
    cp utils/hbmon.service /lib/systemd/system/
    systemctl enable hbmon
    systemctl start hbmon
    systemctl status hbmon
    forward TCP ports 8080 and 9000 in firewall
    
    Please remember the table lastherad displays only station transmissions that are longer than 2 seconds
    
