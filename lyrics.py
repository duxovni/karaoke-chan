#! /usr/bin/python2

class Lyrics:
    """Data type for representing karaoke lyrics"""

    def __init__(self, lyricsData, lyricsFormat="lyrics3v2"):
        """Create a new Lyrics instance

        Args:
            lyricsData (str): lyrics data

        Kwargs:
            lyricsFormat (str): format of lyricsData; can be one of lyrics3v2,
                [more to come]. Defaults to "lyrics3v2".
        """
        raise NotImplemented

    def dump(self, lyricFormat="lyrics3v2"):
        """Dump a raw text representation of the lyrics

        Kwargs:
            lyricsFormat (str): format to dump lyrics in; can be one of
                lyrics3v2, [more to come]. Defaults to "lyrics3v2".

        Returns:
            str. A string representation of the lyrics suitable for
            saving to a file or passing to the Lyrics constructor. The
            string includes all timing markers and escape sequences.
        """
        raise NotImplemented

    def getMetadata(self):
        """Get a dictionary of song metadata

        Returns:
            dict. May contain some, all, or none of the following keys::
                "artist" (str): Name of the artist
                "album" (str): Name of the album
                "title" (str): Title of the song
                "length" (int): Length of the song in seconds
        """
        raise NotImplemented

    def getLines(self):
        """Get the lyrics as a list of lines

        Returns:
            list. A representation of the lyrics as a list of
            lists. Each sublist corresponds to a line of the song, and
            contains strings for individually-timed phrases. The phrases
            contain no newlines, timing markers, or escape sequences, but
            may have trailing spaces.
        """
        raise NotImplemented

    def getTimes(self):
        """Get all timing data

        Returns:
            list. A list of pairs (time, (line, phrase)), ordered by time::
                time (int): start time of a lyric in hundredths of a second
                line (int): index of a line in the list returned by
                    self.getLines()
                phrase (int): index of a phrase in self.getLines()[line]
        """
        raise NotImplemented

    def getCurrentIndex(self, time):
        """Get the index of the current phrase of the song

        Args:
            time (int): time in hundredths of a second

        Returns:
            tuple. A pair (line, phrase) indicating the phrase that should be
            sung at time time::
                line (int): index of a line in the list returned by
                    self.getLines()
                phrase (int): index of a phrase in self.getLines()[line]
        """
        raise NotImplemented
