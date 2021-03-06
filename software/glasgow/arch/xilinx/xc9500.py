# Ref: https://www.xilinx.com/member/forms/download/sim-model-eval-license-xef.html?filename=xc9500xl.zip
# Ref: reverse engineering by whitequark

from bitarray import bitarray

from ...support.bits import *


__all__ = [
    # IR
    "IR_EXTEST", "IR_SAMPLE", "IR_INTEST", "IR_FBLANK", "IR_ISPEN", "IR_ISPENC",
    "IR_FPGM", "IR_FPGMI", "IR_FERASE", "IR_FBULK", "IR_FVFY", "IR_FVFYI", "IR_ISPEX",
    "IR_CLAMP", "IR_HIGHZ", "IR_USERCODE", "IR_IDCODE", "IR_BYPASS",
    # DR
    "DR_ISDATA", "DR_ISADDRESS", "DR_ISCONFIGURATION",
]


IR_EXTEST   = bitarray("00000000", endian="little") # BOUNDARY[..]
IR_SAMPLE   = bitarray("10000000", endian="little") # BOUNDARY[..]
IR_INTEST   = bitarray("01000000", endian="little") # BOUNDARY[..]
IR_FBLANK   = bitarray("10100111", endian="little") # ISADDRESS[18]
IR_ISPEN    = bitarray("00010111", endian="little") # ISPENABLE[6]
IR_ISPENC   = bitarray("10010111", endian="little") # ISPENABLE[6]
IR_FPGM     = bitarray("01010111", endian="little") # ISCONFIGURATION[50]
IR_FPGMI    = bitarray("11010111", endian="little") # ISDATA[34]
IR_FERASE   = bitarray("00110111", endian="little") # ISADDRESS[18]
IR_FBULK    = bitarray("10110111", endian="little") # ISADDRESS[18]
IR_FVFY     = bitarray("01110111", endian="little") # ISCONFIGURATION[50]
IR_FVFYI    = bitarray("11110111", endian="little") # ISDATA[34]
IR_ISPEX    = bitarray("00001111", endian="little") # BYPASS[1]
IR_CLAMP    = bitarray("01011111", endian="little") # BYPASS[1]
IR_HIGHZ    = bitarray("00111111", endian="little") # BYPASS[1]
IR_USERCODE = bitarray("10111111", endian="little") # USERCODE[32]
IR_IDCODE   = bitarray("01111111", endian="little") # IDCODE[32]
IR_BYPASS   = bitarray("11111111", endian="little") # BYPASS[1]


DR_ISDATA = Bitfield("DR_ISDATA", 5, [
    ("valid",    1),
    ("strobe",   1),
    ("data",    32),
])

DR_ISADDRESS = Bitfield("DR_ISADDRESS", 3, [
    ("valid",    1),
    ("strobe",   1),
    ("address", 16),
])

DR_ISCONFIGURATION = Bitfield("DR_ISCONFIGURATION", 7, [
    ("valid",    1),
    ("strobe",   1),
    ("data",    32),
    ("address", 16),
])
