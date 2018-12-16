#!/bin/env python3

import sys
import random
import os
import subprocess
from PIL import Image

WIDTH = 144
HEIGHT = 8

if len(sys.argv) != 3:
    print("Usage {} <input.jpg> <output.rgb>".format(sys.argv[0]))
    print("Creates a vertically scrolling image in raw rgb data.")
    print("Note! output must have .rgb as extension.")
    quit()

im = Image.open(sys.argv[1])
print(im.format, im.size, im.mode)

xsize, ysize = im.size

xout = 144
yout = int(ysize / (xsize / 144.))

im = im.resize((xout, yout))

i = 0
subprocess.call("rm -rf temp123", shell=True)
os.mkdir("temp123")
for y in range(-8, yout+8):
    part = im.crop((0, y, xout, y + 8))
    part.save("temp123/temp_%05d.png" % i)
    i += 1

#subprocess.call("ffmpeg -r 60 -i temp123/temp_%05d.png {}".format(sys.argv[2]), shell=True)
subprocess.call("ffmpeg -r 60 -i temp123/temp_%05d.png -vcodec rawvideo -pix_fmt rgb24 {}".format(sys.argv[2]), shell=True)
subprocess.call("rm -rf temp123", shell=True)

