import time
from struct_common import *

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
            f.write(bytes(self.Magic,'utf-8'))
            w32(f,self.Version)
            w32(f,self.PreloadDirectoryEntries)
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

            #assisting value
            self.OffsetOfOffset = 0
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
            w32(f,off)
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
            f.write(bytes(self.Filename,'utf-8'))
            ret = f.tell() + 1
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
            try:
                f.write(bytes(self.Magic,'utf-8'))
            except:
                f.write(self.Magic)
    def __init__(self):
        self.Header = self.xZipHeader_t()
        self.pDirectoryEntries = []
        self.pPreloadDirectoryEntries = []
        self.nRegular2PreloadEntryMapping = []
        self.pFilenameEntries = {}
        self.Footer = self.xZipFooter_t()   
    def findkey(self,crc):
        for idx,obj in enumerate(self.pDirectoryEntries):
            if obj.FilenameCRC == crc:
                return idx
        return None
    def addFile(self,f,fn,preload=0):
        data = f.read()
        crcname = CRCFilename(fn)
        filename = self.xZipFilenameEntry_t()
        filename.FilenameCRC = crcname
        filename.Filename = fn
        dirent = self.xZipDirectoryEntry_t()
        dirent.FilenameCRC = crcname
        dirent.Data = data
        dirent.Length = len(data)
        dirent.Filename = fn
        self.pDirectoryEntries.append(dirent)
        self.pFilenameEntries[crcname] = filename
        if(preload):
            preloadent = self.xZipDirectoryEntry_t()
            preloadent.FilenameCRC = crcname
            preloadent.Data = data[:preload]
            preloadent.Length = preload
            preloadent.Filename = fn
            mapin = len(self.pPreloadDirectoryEntries)
            self.nRegular2PreloadEntryMapping.append(mapin)
            self.pPreloadDirectoryEntries.append(preloadent)
        else:
            self.nRegular2PreloadEntryMapping.append(0xFFFF)
    def delete(self,fn):
        crcname = CRCFilename(fn)
        entryIndex = self.findkey(crcname)
        if(entryIndex == None):
            raise "Filename not found"
        

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
            Fname = self.xZipFilenameEntry_t()
            Fname.read(f)
            self.pFilenameEntries[Fname.FilenameCRC] = Fname
        f.seek(-8,2)
        self.Footer.read(f)
        print("Most Read\nNow matching Filenames")
        for a in self.pDirectoryEntries:
            a.Filename = self.pFilenameEntries[a.FilenameCRC].Filename
        for a in self.pPreloadDirectoryEntries:
            a.Filename = self.pFilenameEntries[a.FilenameCRC].Filename
   
    def write(self,f):
        #Step one, we collect what we have as of entrys
        self.Header = self.xZipHeader_t()
        self.Header.PreloadDirectoryEntries = len(self.pPreloadDirectoryEntries)
        self.Header.DirectoryEntries = len(self.pDirectoryEntries)
        self.Header.FilenameEntries = len(self.pDirectoryEntries)

        f.seek(0x24)
        for a in self.pDirectoryEntries:
            a.write_entry(f)
        preloatstart = f.tell()
        for a in self.pPreloadDirectoryEntries:
            a.write_entry(f)
        for a in self.nRegular2PreloadEntryMapping:
            w16(f,a)
        for a in self.pPreloadDirectoryEntries:
            a.write_data(f)
        preloadsize = f.tell() - preloatstart
        self.Header.PreloadBytes = preloadsize
        for a in self.pDirectoryEntries:
            xPad(f)
            a.write_data(f)
        xPad(f)
        strings_start = f.tell()
        self.Header.FilenameStringsOffset = strings_start
        for a in self.pFilenameEntries:
            self.pFilenameEntries[a].write_entry(f)
        for a in self.pFilenameEntries:
            self.pFilenameEntries[a].write_string(f)
        stringsize = f.tell()-strings_start
        self.Header.FilenameStringsLength = stringsize
        self.Footer.write(f)
        f.seek(0)
        self.Header.write(f)

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