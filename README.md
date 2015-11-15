# Karaoke-chan

## Synopsis

Karaoke-chan is a (hopefully) cross-platform karaoke player written
with wxPython. I wrote this because I couldn't find any free-software
karaoke players that handled Lyrics3 lyrics.

## Status

This software is currently in beta, and many planned features aren't
there yet. Lyrics3 handling isn't complete, and it may erase metadata
from Lyrics3 tags in mp3 files. Also, it's only been tested on Linux
so far; feedback from users on other platforms would be very much
appreciated.

## Requirements

* Python 2
* [wxPython] (http://wxpython.org/)

### Linux-specific

* gstreamer 0.10
* Whatever gstreamer plugins you need for the file formats you want to play

## Usage

To start the player, just run `karaokechan.py`.

### Playback

To play media files, open them (Ctrl-O), and click the "Play/Pause"
button. If the file includes Lyrics3 v2.00 lyrics, they will be
automatically displayed, and each phrase of the song will turn blue
when you're supposed to sing it. If your lyrics are longer than the
viewer panel, it should automatically scroll to follow the current
phrase.

### Editing

To edit lyrics for a media file, open the lyrics editor (Ctrl-E); a
new pane will appear where you can enter lyrics and timestamps.

The text in the lyrics editor will consist of song phrases
interspersed with timestamps, like this:

```
[00:02.02]Zankoku na tenshi no you ni
[00:07.57]Shounen yo shinwa ni nare
[00:15.18]
[00:23.64]Aoi [00:24.66]kaze ga ima
[00:26.65]Mune no doa o tataite mo
[00:30.37]Watashi dake o [00:32.22]tada mitsumete
[00:34.14]Hohoenderu anata
```

Timestamps can be anywhere in the text, in any order; a timestamp
marks the point where the following phrase begins.

To time a song, you should start by typing in the lyrics, and adding
placeholders where you want timestamps to go.  To add a placeholder at
the current cursor location, press Ctrl-Shift-T; placeholders will
also appear at the start of every new line:

```
[]Zankoku na tenshi no you ni
[]Shounen yo shinwa ni nare
[]
[]Aoi []kaze ga ima
[]Mune no doa o tataite mo
[]Watashi dake o []tada mitsumete
[]Hohoenderu anata
```

To set timestamps, start playing the song, and press Ctrl-T every time
a phrase starts; the next timestamp or placeholder after the cursor
location will be set to the current time in the song, and the cursor
will be moved ahead to the following timestamp or placeholder.

Once you're done, you can save your changes with Ctrl-S, and close the
editor with Ctrl-W.

## Supported file formats

Karaoke-chan uses wxPython's MediaCtrl widget to play media files;
this, in turn, uses whatever media player is available natively on
your system (GStreamer on Linux, QuickTime on Mac OS, and DirectShow
on Windows). Thus, it can play whatever media formats your native
player can.

Currently, creating, editing, and viewing lyrics is only supported for
MP3 files; this will change soon. Lyrics data is embedded in MP3 files
using the Lyrics3 v2.00 format, with some extra (backwards-compatible)
tweaks.

## License

This software is released under the MIT License.
