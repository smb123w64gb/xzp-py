# xzp-py
Xzip Python ProtoType

Just getting my barrings again...
Else this is just my rough draft till it works and i move over to the xzp-rs code.

Allot of the code is going to be based around Valves own in the 2006 sdk (source-sdk-2006-ep1\public\xzp.cpp & xzp.h)

Why do we need xzp? XFat has limmited folders and files, so having HL2 in a uncompressed state is a no go on real hardware. While itll be good for emu testing, real hardware needs less folders.
What does xzp do? xZip is Valve's format made specaly for xbox OG, I beleve the 360 and PS3 Source games have there own. 
    It contains the main file, and some headers to "PreLoad". Allot of it is XTF headers which include there Backup MIP as the preloaded image.

There more research todo but that what i have for now.