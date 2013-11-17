BitTalker
=========

Raspberry PI talking bitcoin ticker

This app uses festival, and polls the current Bitstamp price (once, every 61s, to ensure it does not exceed their 600/10m polling rule), as well as computing the BTC value stored in a bitcoin-qt wallet which is running on a separate computer on the network. Notably, I didn't want it jabbering away every time the price changed. As such, it is designed to only speak based upon a user designed variance.

For example, only talk when the price has changed by $5.00.

In addition to talking, it will print to a log by setting the debug flag to true. In general, outside of debugging, and to keep storage requirements to a minimum, it is better to set the debug flag to false.

And finally, this reflects USD. So, if you want to display a different currency, you will need to modify the output. 

With that said, I thought I'd share the code.

Oh and. If you find this to be the least bit useful, bitcoin tips are always welcomed. They can be sent to: 1DzHAT7jbxJAAGoJ6KjmfzDHWhYKaMhrbJ
