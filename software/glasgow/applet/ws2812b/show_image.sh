#!/bin/sh

set -e

rm -f temp.rgb
./glasgow/applet/ws2812b/image_to_scrolling_rgb.py "$1" "temp.rgb"
pypy glasgow/applet/ws2812b/gen_video.py 2 "temp.rgb" "temp.bin"
python3.6 -m glasgow.cli run ws2812b --port A -V 5 -o 2 -d 25 -p $((144 * 4)) "temp.bin"
