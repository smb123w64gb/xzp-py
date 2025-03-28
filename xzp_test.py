import sys
import xzip
import os



xzpin = open(sys.argv[1], "rb")
xzipfile = xzip.xZip()
xzipfile.read(xzpin)
xzpin.close()

xzpout = open(sys.argv[2],'wb')
xzipfile.write(xzpout)
'''
rootdir = sys.argv[1]

newxzp = xzip.xZip()


for currentpath, folders, files in os.walk(rootdir):
    for file in files:
        newxzp.addFile(open(os.path.join(currentpath, file),'rb'),os.path.join(currentpath, file).replace(rootdir,'')[1:])
        #print(os.path.join(currentpath, file).replace(rootdir,'')[1:])

xzpout = open(sys.argv[2],'wb')
newxzp.write(xzpout)
'''


#Extraction
# 1. I must make the directorys if they do not exist.
# 2. But i must remove the file its selfS
#for x in xzipfile.pDirectoryEntries:
#    print(x.Filename.split("\\"))
