#!/bin/sh

set -e

rm -f temp.rgb
./glasgow/applet/ws2812b/video_to_rgb.sh "$1" "temp.rgb"
pypy glasgow/applet/ws2812b/gen_video.py 2 "temp.rgb" temp.bin
python3.6 -m glasgow.cli run ws2812b --port A -V 5 -o 2 -d 1 -p $((144 * 4)) temp.bin
