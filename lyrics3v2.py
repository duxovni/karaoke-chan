#! /usr/bin/python2

import timedtext

ID3_LENGTH = 128
SIZE_LENGTH = 6
START_TAG = "LYRICSBEGIN"
END_TAG = "LYRICS200"

SIZE_OFFSET = -(SIZE_LENGTH + len(END_TAG) + ID3_LENGTH)

FIELD_ID_LENGTH = 3
FIELD_SIZE_LENGTH = 5

def read(filename):
    """Read Lyrics3 v2.00 data from an mp3 file

    Args:
        filename (str): pathname of mp3 file containing Lyrics3 v2.00 data

    Returns:
        str. Lyrics3 v2.00 data, including "LYRICSBEGIN" but not including
        size descriptor and "LYRICS200" string.

    Raises:
        ValueError: file does not contain Lyrics3 v2.00 data
    """

    with open(filename, 'rb') as f:
        f.seek(SIZE_OFFSET, 2)
        size = int(f.read(SIZE_LENGTH))
        if f.read(len(END_TAG)) != END_TAG:
            raise ValueError, "{} tag not found in file {}".format(END_TAG,
                                                                   filename)

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

def load(lyricsData):
    """Parse Lyrics3 v2.00 data

    Args:
        lyricsData (str): Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.

    Returns:
        New Lyrics instance containing the lyrics data

    Raises:
        ValueError: data isn't valid Lyrics3 v2.00 data or doesn't contain any
            LYR field
    """
    if not lyricsData.startswith(START_TAG):
        raise ValueError, "Not valid Lyrics3 v2.00 data"

    lyricsData = lyricsData[len(START_TAG):]

    lyrics = None
    metadata = {}

    while lyricsData:
        fieldId = lyricsData[:FIELD_ID_LENGTH]
        lyricsData = lyricsData[FIELD_ID_LENGTH:]

        fieldSize = int(lyricsData[:FIELD_SIZE_LENGTH])
        lyricsData = lyricsData[FIELD_SIZE_LENGTH:]

        fieldData = lyricsData[:fieldSize]
        lyricsData = lyricsData[fieldSize:]

        if fieldId = "LYR":
            lyrics = timedtext.load(fieldData)
        elif fieldId == "EAL":
            metadata["album"] = fieldData
        elif fieldId = "EAR":
            metadata["artist"] = fieldData
        elif fieldId = "ETT":
            metadata["title"] = fieldData
        else:
            pass

    if lyrics is None:
        raise ValueError, "Lyrics not found"

    lyrics.setMetadata(**metadata)
    return lyrics

def dump(lyrics):
    """Dump data from Lyrics instance to Lyrics3 v2.00 format

    Args:
        lyrics (Lyrics): Lyrics instance to dump as Lyrics3 v2.00 data

    Returns:
        str. String containing Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.
    """
    raise NotImplementedError
