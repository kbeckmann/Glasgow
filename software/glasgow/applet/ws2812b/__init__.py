import math
import argparse
import logging
import struct
import time
import math
from migen import *
from migen.genlib.fsm import *
import binascii
import asyncio

from .. import *

#        ________________             ____
#       |       |        |           |
# ______|       |________|___________|
#       |       |        |           |
# [ns]  0      400      850        1250
#              "0"      "1"         next bit

class WS2812BSubtarget(Module):
    def __init__(self, pads, out_fifo, sys_clk_freq):
        oe = Signal()
        self.comb += [
            pads.data_t.oe.eq(oe),
        ]

        reset_cyc     = math.ceil(1e-6 * sys_clk_freq)
        t0_hi         = math.ceil(400e-9 * sys_clk_freq)
        t1_hi         = math.ceil(400e-9 * sys_clk_freq) # Time to wait after waiting t0_hi
        t_lo          = math.ceil(750e-9 * sys_clk_freq) # Time to wait after waiting t0_hi + t1_hi
        t_one_ms      = math.ceil(1e-3 * sys_clk_freq)
        bitno         = Signal(3)
        byteno        = Signal(16)
        shreg         = Signal(8)
        header_byte   = Signal(max=8)
        num_outputs   = Signal(max=16)
        timer         = Signal(max=math.ceil(sys_clk_freq))
        refresh_delay = Signal(max=math.ceil(sys_clk_freq))

        self.submodules.fsm = FSM(reset_state="IDLE")
        self.fsm.act("IDLE",
            If(out_fifo.readable,
                NextValue(oe, 1),
                NextValue(timer, 0),
                NextValue(header_byte, 0),
                NextState("CHUNK")
            ).Else(
                NextValue(oe, 0),
            )
        )
        self.fsm.act("CHUNK",
            If(timer == 0,
                If(out_fifo.readable,
                    out_fifo.re.eq(1),
                    If(out_fifo.dout == 0,
                        NextState("IDLE")
                    ).Else(
                        If(header_byte == 0,
                            NextValue(byteno[8:16], out_fifo.dout),
                            NextValue(header_byte, 1),
                        ).Elif(header_byte == 1,
                            NextValue(byteno[0:8], out_fifo.dout),
                            NextValue(header_byte, 2),
                        ).Elif(header_byte == 2,
                            NextValue(refresh_delay, t_one_ms * out_fifo.dout),
                            NextValue(header_byte, 3),
                        ).Elif(header_byte == 3,
                            NextValue(num_outputs, out_fifo.dout),
                            NextValue(header_byte, 0),
                            NextState("LOAD")
                        )
                    )
                )
            ).Else(
                NextValue(timer, timer - 1)
            )
        )
        self.fsm.act("LOAD",
            If(out_fifo.readable,
                out_fifo.re.eq(1),
                If(num_outputs == 1,
                    NextValue(bitno, 7),
                ).Elif(num_outputs == 2,
                    NextValue(bitno, 3),
                ).Elif(num_outputs == 4,
                    NextValue(bitno, 1),
                ).Elif(num_outputs == 8,
                    NextValue(bitno, 0),
                ),
                NextValue(byteno, byteno - 1),
                NextValue(shreg, out_fifo.dout),
                NextState("SETUP"),
            )
        )
        self.fsm.act("SETUP",
            NextValue(pads.data_t.o, ~0),
            NextState("HOLD_HI0"),
            NextValue(timer, t0_hi),
        )
        self.fsm.act("HOLD_HI0",
            If(timer == 0,
                If(num_outputs == 1,
                    NextValue(pads.data_t.o, shreg[7:]),
                ).Elif(num_outputs == 2,
                    NextValue(pads.data_t.o, shreg[6:]),
                ).Elif(num_outputs == 4,
                    NextValue(pads.data_t.o, shreg[4:]),
                ).Elif(num_outputs == 8,
                    NextValue(pads.data_t.o, shreg),
                ),
                NextValue(timer, t1_hi),
                NextState("HOLD_HI1"),
            ).Else(
                NextValue(timer, timer - 1),
            )
        )
        self.fsm.act("HOLD_HI1",
            If(timer == 0,
                NextValue(pads.data_t.o, 0),
                NextValue(timer, t_lo),
                NextState("HOLD_LO"),
            ).Else(
                NextValue(timer, timer - 1),
            )
        )
        self.fsm.act("HOLD_LO",
            If(timer == 0,
                NextState("NEXTBIT")
            ).Else(
                NextValue(timer, timer - 1),
            )
        )
        self.fsm.act("NEXTBIT",
            If((bitno == 0) & (byteno == 0),
                NextState("CHUNK"),
                NextValue(timer, refresh_delay),
            ).Elif(bitno == 0,
                NextState("LOAD"),
            ).Else(
                NextValue(bitno, bitno - 1),
                NextValue(shreg, shreg << num_outputs),
                NextState("SETUP"),
            )
        )


class WS2812BApplet(GlasgowApplet, name="ws2812b"):
    logger = logging.getLogger(__name__)
    help = "ws2812b pixel party"
    description = """
    Push pixels to a ws2812 LED-strip
    """

    @classmethod
    def add_build_arguments(cls, parser, access):
        access.add_build_arguments(parser)
        access.add_pin_set_argument(parser, "data", width=8, default=True)

    def build(self, target, args):
        self.mux_interface = iface = target.multiplexer.claim_interface(self, args)
        iface.add_subtarget(WS2812BSubtarget(
            pads=iface.get_pads(args, pin_sets=("data",)),
            out_fifo=iface.get_out_fifo(),
            sys_clk_freq=target.sys_clk_freq,
        ))

    @classmethod
    def add_run_arguments(cls, parser, access):
        access.add_run_arguments(parser)

        parser.add_argument(
            "-p", "--pixels", metavar="PIXELS", type=int, default=144,
            help="set number of pixels in the LED strip (default: %(default))")
        parser.add_argument(
            "-o", "--outputs", metavar="OUTPUTS", type=int, default=2,
            help="set number of output pins and interleaved pixels to use. Valid: 1, 2, 4 (default: %(default))")
        parser.add_argument(
            "-d", "--delay", metavar="DELAY", type=int, default=10,
            help="ms delay between pixel blits (default: %(default)ms)")
        parser.add_argument(
            "pixelstream", metavar="PIXELSTREAM", type=argparse.FileType("rb"),
            help="pixelstream file")

    async def run(self, device, args):
        iface = await device.demultiplexer.claim_interface(self, self.mux_interface, args)
        pixelstream = args.pixelstream.read()

        # Infinite loop
        for i in range(3):
            print("Loop")
            pixelbuf = memoryview(pixelstream)
            i = 0
            t0 = time.time()
            num_bytes = 0
            offset = 0
            while offset < len(pixelbuf):
                i += 1
                tdiff = time.time() - t0
                if tdiff > 0.5:
                    print("{} bytes/s; {} fps".format(round(num_bytes / tdiff), round(2.0 * i / tdiff)))
                    i = num_bytes = 0
                    t0 = time.time()
                chunk = pixelbuf[offset:offset + args.pixels * 3 * args.outputs]
                num_bytes += len(chunk)
                offset += len(chunk)
                await iface.write(struct.pack(">HBB", len(chunk), args.delay, args.outputs) + chunk)
                await iface.flush()
                # await asyncio.sleep(0.01)
            # for i in range(1000):
            #     chunk = b"\x00" * args.pixels * 3 * args.outputs
            #     await iface.write(struct.pack(">HBB", len(chunk), args.delay, args.outputs) + chunk)
            #     await iface.flush()

        await iface.write([0])
        await iface.flush()

# -------------------------------------------------------------------------------------------------

class WS2812BAppletTestCase(GlasgowAppletTestCase, applet=WS2812BApplet):
    @synthesis_test
    def test_build(self):
        self.assertBuilds()
