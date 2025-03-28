import sys,os
from xzip import *
xzip = open(sys.argv[1], "rb")
basedir = sys.argv[1][0:sys.argv[1].find('.',1)] + '\\'
xz = xZip()
xz.read(xzip)

preloadSize = 0
for x in range(xz.Header.DirectoryEntries):
    filename = basedir+xz.pFilenameEntries[x].Filename
    filedir = filename[0:filename.rfind('\\')]
    if(not os.path.exists(filedir)):
        os.makedirs(filedir)
    file = open(filename, "wb")
    file.write(xz.pDirectoryEntries[x].Data)
    if(xz.nRegular2PreloadEntryMapping[x] != 0xFFFF):
        print("Preload:%s\t%s\t%s"%(xz.pPreloadDirectoryEntries[xz.nRegular2PreloadEntryMapping[x]].Length,xz.pDirectoryEntries[x].Length,xz.pFilenameEntries[x].Filename))
    file.close()