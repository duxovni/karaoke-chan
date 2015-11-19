#! /usr/bin/env python2


from __future__ import division

import re

import Tkinter as tk

import kchan.timedtext as timedtext


class LyricsCtrl(tk.Text):
    def __init__(self, parent, player, font):
        tk.Text.__init__(self, parent, wrap=tk.WORD, state=tk.DISABLED,
                         font=font)
        self.player = player
        self.lyrics = None
        # parent is responsible for calling OnPlayer on player state change
        self.phraseTimer = None
        self.font = font
        self.tag_config('tag-center', justify='center')

    def SetLyrics(self, lyrics):
        self.lyrics = lyrics
        self.phrases = lyrics.getPhrases()
        self.times = lyrics.getTimes()
        self.config(state=tk.NORMAL)
        self.delete('0.0', tk.END)
        self.insert('0.0', ''.join(self.phrases), 'tag-center')
        self.config(state=tk.DISABLED)

    def ClearLyrics(self):
        self.lyrics = None
        self.phrases = None
        self.times = None
        self.config(state=tk.NORMAL)
        self.delete('0.0', tk.END)
        self.config(state=tk.DISABLED)

    def CenterPosition(self, pos):
        boxHeight = self.winfo_height()
        lineHeight = self.font.metrics('linespace')
        lineCount = boxHeight // lineHeight

        currentLine = int(self.index(pos).split('.')[0])
        lastLine = int(self.index(tk.END + '-1c').split('.')[0])

        # As long as lineCount is nonzero, (lineCount - 1) / 2 and
        # lineCount / 2 must be two nonnegative numbers with sum
        # lineCount - 1, so the number of lines from topLine to
        # bottomLine inclusive will be exactly lineCount.
        topLine = max(currentLine - (lineCount - 1) // 2, 0)
        bottomLine = min(currentLine + lineCount // 2, lastLine)

        self.see('{}.0'.format(topLine))
        self.see('{}.0'.format(bottomLine))
        self.see(pos) # even if something weird happens, pos will be visible

    def OnPhraseTimer(self):
        if self.lyrics is None:
            return

        playTime = self.player.Tell() / 10
        phrase, startTime, endTime = self.lyrics.getCurrent(playTime)

        if phrase is not None:
            phraseStart = sum(len(p) for p in self.phrases[:phrase])
            phraseEnd = phraseStart + len(self.phrases[phrase])

            # self.tag_add('reset', 0, tk.END, wx.TextAttr(wx.BLACK))
            self.config(state=tk.NORMAL)
            self.tag_delete('highlight')
            self.tag_add('highlight',
                         '0.0 + {} chars'.format(phraseStart),
                         '0.0 + {} chars'.format(phraseEnd))
            self.tag_config('highlight', foreground='blue')
            self.config(state=tk.DISABLED)
            self.CenterPosition('0.0 + {} chars'.format(phraseStart))

        if endTime is not None:
            self.phraseTimer = self.after(int((endTime - playTime) * 10),
                                          self.OnPhraseTimer)

    def OnPlayer(self):
        if self.player.playing():
            self.OnPhraseTimer()
        else:
            if self.phraseTimer is not None:
                self.after_cancel(self.phraseTimer)


class LyricsEditor(tk.Text):
    def __init__(self, parent, player):
        tk.Text.__init__(self, parent, wrap=tk.WORD, undo=True)
        self.player = player
        self.bind('<Key-Return>', (lambda evt: self.OnEnter()), self)

    def LoadLyrics(self, lyrics):
        self.delete('0.0', tk.END)
        if lyrics is not None:
            self.insert('0.0', timedtext.dump(lyrics, frac=True))
        self.edit_reset()
        self.edit_modified(False)

    def GetLyrics(self):
        return timedtext.load(self.get('0.0', tk.END).replace('[]', ''))

    def AddPlaceholder(self):
        self.insert(tk.INSERT, '[]')

    def FindNextTimestamp(self, pos=None):
        if pos is None:
            pos = tk.INSERT

        atPos = self.get(pos, tk.END)
        match = re.search(r'\[(\d\d:\d\d(.\d\d)?)?\]', atPos)
        if not match:
            return None
        return ('{} + {} chars'.format(pos, match.start()),
                '{} + {} chars'.format(pos, match.end()))

    def SetTimestamp(self):
        self.focus_set()

        nextTimestamp = self.FindNextTimestamp()
        if not nextTimestamp:
            return False

        playTime = self.player.Tell()
        self.mark_set('ts_end', nextTimestamp[1])
        self.delete(nextTimestamp[0], nextTimestamp[1])
        self.insert(nextTimestamp[0],
                    '[{:02}:{:02}.{:02}]'.format(int(playTime / 60000),
                                                 int(playTime / 1000) % 60,
                                                 int(playTime / 10) % 100))

        nextTimestamp = self.FindNextTimestamp('ts_end')
        if nextTimestamp:
            self.mark_set(tk.INSERT, nextTimestamp[0])

        return True

    def OnEnter(self):
        self.insert(tk.INSERT, '\n')
        self.AddPlaceholder()
        return 'break'
