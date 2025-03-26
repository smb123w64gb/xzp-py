from struct_common import *

def xwvPreloadSize(f):
    f.seek(0)
    headersize = u32(f)
    f.seek(0x10)
    vdatSize = u16(f)
    return headersize+vdatSize
def xtfPreloadSize(f):
    f.seek(0x1C)
    preload = u16(f)
    return preload
#Todo, reaserch the VHV from BSP in HL2X