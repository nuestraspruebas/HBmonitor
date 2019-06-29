Requirements:

- a webserver with activated PHP (apache, nginx or whatever) – PHP 7.x is ok

 

Modifikation/Extension of hbmonitor  – we log if a call is ended (I think it’s better as start) Please check permissions for writing the logfile in target folder !


        if p[0] == 'GROUP VOICE' and p[2] != 'TX':
            if p[1] == 'END':
                log_message = '{}: {} {}:   SYS: {:12.12s} SRC: {:8.8s}; {:15.15s} TS: {} TGID: {:>5s} SUB: {:8.8s}; {:30.30s} Time: {}s'.format(_now, p[0], p[1], p[3], p[5], alias_call(int(p[5]), peer_ids), p[7], p[8], p[6], alias_short
                # log only to file if system is NOT OpenBridge event (not logging open bridge system, name depends on your OB definitions) AND transmit time is LONGER as 2sec (make sense for very short transmits)
                if int(float(p[9])) > 2:
                    log_lh_message = '{},{},{},{},{},{},{},TS{},TG{},{},{}'.format(_now, p[9], p[0], p[1], p[3], p[5], alias_call(int(p[5]), peer_ids), p[7], p[8], p[6], alias_short(int(p[6]), subscriber_ids))
                    lh_logfile = open('/var/www/vhosts/dmr.bzsax.de/public_html/lastheard.log', "a")
                    lh_logfile.write(log_lh_message + '\n')
                    lh_logfile.close()
            elif p[1] == 'START':


The line: 

    if int(float(p[9])) > 2:

we can skip show in last heard for exmaple from MASTER with name OPB-Link

    if p[3] != 'OPB-Link' and int(float(p[9])) > 2:


I recommed to shorten the lastheard.log from time to time (I cut every day to 550 lines, longer values maybe extend the load time and parsing) with this script lastheard.sh:

    #!/bin/bash
    mv /var/www/html/lastheard.log /var/www/html/lastheard.log.save
    /usr/bin/tail -550 /var/www/html/lastheard.log.save > /var/www/html/lastheard.log
    mv /var/www/html/lastheard.log /var/www/html/lastheard.log.save
    /usr/bin/tail -550 /var/www/html/lastheard.log.save > /var/www/html/lastheard.log


Call this script with crontab for everyday use.

Put this file in /etc/cron.d/daily


Call the website with http://[YOUR_HOST/log.php it runs with a refresh/reload time of 30sec, change the script for other timeset.


Heiko, DL1BZ


PS 
Thank you, Heiko, who shared the lastheard code
The attached version of web_tables.py contains the display in the column of group names

73 Waldek SP2ONG

