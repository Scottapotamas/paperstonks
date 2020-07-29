#!/usr/bin/env python

import argparse
from PIL import Image
from inky import InkyWHAT

print("""Inky wHAT: Dither image modified as a prep for giving a eInk gift

Dithered display of a stonks meme on the eInk display
""")

colour = "red"
img_file = "./stonks.jpg"

inky_display = InkyWHAT(colour)
inky_display.set_border(inky_display.WHITE)

img = Image.open(img_file)
w, h = img.size

# Rescale image
h_new = 300
w_new = int((float(w) / h) * h_new)
w_cropped = 400
img = img.resize((w_new, h_new), resample=Image.LANCZOS)

# Crop to 400px width
x0 = (w_new - w_cropped) / 2
x1 = x0 + w_cropped
y0 = 0
y1 = h_new
img = img.crop((x0, y0, x1, y1))

# Convert the image to use a white / black / red colour palette

pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

img = img.convert("RGB").quantize(palette=pal_img)

# Render

inky_display.set_image(img)
inky_display.show()
