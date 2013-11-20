# -----------------------------------------------------------------------------
# This code is written by VRHax.
# It is in the public domain, so you can do what you like with it
# but a link to https://github.com/vrhax/BitTalker would be nice.
#
# It works on the Raspberry Pi computer with the standard Debian Wheezy OS and
# the festival tts module
# -----------------------------------------------------------------------------
#
# USAGE: python bittalker.py
#
# -----------------------------------------------------------------------------
# import system libraries
# -----------------------------------------------------------------------------

import ConfigParser, os, sys, time

# -----------------------------------------------------------------------------
# import json api call library (exchange api)
# -----------------------------------------------------------------------------

import urllib2, httplib, json

# -----------------------------------------------------------------------------
# import bitcoin wallet connection library
#
#   NB: must first install bitcoin-python (as follows):
#
#       sudo apt-get install python-setuptools
#       sudo easy_install pip
#       sudo pip install bitcoin-python
# -----------------------------------------------------------------------------

import bitcoinrpc

# -----------------------------------------------------------------------------
# import subprocess library for calling festival tts
#
#   NB: must first install festival tts (as follows):
#
#       sudo apt-get update
#       sudo apt-get upgrade
#       sudo apt-get install alsa-utils
#
#       sudo nano /etc/modules
#
#         change snd-bcm2835 to snd_bcm2835
#
#       sudo apt-get install mplayer
#
#       sudo nano /etc/mplayer/mplayer.conf
#
#         add nolirc=yes
#
#       sudo apt-get install festival
#
# -----------------------------------------------------------------------------

import subprocess

# -----------------------------------------------------------------------------
# configuration initialization
# -----------------------------------------------------------------------------

config  = ConfigParser.RawConfigParser();
config.read('defaults.cfg');

sname   = config.get('Default','sname');
lname   = config.get('Default','lname');
lsize   = config.getint('Default','lsize');
debug   = config.getboolean('Default','debug');

btcuser = config.get('Client','btcuser');
btcpass = config.get('Client','btcpass');
btchost = config.get('Client','btchost');
btcport = config.getint('Client','btcport');

exname  = config.get('Exchange','exname');
exurl   = config.get(exname,'exurl');
pfld    = config.get(exname,'pfld');
pvar    = config.getfloat('Exchange','pvar');
poll    = config.getfloat('Exchange','poll');

lastex  = '000.00';
lastbal = '000.00';

# -----------------------------------------------------------------------------
# templates
# -----------------------------------------------------------------------------

from string import Template;

plog1        = Template('$pnow: Old: $oprice New: $nprice BTC: $btc Value: $bval');
plog2        = Template('$pnow: Old: $oprice New: $nprice');

sbitmsg      = Template('You have $btc bitcoins, which are worth $bval cents');
smktmsg      = Template(exname+'\'s market price is $nprice cents');
sdeltamsg    = Template(exname+'\'s market price has $mdelta from $oprice cents to $nprice cents');

from time import gmtime, strftime

# -----------------------------------------------------------------------------
# logging macro.
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
# speech macros
# -----------------------------------------------------------------------------

def say(phrase):
    subprocess.call('echo "'+phrase.replace('00 cents','00')+'" | festival --tts', shell=True);

def talk(delta,price,btcbal):

    global client;

    now = strftime("%Y-%m-%d %H:%M:%S", time.localtime());

    if(delta != ''):
        say(sdeltamsg.substitute(mdelta=delta,oprice='\$'+lastex,nprice='\$'+price));
    else :
        say(smktmsg.substitute(nprice='\$'+price));

    if(client):
        btcval  = str("%.2f" % round((float(price) * float(btcbal)),2));
        say(sbitmsg.substitute(btc=btcbal,bval='\$'+btcval));
        if(debug):log(plog1.substitute(pnow=now,oprice='$'+lastex,nprice='$'+price,btc=btcbal,bval='$'+btcval));
    else:
        if(debug):log(plog2.substitute(pnow=now,oprice='$'+lastex,nprice='$'+price));

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

say('Hello!');
say(sname+' started.');
say(exname+' polling set to '+str(poll)+' seconds.');

# -----------------------------------------------------------------------------
# polling loop
# -----------------------------------------------------------------------------

while True:

  global client;

  try:

# -----------------------------------------------------------------------------
# get bitcoin client data
# -----------------------------------------------------------------------------

    try:
        conn = bitcoinrpc.connect_to_remote(btcuser, btcpass, host=btchost, port=btcport)
        btcbalance = str(conn.getbalance());
        client = True;

# -----------------------------------------------------------------------------
# no client running
# -----------------------------------------------------------------------------

    except (Exception):
        btcbalance = '0.0';
        say('No bitcoin client found.');
        say('Continuing.');
        client = False;

# -----------------------------------------------------------------------------
# get market data
# -----------------------------------------------------------------------------

    try:
        jsonurl = urllib2.urlopen(exurl);
        data = json.loads(jsonurl.read());
        btcprice =  data[pfld];

# -----------------------------------------------------------------------------
# site down or slow response. check again in 30 seconds
# -----------------------------------------------------------------------------

    except (urllib2.HTTPError):
        say(exname+' unaccessible. Rechecking in 1 minute');
        time.sleep(60);
        continue;

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
# poll once every n seconds
# -----------------------------------------------------------------------------

    time.sleep(poll);

# -----------------------------------------------------------------------------
# ctrl-c halts script
# -----------------------------------------------------------------------------

  except (KeyboardInterrupt, SystemExit):
    break;

# -----------------------------------------------------------------------------
# The End. Clean exit.
# -----------------------------------------------------------------------------

say(sname+' halted. Good-bye!');
exit(0);
