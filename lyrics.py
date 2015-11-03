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
            string includes all timestamps and escape sequences.
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

    def getPhrases(self):
        """Get the lyrics as a list of phrases

        Returns:
            list. A representation of the lyrics as a list of strings.
            Each string is a separate "phrase": a substring of the lyrics
            delimited by timestamps or start/end of file. The phrases
            contain no timestamps or escape sequences, but
            may contain newlines or trailing spaces.
        """
        raise NotImplemented

    def getTimes(self):
        """Get all timing data

        Returns:
            list. A list of pairs (time, phrase), ordered by time::
                time (int): start time of a lyric in hundredths of a second
                phrase (int): index of a phrase in the list returned by
                    self.getPhrases()
        """
        raise NotImplemented

    def getCurrentIndex(self, time):
        """Get the index of the current phrase of the song

        Args:
            time (int): time in hundredths of a second

        Returns:
            int. index of the phrase in self.getPhrases() that is being
            sung at time time.
        """
        raise NotImplemented
