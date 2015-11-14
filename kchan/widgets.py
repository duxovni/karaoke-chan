#! /usr/bin/env python2

import re

import wx
import wx.media as wxm

import kchan.timedtext as timedtext

class LyricsCtrl(wx.TextCtrl):
    def __init__(self, parent, player):
        wx.TextCtrl.__init__(self, parent,
                             style = wx.TE_MULTILINE
                             | wx.TE_READONLY
                             | wx.TE_CENTRE)
        self.player = player
        self.lyrics = None
        self.phraseTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.HandlePhraseTimer, self.phraseTimer)
        # parent is responsible for calling HandlePlayer on player state change

    def SetLyrics(self, lyrics):
        self.lyrics = lyrics
        self.phrases = lyrics.getPhrases()
        self.times = lyrics.getTimes()
        self.SetValue(''.join(self.phrases))

    def ClearLyrics(self):
        self.lyrics = None
        self.phrases = None
        self.times = None
        self.Clear()

    def CenterPosition(self, pos):
        boxHeight = self.GetClientSize()[1]
        lineHeight = self.GetDefaultStyle().GetFont().GetPixelSize().GetHeight()
        lineCount = boxHeight / lineHeight

        currentLine = self.PositionToXY(pos)[1]
        lastLine = self.PositionToXY(self.GetLastPosition())[1]

        # As long as lineCount is nonzero, (lineCount-1)/2 and
        # lineCount/2 must be two nonnegative numbers with sum
        # lineCount-1, so the number of lines from topLine to
        # bottomLine inclusive will be exactly lineCount.
        topLine = max(currentLine - (lineCount-1)/2, 0)
        bottomLine = min(currentLine + lineCount/2, lastLine)

        self.ShowPosition(self.XYToPosition(0, topLine))
        self.ShowPosition(self.XYToPosition(0, bottomLine))
        self.ShowPosition(pos) # even if something weird happens, pos will be visible

    def HandlePhraseTimer(self, evt):
        if self.lyrics is None:
            return

        playTime = self.player.Tell() / 10
        phrase, startTime, endTime = self.lyrics.getCurrent(playTime)

        if phrase is not None:
            phraseStart = sum(len(p) for p in self.phrases[:phrase])
            phraseEnd = phraseStart + len(self.phrases[phrase])

            # if self.lastPhrase is not None:
            #     self.SetStyle(self.lastPhrase[0], self.lastPhrase[1],
            #                   wx.TextAttr(wx.Colour(100,100,100)))

            self.SetStyle(0, self.GetLastPosition(), wx.TextAttr(wx.Colour(0, 0, 0)))
            self.SetStyle(phraseStart, phraseEnd, wx.TextAttr(wx.Colour(0, 0, 255)))
            self.CenterPosition(phraseStart)

            self.lastPhrase = (phraseStart, phraseEnd)

        if endTime is not None:
            self.phraseTimer.Start((endTime - playTime) * 10, wx.TIMER_ONE_SHOT)

    def HandlePlayer(self, evt):
        if self.player.GetState() == wxm.MEDIASTATE_PLAYING:
            self.HandlePhraseTimer(None)
        else:
            self.phraseTimer.Stop()

class LyricsEditor(wx.TextCtrl):
    def __init__(self, parent, player):
        wx.TextCtrl.__init__(self, parent,
                             style=wx.TE_MULTILINE
                             | wx.TE_PROCESS_ENTER)
        self.player = player
        self.Bind(wx.EVT_TEXT_ENTER, self.HandleEnter, self)

    def LoadLyrics(self, lyrics):
        if lyrics is None:
            self.Clear()
        else:
            self.SetValue(timedtext.dump(lyrics, frac=True))
        self.DiscardEdits()

    def GetLyrics(self):
        return timedtext.load(self.GetValue().replace("[]", ""))

    def AddPlaceholder(self):
        self.WriteText("[]")

    def FindNextTimestamp(self, pos=None):
        if pos is None:
            pos = self.GetInsertionPoint()

        atPos = self.GetRange(pos, self.GetLastPosition())
        match = re.search(r"\[(\d\d:\d\d(.\d\d)?)?\]", atPos)
        if not match:
            return None
        return (pos + match.start(), pos + match.end())

    def AtTimestamp(self):
        nextTimestamp = self.FindNextTimestamp()
        return nextTimestamp and nextTimestamp[0] == self.GetInsertionPoint()

    def ToNextTimestamp(self):
        nextTimestamp = self.FindNextTimestamp(self.GetInsertionPoint()
                                               + (1 if self.AtTimestamp() else 0))
        if nextTimestamp:
            self.SetInsertionPoint(nextTimestamp[0])
            return True
        else:
            return False

    def SetTimestamp(self):
        self.SetFocus()

        nextTimestamp = self.FindNextTimestamp()
        if not nextTimestamp:
            return False

        playTime = self.player.Tell()
        self.Replace(nextTimestamp[0], nextTimestamp[1],
                     "[{:02}:{:02}.{:02}]".format(playTime / 60000,
                                                  (playTime / 1000) % 60,
                                                  (playTime / 10) % 100))

        nextTimestamp = self.FindNextTimestamp()
        if nextTimestamp:
            self.SetInsertionPoint(nextTimestamp[0])

        return True

    def HandleEnter(self, evt):
        self.WriteText("\n")
        self.AddPlaceholder()
