# PaperStonks
Self-contained quick project for a desk stock summary page using a [Pimoroni InkyWhat eInk display](https://shop.pimoroni.com/products/inky-what?variant=13590497624147) and [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/). I got the eInk capable of drawing red.

Intended as a gift, so the project is intended to be done reasonably quickly and configuration after 'deployment' should be possible remotely and with minimal fuss.

# Setup 

Pretty standard setup:

- Install latest minimal [Raspbian](https://www.raspberrypi.org/downloads/raspberry-pi-os/) and flash to a SD card with [Etcher](https://www.balena.io/etcher/). 

- Setup the image with [SSH enabled, and add WiFi](https://desertbot.io/blog/headless-pi-zero-w-wifi-setup-windows) credentials.

- Configure a new hostname `stockticker.local` in this case.
- Set a new password, etc.
- Run `sudo apt update && sudo apt upgrade`.

- I used Pimoroni's quick setup `curl https://get.pimoroni.com/inky | bash` one-liner to get _that side_ setup (its mostly doing things like installing `pip`, `numpy` and configuring SPI mode on the Pi). It takes a _very_ long time to run.
- A reboot is required at this point.
- Clone this repo into the home directory `git clone https://github.com/Scottapotamas/paperstonks.git`


Before giving the display as a gift, setup the dispay to have a nice 'welcome' image. Run the `prep_display` program with `python gift.py` to draw a dithered image.

# Usage

- Provide power and allow the system to boot.

- The eInk display should display content when ready (system assumes a valid wifi/network connection is present).

- Pulls stock info from Yahoo finance and formats the output for display on the eInk.



# Updates

The Pi will pull this git repo periodically.
