import sys
import xzip
from pathlib import Path



xzpin = open(sys.argv[1], "rb")
xzipfile = xzip.xZip()
xzipfile.read(xzpin)
xzpin.close()

xzpout = open(sys.argv[2],'wb')
xzipfile.write(xzpout)

#Extraction
# 1. I must make the directorys if they do not exist.
# 2. But i must remove the file its selfS
#for x in xzipfile.pDirectoryEntries:
#    print(x.Filename.split("\\"))
