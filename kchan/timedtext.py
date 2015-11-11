#! /usr/bin/python2

import re
from kchan.lyrics import Lyrics

def load(lyricsData):
    """Parse text with timestamps into a Lyrics instance

    Args:
        lyricsData (str): String containing text and timestamps. There may be
        any number of timestamps, in any order, at any locations, but they must
        all be of the form [mm:ss] or [mm:ss.xx]. If several timestamps appear
        consecutively with nothing separating them, they are treated as all
        applying to the nonempty phrase that follows, so that the phrase is
        repeated at several different times in the song. If there's no initial
        timestamp, then the initial phrase is treated as having timestamp
        [00:00.00].

    Returns:
        Lyrics instance storing the phrases and timing from the provided lyrics,
        with no metadata
    """
    lyrics = Lyrics()

    terms = re.split("(\[\d\d:\d\d\]|\[\d\d:\d\d\.\d\d\])", lyricsData)

    if terms[0] != "":
        lyrics.addPhrase(terms[0], [0])

    timedphrases = zip(terms[1::2], terms[2::2]) # pairs of timestamp and phrase

    times = []
    for (t, p) in timedphrases:
        m = re.match("\[(\d\d):(\d\d)\.?(\d\d)?\]", t)
        timeParts = m.groups('00')
        time = (int(timeParts[0]) * 6000
                + int(timeParts[1]) * 100
                + int(timeParts[2]))
        times.append(time)

        if p != "":
            lyrics.addPhrase(p, times)
            times = []

    if times != []:
        lyrics.addPhrase("", times)

    return lyrics

def dump(lyrics, frac=False, crlf=False):
    """Dump timing data from a Lyrics instance into a string format

    Args:
        lyrics (Lyrics): Lyrics instance to be converted to text

    Kwargs:
        frac (bool): whether to include hundredths of a second in timestamps.
            If True, timestamps will be of the form [mm:ss.xx], otherwise
            they will just be [mm:ss] (rounded to the nearest second).
            Defaults to False.
        cr (bool): whether to use CRLF newlines. Defaults to False.

    Returns:
        str. A string containing phrases and timestamps.
    """
    phrases = [[phrase.replace('\n', '\r\n') if crlf else phrase]
               for phrase in lyrics.getPhrases()]
    times = lyrics.getTimes()

    for (time, idx) in times:
        minutes = time / 6000
        seconds = (time / 100) % 60
        hundredths = time % 100
        if frac:
            phrases[idx].insert(-1, "[{:02}:{:02}.{:02}]".format(minutes, seconds, hundredths))
        else:
            phrases[idx].insert(-1, "[{:02}:{:02}]".format(minutes, seconds + (1 if hundredths >= 50 else 0)))

    return ''.join(''.join(l) for l in phrases)
