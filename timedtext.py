#! /usr/bin/python2

import re
from lyrics import Lyrics

def load(lyricsData):
    """Parse text with timestamps into a Lyrics instance

    Args:
        lyricsData (str): String containing text and timestamps. There may be
        any number of timestamps, in any order, at any locations, but they must
        all be of the form [mm:ss] or [mm:ss.xx].

    Returns:
        Lyrics instance storing the phrases and timing from the provided lyrics,
        with no metadata
    """
    raise NotImplementedError

def dump(lyrics, frac=False, crlf=False):
    """Dump timing data from a Lyrics instance into a string format

    Args:
        lyrics (Lyrics): Lyrics instance to be converted to text

    Kwargs:
        frac (bool): whether to include hundredths of a second in timestamps.
            If True, timestamps will be of the form [mm:ss.xx], otherwise
            they will just be [mm:ss]. Defaults to False.
        cr (bool): whether to use CRLF newlines. Defaults to False.

    Returns:
        str. A string containing phrases and timestamps.
    """
    raise NotImplementedError
