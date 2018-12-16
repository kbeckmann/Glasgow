import colorsys
import struct
import math
import random

PIXELS = 144 * 4

# interleaved = 1
interleaved = 2
# interleaved = 4
# interleaved = 8

f = open("test_{}.bin".format(interleaved), "wb")

for n in range(1000):
    for x in range(PIXELS):
        # This way we get a half "rainbow", easy to find breaks/seams
        # hue = float(x + n/10.) / PIXELS / 2
        hue = (float(n) / 100 + float(x) / PIXELS )

        r, g, b = colorsys.hsv_to_rgb(
                hue,
                1,
                16)
        
        r = int(r)
        g = int(g)
        b = int(b)
#        print(r, g, b)
        # r = random.randint(0, 16)
        # g = random.randint(0, 16)
        # b = random.randint(0, 16)
        # r = 127 if n % 2 == 0 else 0
        # g = 127 if n % 2 == 0 else 0
        # b = 127 if n % 2 == 0 else 0

        if interleaved == 2:
            data1 = bytearray(struct.pack("BBB", g, r, b))
            data2 = bytearray(struct.pack("BBB", g, r, b))
            for i in range(len(data1)):
                byte1 = data1[i]
                byte2 = data2[i]
                cur = 0
                for j in range(8):
                    cur |= (byte1 & (2**j)) << (j + 0)
                    cur |= (byte2 & (2**j)) << (j + 1)
                f.write(struct.pack(">H", cur))
            #     print(hex(cur))
            #     print(bin(cur))
            # quit()
        elif interleaved == 4:
            data1 = struct.pack("BBB", r, g, b)
            data2 = struct.pack("BBB", r, 0, 0) # intentionally wrong
            data3 = struct.pack("BBB", 0, g, 0) # intentionally wrong
            data4 = struct.pack("BBB", 0, 0, b) # intentionally wrong
            for i in range(len(data1)):
                cur = 0
                byte1 = ord(data1[i])
                byte2 = ord(data2[i])
                byte3 = ord(data3[i])
                byte4 = ord(data4[i])
                for j in range(8):
                    cur |= (byte1 & (2**j)) << (j * 3 + 0)
                    cur |= (byte2 & (2**j)) << (j * 3 + 1)
                    cur |= (byte3 & (2**j)) << (j * 3 + 2)
                    cur |= (byte4 & (2**j)) << (j * 3 + 3)
                f.write(struct.pack(">L", cur))
        elif interleaved == 8:
            data1 = struct.pack("BBB", r, g, b)
            data2 = struct.pack("BBB", r, 0, 0) # intentionally wrong
            data3 = struct.pack("BBB", 0, g, 0) # intentionally wrong
            data4 = struct.pack("BBB", 0, 0, b) # intentionally wrong
            data5 = struct.pack("BBB", 0, g, b) # intentionally wrong
            data6 = struct.pack("BBB", r, g, 0) # intentionally wrong
            data7 = struct.pack("BBB", r, 0, b) # intentionally wrong
            data8 = struct.pack("BBB", 0, g, b) # intentionally wrong
            for i in range(len(data1)):
                cur = 0
                byte1 = ord(data1[i])
                byte2 = ord(data2[i])
                byte3 = ord(data3[i])
                byte4 = ord(data4[i])
                byte5 = ord(data5[i])
                byte6 = ord(data6[i])
                byte7 = ord(data7[i])
                byte8 = ord(data8[i])
                for j in range(8):
                    cur |= (byte1 & (2**j)) << (j * 7 + 0)
                    cur |= (byte2 & (2**j)) << (j * 7 + 1)
                    cur |= (byte3 & (2**j)) << (j * 7 + 2)
                    cur |= (byte4 & (2**j)) << (j * 7 + 3)
                    cur |= (byte5 & (2**j)) << (j * 7 + 4)
                    cur |= (byte6 & (2**j)) << (j * 7 + 5)
                    cur |= (byte7 & (2**j)) << (j * 7 + 6)
                    cur |= (byte8 & (2**j)) << (j * 7 + 7)
                f.write(struct.pack(">Q", cur))
        else:
            # No interleaving
            f.write(struct.pack("BBB", g, r, b))

f.close()
