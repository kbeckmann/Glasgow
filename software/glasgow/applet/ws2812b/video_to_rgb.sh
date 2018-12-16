#!/bin/bash

echo "$#"

if [ "$#" -ne 2 ]; then
    echo "Usage $0 <input.mp4> <output.rgb>"
    echo "Converts and scales video or gif to 144x8 raw rgb data."
    echo "Note! output must have .rgb as extension."
    exit 1
fi

width=$(ffprobe -v error -show_entries stream=width -of default=noprint_wrappers=1 "$1" | grep width -m 1)
width=${width#*=}
height=$(ffprobe -v error -show_entries stream=height -of default=noprint_wrappers=1 "$1" | grep height -m 1)
height=${height#*=}

echo $width
echo $height

crop_height=$(( 8 * (width / 144) ))

ffmpeg -i "$1" -vf "crop=$width:$crop_height,scale=144:8" -vcodec rawvideo -pix_fmt rgb24 "$2"
