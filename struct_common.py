import struct
def u8(file):
    return struct.unpack("B", file.read(1))[0]
 
def u16(file):
    return struct.unpack("<H", file.read(2))[0]
 
def u32(file):
    return struct.unpack("<I", file.read(4))[0]

def s32(file):
    return struct.unpack("<i", file.read(4))[0]

def w32(file,val):
    file.write(struct.pack("<I", val))

def ws32(file,val):
    file.write(struct.pack("<i", val))

def w16(file,val):
    file.write(struct.pack("<H", val))

def ws16(file,val):
    file.write(struct.pack("<h", val))

def w8(file,val):
    file.write(struct.pack("B", val))

def ws8(file,val):
    file.write(struct.pack("b", val))

def wstr(file,val):
    file.write(struct.pack("s", val))