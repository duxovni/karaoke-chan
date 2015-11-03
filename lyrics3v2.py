#! /usr/bin/python2

ID3_LENGTH = 128
SIZE_LENGTH = 6
START_TAG = "LYRICSBEGIN"
END_TAG = "LYRICS200"

SIZE_OFFSET = -(SIZE_LENGTH + len(END_TAG) + ID3_LENGTH)

def read(filename):
    """Read Lyrics3 v2.00 data from an mp3 file

    Args:
        filename (str): pathname of mp3 file containing Lyrics3 v2.00 data

    Returns:
        str. Lyrics3 v2.00 data, including "LYRICSBEGIN" but not including
        size descriptor and "LYRICS200" string.
    """

    with open(filename, 'rb') as f:
        f.seek(SIZE_OFFSET, 2)
        size = int(f.read(SIZE_LENGTH))

        f.seek(SIZE_OFFSET - size, 2)
        return f.read(size)

def write(filename, lyricsData):
    """Write Lyrics3 v2.00 data to an mp3 file

    Args:
        filename (str): pathname of mp3 file to write data to
        lyricsData (str): Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.
    """
    raise NotImplemented
