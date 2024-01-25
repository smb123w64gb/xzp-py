import struct,time
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

def xPad(f):
    f.write(bytes([0] * (( 512 - ( f.tell() % 512) ) % 512)))


def getstr(f, term=b'\0'):
    result = ""
    tmpChar = f.read(1).decode("ASCII")
    while ord(tmpChar) != 0:
        result += tmpChar
        tmpChar = f.read(1).decode("ASCII")
    return result

def rS(f,o):
    c = f.tell()
    f.seek(o)
    s = getstr(f)
    f.seek(c)
    return s

def rR(f,o,l):
    c = f.tell()
    f.seek(o)
    d = f.read(l)
    f.seek(c)
    return d
def xmwPreloadSize(f):
    f.seek(4)
    headersize = u32(f)
    f.seek(0x14)
    vdatSize = u16(f)
    return headersize+vdatSize

def CRCFilename(filename):
    hash = int(0xAAAAAAAA)
    for c in filename:
        if c == '/':
            c ='\\'
        else:
            c = c.lower()
        hash = 0xFFFFFFFF & int(hash * 33 + ord(c))
    return hash
class xZip(object):
    class xZipHeader_t(object):
        def __init__(self):
            self.Magic = 'piZx'# Valve Cast this to uint thus fliparu
            self.Version = 6
            self.PreloadDirectoryEntries = 0
            self.DirectoryEntries = 0
            self.PreloadBytes = 0
            self.HeaderLength = 0x24
            self.FilenameEntries = 0
            self.FilenameStringsOffset = 0
            self.FilenameStringsLength = 0
        def read(self,f):
            self.Magic = f.read(4)
            self.Version = u32(f)
            self.PreloadDirectoryEntries = u32(f)
            self.DirectoryEntries = u32(f)
            self.PreloadBytes = u32(f)
            self.HeaderLength = u32(f)
            self.FilenameEntries = u32(f)
            self.FilenameStringsOffset = u32(f)
            self.FilenameStringsLength = u32(f)
        def write(self,f):
            f.write(self.Magic)
            w32(f,self.PreloadDirectoryEntries)
            w32(f,self.Version)
            w32(f,self.DirectoryEntries)
            w32(f,self.PreloadBytes)
            w32(f,self.HeaderLength)
            w32(f,self.FilenameEntries)
            w32(f,self.FilenameStringsOffset)
            w32(f,self.FilenameStringsLength)
    class xZipDirectoryEntry_t(object):
        def __init__(self):
            self.FilenameCRC = 0
            self.Length = 0
            self.StoredOffset = 0
            self.Data = []
            self.Filename = ''
        def read(self,f):
            self.FilenameCRC = u32(f)
            self.Length = u32(f)
            self.StoredOffset = s32(f)
            self.OffsetOfOffset = 0
            self.Data = rR(f,self.StoredOffset,self.Length)
        def write_entry(self,f):
            w32(f,self.FilenameCRC)
            w32(f,self.Length)
            self.OffsetOfOffset = f.tell()
            w32(f,0)
        def write_data(self,f):
            off = f.tell()
            f.write(self.Data)
            ret = f.tell()
            f.seek(self.OffsetOfOffset)
            w32(off)
            f.seek(ret)
        def DirectoryEntrySortCompare(l,r):
            if(l.FilenameCRC < r.FilenameCRC):
                return -1
            elif(l.FilenameCRC > r.FilenameCRC):
                return 1
            
            if(l.Length < r.Length):
                return -1
            elif(l.Length > r.Length):
                return 1
            
            if(l.StoredOffset < r.StoredOffset):
                return -1
            elif(l.StoredOffset > r.StoredOffset):
                return 1
            
            return 0
        def DirectoryEntryFindCompare(l,r):
            if(l.FilenameCRC < r.FilenameCRC):
                return -1
            elif(l.FilenameCRC > r.FilenameCRC):
                return 1
    class xZipFilenameEntry_t(object):
        def __init__(self):
            self.FilenameCRC = 0
            self.FilenameOffset = 0
            self.TimeStamp = int(time.time())
            self.OffsetOfOffset = 0
            self.Filename = ''
        def read(self,f):
            self.FilenameCRC = u32(f)
            self.FilenameOffset = u32(f)
            self.TimeStamp = u32(f)
            self.Filename = rS(f,self.FilenameOffset)
        def write_entry(self,f):
            w32(f,self.FilenameCRC)
            self.OffsetOfOffset = f.tell()
            w32(f,0)
            w32(f,self.TimeStamp)
        def write_string(self,f):
            off = f.tell()
            f.write(self.Filename)
            ret = f.tell()
            f.seek(self.OffsetOfOffset)
            w32(f,off)
            f.seek(ret)
    class xZipFooter_t(object):
        def __init__(self):
            self.Size = 0
            self.Magic = 'tFzX' #Byteflipy
        def read(self,f):
            self.Size = u32(f)
            self.Magic = f.read(4)
        def write(self,f):
            #Ima be lazy
            w32(f,f.tell()+8)
            f.write(self.Magic)
    def __init__(self):
        self.Header = self.xZipHeader_t()
        self.pDirectoryEntries = []
        self.pPreloadDirectoryEntries = []
        self.nRegular2PreloadEntryMapping = []
        self.pFilenameEntries = []
        self.Footer = self.xZipFooter_t()       
    def read(self,f):
        self.Header.read(f)
        for a in range(self.Header.DirectoryEntries):
            self.pDirectoryEntries.append(self.xZipDirectoryEntry_t())
            self.pDirectoryEntries[a].read(f)
        #Preload Starts here
        for a in range(self.Header.PreloadDirectoryEntries):
            self.pPreloadDirectoryEntries.append(self.xZipDirectoryEntry_t())
            self.pPreloadDirectoryEntries[a].read(f)
        for a in range(self.Header.DirectoryEntries):
            self.nRegular2PreloadEntryMapping.append(u16(f))
        f.seek(self.Header.FilenameStringsOffset)
        for a in range(self.Header.DirectoryEntries):
            self.pFilenameEntries.append(self.xZipFilenameEntry_t())
            self.pFilenameEntries[a].read(f)
        f.seek(-8,2)
        self.Footer.read(f)
        for a in self.pDirectoryEntries:
            #[val for key, val in test_dict.items() if search_key in key]
            for b in self.pFilenameEntries:
                if b.FilenameCRC == a.FilenameCRC:
                    a.Filename = b.Filename
        for a in self.pPreloadDirectoryEntries:
            #[val for key, val in test_dict.items() if search_key in key]
            for b in self.pFilenameEntries:
                if b.FilenameCRC == a.FilenameCRC:
                    a.Filename = b.Filename
    def write(self,f):
        print("Not working")

'''
Header
RegLoading
 #Preloading starts from here
PreLoading
PreloadMapping #To Regular loading -1 is no preload
PreData #Mainly headers but textures get a Preload Texture 8x8
 #Preload Ends
BulkData
Strings
Footer
'''