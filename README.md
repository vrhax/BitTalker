BitTalker
=========

Raspberry PI talking bitcoin ticker

This app uses festival, and polls the current Bitstamp price (once, every 61s, to ensure it does not exceed their 600/10m polling rule), as well as computing the BTC value stored in a bitcoin-qt wallet which is running on a separate computer on the network. Notably, I didn't want it jabbering away every time the price changed. As such, it is designed to only speak based upon a user designated variance.

For example, only talk when the price has changed, up or down, by $5.00.

In addition to talking, it will print to a log. Though, in general, outside of debugging, and to keep storage requirements to a minimum, it is better to set the debug flag to 'False'.

And finally, this first pass example is somewhat of a kludge, in that it is my first attempt at writing a python script. So, at this point, it reflects USD only. For example, since I could  not figure out how to set up the tokens so that festival would correctly speak dollars, I kludged a string replace. So, if you want it to speak in a different currency, you will need to modify the dollar bit.
