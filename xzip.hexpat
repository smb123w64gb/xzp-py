#pragma pattern_limit 999999999

#include <type/time.pat>

struct xZipHeader_t {
    u32 Magic ;                                             // MAGIC
    u32 Version;                                    // VERSION
    u32 PreloadDirectoryEntries;    // Number of preloaded directory entries.
    u32 DirectoryEntries;                   // Total # of directory entries (may not correspond to # of files as one file may have any number of directory entries)
    u32 PreloadBytes;                               // Number of bytes following the directory to preload.
    u32 HeaderLength;                               // Length of this header.
    u32 FilenameEntries;                    // The count of filename entries.
    u32 FilenameStringsOffset;              // Offset to the filename strings offset table (array of dwords) (v2 only)
    u32 FilenameStringsLength;              // Length of the filename string data. ( including the offsets table
};

struct xZipDirectoryEntry_t
{
    u32 FilenameCRC;      // CRC of the filename

    u32 Length;           // Length of this chunk of the file. In bytes. TODO: use sectors instead:
    s32 StoredOffset;     // Offset the file data in the .xzip.  When building the zip, a negative means standard data, positive means preloaded data.
    char data[Length] @ StoredOffset;
};
struct xZipFilenameEntry_t
{
    u32 FilenameCRC;
    u32 FilenameOffset;
    type::time32_t timestamp;
    char Filename[] @ FilenameOffset;
};

struct xZip{
    xZipHeader_t m_Header;
    xZipDirectoryEntry_t m_pDirectory[m_Header.DirectoryEntries];
    xZipDirectoryEntry_t m_pPreloadDirectory[m_Header.PreloadDirectoryEntries];
    s16 nRegular2PreloadSize[m_Header.DirectoryEntries];
    xZipFilenameEntry_t m_pFilename[m_Header.DirectoryEntries] @ m_Header.FilenameStringsOffset;
};

xZip file @ 0;
