#! /usr/bin/python2

import kchan.timedtext as timedtext

ID3_START = "TAG"
ID3_LENGTH = 128

SIZE_LENGTH = 6
START_TAG = "LYRICSBEGIN"
END_TAG = "LYRICS200"

SIZE_OFFSET = -(SIZE_LENGTH + len(END_TAG) + ID3_LENGTH)

FIELD_ID_LENGTH = 3
FIELD_SIZE_LENGTH = 5

def read(filepath):
    """Read Lyrics3 v2.00 data from an mp3 file

    Args:
        filepath (str): pathname of mp3 file containing Lyrics3 v2.00 data

    Returns:
        str. Lyrics3 v2.00 data, including "LYRICSBEGIN" but not including
        size descriptor and "LYRICS200" string.

    Raises:
        ValueError: file does not contain Lyrics3 v2.00 data
    """

    with open(filepath, 'rb') as f:
        f.seek(SIZE_OFFSET, 2)
        size = 0
        try:
            size = int(f.read(SIZE_LENGTH))
        except ValueError:
            raise ValueError, "Lyrics3 v2.00 size field not found in file {}".format(filepath)
        if f.read(len(END_TAG)) != END_TAG:
            raise ValueError, "Lyrics3 v2.00 tag not found in file {}".format(filepath)

        f.seek(SIZE_OFFSET - size, 2)
        return f.read(size)

def write(filepath, lyricsData):
    """Write Lyrics3 v2.00 data to an mp3 file

    Args:
        filepath (str): pathname of mp3 file to write data to
        lyricsData (str): Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.
    """
    if len(lyricsData) >= 10**SIZE_LENGTH:
        raise ValueError, "Lyrics data too long"

    lyricsData = lyricsData + "{{:0{}}}".format(SIZE_LENGTH).format(len(lyricsData)) + END_TAG

    with open(filepath, 'r+ab') as f:
        # first, remove existing Lyrics3 and ID3 data, saving ID3
        # data if it's there
        f.seek(-ID3_LENGTH, 2)
        id3 = f.read(ID3_LENGTH)

        if id3.startswith(ID3_START):
            # check for Lyrics3 data
            f.seek(SIZE_OFFSET, 2)
            size = None
            try:
                size = int(f.read(SIZE_LENGTH))
            except ValueError:
                pass
            if size is not None and f.read(len(END_TAG)) == END_TAG:
                # Lyrics3 data found, truncate at start of Lyrics3 data
                f.seek(SIZE_OFFSET - size, 2)
            else:
                # Just ID3, truncate at start of ID3
                f.seek(-ID3_LENGTH, 2)
            f.truncate()
        else:
            id3 = ID3_START + ('\0' * (ID3_LENGTH - len(ID3_START)))

        # Our file has now been truncated so that it contains no
        # Lyrics3 or ID3 data; now we add in our Lyrics3 data and an
        # ID3 tag.
        f.write(lyricsData + id3)
        f.flush()
        f.close()

def load(lyricsData, kcl=True):
    """Parse Lyrics3 v2.00 data

    Args:
        lyricsData (str): Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.

    Kwargs:
        kcl (bool): Use KCL lyrics data if available. KCL is an ad-hoc
        format invented for this program; it's a Lyrics3 tag identical
        to LYR, except that the timestamps have 0.01-second precision
        and it uses unix line endings.

    Returns:
        New Lyrics instance containing the lyrics data

    Raises:
        ValueError: data isn't valid Lyrics3 v2.00 data or doesn't contain any
            LYR field
    """
    if not lyricsData.startswith(START_TAG):
        raise ValueError, "Not valid Lyrics3 v2.00 data"

    lyricsData = lyricsData[len(START_TAG):]

    lyrLyrics = None
    kclLyrics = None
    metadata = {}

    while lyricsData:
        fieldId = lyricsData[:FIELD_ID_LENGTH]
        lyricsData = lyricsData[FIELD_ID_LENGTH:]

        fieldSize = int(lyricsData[:FIELD_SIZE_LENGTH])
        lyricsData = lyricsData[FIELD_SIZE_LENGTH:]

        fieldData = lyricsData[:fieldSize]
        lyricsData = lyricsData[fieldSize:]

        if fieldId == "LYR":
            lyrLyrics = timedtext.load(fieldData)
        elif fieldId == "KCL":
            kclLyrics = timedtext.load(fieldData)
        elif fieldId == "EAL":
            metadata["album"] = fieldData
        elif fieldId == "EAR":
            metadata["artist"] = fieldData
        elif fieldId == "ETT":
            metadata["title"] = fieldData
        else:
            pass

    lyrics = (kclLyrics if kcl else None) or lyrLyrics
    if lyrics is None:
        raise ValueError, "Lyrics not found"

    lyrics.setMetadata(**metadata)
    return lyrics

def dump(lyrics, kcl=True):
    """Dump data from Lyrics instance to Lyrics3 v2.00 format

    Args:
        lyrics (Lyrics): Lyrics instance to dump as Lyrics3 v2.00 data

    Kwargs:
        kcl (bool): Include KCL lyrics in addition to LYR lyrics;
        this allows us to include higher-precision timestamps in a
        backwards-compatible way.

    Returns:
        str. String containing Lyrics3 v2.00 data, including "LYRICSBEGIN"
            but not including size descriptor and "LYRICS200" string.
    """
    lyrData = timedtext.dump(lyrics, crlf=True)

    if len(lyrData) >= 10**FIELD_SIZE_LENGTH:
        raise ValueError, "Lyrics too long"

    lyrics3Data = (START_TAG
              + "LYR{{:0{}}}".format(FIELD_SIZE_LENGTH).format(len(lyrData))
              + lyrData)

    if kcl:
        kclData = timedtext.dump(lyrics, frac=True)
        if len(kclData) >= 10**FIELD_SIZE_LENGTH:
            raise ValueError, "Lyrics too long"
        lyrics3Data += ("KCL{{:0{}}}".format(FIELD_SIZE_LENGTH).format(len(kclData))
                   + kclData)

    return lyrics3Data
