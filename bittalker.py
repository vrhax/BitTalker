# -----------------------------------------------------------------------------
# Created by vrhax on November 16, 2013
# -----------------------------------------------------------------------------
# USAGE: python bittalker.py variance debug
#
# example: python bittalker.py 5.0 True
#
#
# -----------------------------------------------------------------------------
# client info
# be sure to add/update the following lines in your bitcoin.conf file
#
# server=1
# daemon=1
# rpcuser=RPCUSER           <= remote procedure call username
# rpcpassword=RPCPASSWORD   <= remote procedure call password
# rpcallowip=127.0.0.1      <= localhost
# rpcallowip=RPIHOST        <= raspberry pi ip address
# rpcport=RCPPORT           <= usually 8332
# -----------------------------------------------------------------------------

btcuser = 'RPCUSER';
btcpass = 'RPCPASSWORD';
btchost = 'RPCHOST';
btcport = RPCPORT;

# -----------------------------------------------------------------------------
# exchange info
# -----------------------------------------------------------------------------

exname  = "BitStamp";
exurl   = "https://www.bitstamp.net/api/ticker/";

# -----------------------------------------------------------------------------
# imports time library (for while loop sleep)
# -----------------------------------------------------------------------------

import sys
import time

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
# templates
# -----------------------------------------------------------------------------

from string import Template;

plog         = Template('$pnow: Old: $oprice New: $nprice BTC: $btc Value: $bval');

sbitmsg      = Template('You have $btc bitcoins, which are worth $bval cents');
smktmsg      = Template(exname+'\'s market price is $nprice cents');
sdeltamsg    = Template(exname+'\'s market price has $mdelta from $oprice cents to $nprice cents');

from time import gmtime, strftime

# -----------------------------------------------------------------------------
# macros to make code cleaner
# -----------------------------------------------------------------------------

def log(phrase):
    old_stdout  = sys.stdout;
    log_file    = open("bittalk.log","a");
    sys.stdout  = log_file;
    print phrase;
    sys.stdout = old_stdout;
    log_file.close();

def newlog():
    old_stdout  = sys.stdout;
    log_file    = open("bittalk.log","w");
    sys.stdout  = log_file;
    sys.stdout = old_stdout;
    log_file.close();
    say(sname+' started. Hello!');
    log('# ----------------------------------------------------------------------------- #');

def say(phrase):
    subprocess.call('echo "'+phrase+'" | festival --tts', shell=True);

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

total   = len(sys.argv);
cmdargs = str(sys.argv);

sname   = 'Bit Talker';

if(total == 3):
    exvar   = str(sys.argv[1]);
    debug   = str(sys.argv[2]);
elif(total == 2):
    exvar   = str(sys.argv[1]);
    debug   = True;
else:
    exvar   = '1.0';
    debug   = True;

# -----------------------------------------------------------------------------
# polling loop
# -----------------------------------------------------------------------------

global lastex, lastbal;

lastex  = '0.0';
lastbal = '0.0';

newlog();

while True:

  global client;

  try:

    jsonurl = urllib2.urlopen(exurl);
    data = json.loads(jsonurl.read());
    btcprice =  data['last'];

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
    elif (float(btcprice) >= float(lastex) + float(exvar)) :
        talk('increased',btcprice,btcbalance);
        lastex  = btcprice;
    elif (float(btcprice) <= float(lastex) - float(exvar)) :
        talk('decreased',btcprice,btcbalance);
        lastex  = btcprice;

# -----------------------------------------------------------------------------
# poll once every 5 minutes
# -----------------------------------------------------------------------------

    time.sleep(61);

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
