import sys
import xzip


xzpin = open(sys.argv[1], "rb")
xzipfile = xzip.xZip()
xzipfile.read(xzpin)
