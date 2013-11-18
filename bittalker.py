# -----------------------------------------------------------------------------
# Created by vrhax on November 16, 2013
# -----------------------------------------------------------------------------
# USAGE: python bittalker.py
#
# -----------------------------------------------------------------------------
# import system libraries
# -----------------------------------------------------------------------------

import ConfigParser, os, sys, time

# -----------------------------------------------------------------------------
# bitcoin wallet connection library
# must install bitcoin-python first (as follows)
#
# sudo apt-get install python-setuptools
# sudo easy_install pip
# sudo pip install bitcoin-python
# -----------------------------------------------------------------------------

import bitcoinrpc

# -----------------------------------------------------------------------------
# json api call library (exchange api)
# -----------------------------------------------------------------------------

import urllib2
import json

# -----------------------------------------------------------------------------
# for festival tts
# -----------------------------------------------------------------------------

import subprocess

# -----------------------------------------------------------------------------
# configuration initialization
# -----------------------------------------------------------------------------

config  = ConfigParser.RawConfigParser();
config.read('defaults.cfg');

sname   = config.get('Default','sname');
debug   = config.getboolean('Default','debug');
lname   = config.get('Default','lname');
lsize   = config.getint('Default','lsize');

btcuser = config.get('Client','btcuser');
btcpass = config.get('Client','btcpass');
btchost = config.get('Client','btchost');
btcport = config.getint('Client','btcport');

exname  = config.get('Exchange','exname');
exurl   = config.get('Exchange','exurl');
pfld    = config.get('Exchange','pfld');
pvar    = config.getfloat('Exchange','pvar');
poll    = config.getfloat('Exchange','poll');

lastex  = '0.00';
lastbal = '0.00';

# -----------------------------------------------------------------------------
# templates
# -----------------------------------------------------------------------------

from string import Template;

plog         = Template('$pnow: Old: $oprice New: $nprice BTC: $btc Value: $bval');

sbitmsg      = Template('You have $btc bitcoins, which are worth $bval cents');
smktmsg      = Template(exname+'\'s market price is $nprice cents');
sdeltamsg    = Template(exname+'\'s market price has $mdelta from $oprice cents to $nprice cents');

from time import gmtime, strftime

# -----------------------------------------------------------------------------
# logging macro. limit filesize to 1MB
# -----------------------------------------------------------------------------

def log(phrase):
    old_stdout      = sys.stdout;
    if(os.path.isfile(lname)):
        if(os.path.getsize(lname) >= lsize):
            say('Max filesize reached. Creating new file.');
            log_file    = open(lname,"w");
            sys.stdout  = log_file;
            print '# ----------------------------------------------------------------------------- #';
        else:
            log_file    = open(lname,"a");
            sys.stdout  = log_file;
    else:
        log_file    = open(lname,"w");
        sys.stdout  = log_file;
        print '# ----------------------------------------------------------------------------- #';
    print phrase;
    sys.stdout = old_stdout;
    log_file.close();

# -----------------------------------------------------------------------------
# macros to make code cleaner
# -----------------------------------------------------------------------------

def say(phrase):
    subprocess.call('echo "'+phrase.replace('00 cents','00')+'" | festival --tts', shell=True);

def talk(delta,price,btcbal):

    now = strftime("%Y-%m-%d %H:%M:%S", time.localtime());

    if(delta != ''):
        say(sdeltamsg.substitute(mdelta=delta,oprice='\$'+lastex,nprice='\$'+price));
    else :
        say(smktmsg.substitute(nprice='\$'+price));

    if(client):
        btcval  = str("%.2f" % round((float(price) * float(btcbal)),2));
        say(sbitmsg.substitute(btc=btcbal,bval='\$'+btcval));
        if(debug):log(plog.substitute(pnow=now,oprice='$'+lastex,nprice='$'+price,btc=btcbal,bval='$'+btcval));
    else:
        if(debug):log(plog.substitute(pnow=now,oprice='$'+lastex,nprice='$'+price));

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

say('Hello!');
say(sname+' started.');

# -----------------------------------------------------------------------------
# polling loop
# -----------------------------------------------------------------------------

while True:

  global client;

  try:

    jsonurl = urllib2.urlopen(exurl);
    data = json.loads(jsonurl.read());
    btcprice =  data[pfld];

    try:
        conn = bitcoinrpc.connect_to_remote(btcuser, btcpass, host=btchost, port=btcport)
        btcbalance = str(conn.getbalance());
        client = True;
    except (Exception):
        alert('No bitcoin client found.');
        client = False;

# -----------------------------------------------------------------------------
# check reporting status (little/no change, stay silent)
# -----------------------------------------------------------------------------

    if (client and (btcbalance != lastbal)) :
        talk('',btcprice,btcbalance);
        lastbal = btcbalance;
    elif (float(btcprice) >= float(lastex) + float(pvar)) :
        talk('increased',btcprice,btcbalance);
        lastex  = btcprice;
    elif (float(btcprice) <= float(lastex) - float(pvar)) :
        talk('decreased',btcprice,btcbalance);
        lastex  = btcprice;

# -----------------------------------------------------------------------------
# poll once every 5 minutes
# -----------------------------------------------------------------------------

    time.sleep(poll);

# -----------------------------------------------------------------------------
# site down or slow response. check again in 30 seconds
# -----------------------------------------------------------------------------

  except (urllib2.URLError):
    time.sleep(30);
    continue;

# -----------------------------------------------------------------------------
# ctrl-c halts script
# -----------------------------------------------------------------------------

  except (KeyboardInterrupt, SystemExit):
    break;

# -----------------------------------------------------------------------------
# The End
# -----------------------------------------------------------------------------

log('# ----------------------------------------------------------------------------- #');
say(sname+' halted. Good-bye!');
