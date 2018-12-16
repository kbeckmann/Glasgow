import colorsys
import struct
import math
import random
import sys

WIDTH = 144
HEIGHT = 8
PIXELS = WIDTH * HEIGHT

# interleaved = 1
# interleaved = 2

interleaved = int(sys.argv[1])

ARGB = 0 #todo

# Read ARGB data
data_in = bytearray(open(sys.argv[2], "rb").read())
f = open(sys.argv[3], "wb")

def rgbv_to_bytes(r, g, b, v):
    r = int(float(r) * v)
    g = int(float(g) * v)
    b = int(float(b) * v)
    return bytearray(struct.pack("BBB", g, r, b))

for frame in range(0, len(data_in) / 4 / PIXELS):
    for i in range(0, PIXELS / interleaved):
        if interleaved == 2:
            index = frame * PIXELS + i
            if (index % (WIDTH * 2) >= WIDTH):
                pass #todo remove
            else:
                offset = WIDTH - 1 + index % WIDTH
                start = index - index % WIDTH
                index = start + WIDTH - index % WIDTH - 1

            if ARGB:
                index *= 4
                r = int(data_in[index + 1])
                g = int(data_in[index + 2])
                b = int(data_in[index + 3])
                data1 = rgbv_to_bytes(r, g, b, 1)

                r = int(data_in[(index + 4 * PIXELS / 2) + 1])
                g = int(data_in[(index + 4 * PIXELS / 2) + 2])
                b = int(data_in[(index + 4 * PIXELS / 2) + 3])
                data2 = rgbv_to_bytes(r, g, b, 0.1)
            else:
                index *= 3
                r = int(data_in[index + 0])
                g = int(data_in[index + 1])
                b = int(data_in[index + 2])
                data1 = rgbv_to_bytes(r, g, b, 0.1)

                r = int(data_in[(index + 3 * (PIXELS / 2)) + 0])
                g = int(data_in[(index + 3 * (PIXELS / 2)) + 1])
                b = int(data_in[(index + 3 * (PIXELS / 2)) + 2])
                data2 = rgbv_to_bytes(r, g, b, 0.1)

            for i in range(len(data1)):
                byte1 = data1[i]
                byte2 = data2[i]
                cur = 0
                for j in range(8):
                    cur |= (byte1 & (2**j)) << (j + 0)
                    cur |= (byte2 & (2**j)) << (j + 1)
                f.write(struct.pack(">H", cur))
        else:
            index = frame * PIXELS + i
            if (index % (WIDTH * 2) >= WIDTH):
                pass #todo remove
            else:
                offset = WIDTH - 1 + index % WIDTH
                start = index - index % WIDTH
                index = start + WIDTH - index % WIDTH - 1

            # Align for ARGB
            if ARGB:
                index *= 4
                a = 255 - int(data_in[index + 0])
                r = int((data_in[index + 1] * a) / 255)
                g = int((data_in[index + 2] * a) / 255)
                b = int((data_in[index + 3] * a) / 255)
            else:
                index *= 3
                r = int(data_in[index + 0])
                g = int(data_in[index + 1])
                b = int(data_in[index + 2])

            data = rgbv_to_bytes(r, g, b, 0.1)
            f.write(data)

f.close()
