#! /usr/bin/env python2

import os.path
import user
import re

import wx
import wx.media as wxm

import kchan.lyrics as lyrics
import kchan.widgets as kcw
import kchan.timedtext as timedtext
import kchan.formats.lyrics3v2 as lyrics3v2

class KaraokePlayer(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # media widget
        self.player = wxm.MediaCtrl(self)
        self.Bind(wxm.EVT_MEDIA_FINISHED, self.HandleStop, self.player)

        # lyrics viewer
        self.lyricsViewer = kcw.LyricsCtrl(self, self.player)

        # lyrics editor
        self.lyricsEditor = kcw.LyricsEditor(self, self.player)

        # menu bar
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(wx.ID_OPEN)
        self.fileMenu.Append(wx.ID_EDIT)
        self.fileMenu.Append(wx.ID_SAVE)
        self.fileMenu.Append(wx.ID_CLOSE)
        self.fileMenu.Append(wx.ID_EXIT)
        self.menuBar.Append(self.fileMenu, "&File")
        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.HandleOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.HandleEdit, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.HandleSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.HandleClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.HandleExit, id=wx.ID_EXIT)

        # these are only enabled in Edit Mode
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)

        # controls
        self.playPauseButton = wx.ToggleButton(self, label="Play/Pause")
        self.stopButton = wx.Button(self, label="Stop")
        self.muteButton = wx.ToggleButton(self, label="Mute")
        self.timestampButton = wx.Button(self, label="Set Timestamp")
        self.volumeSlider = wx.Slider(self, minValue=0, maxValue=100, size=(100, -1))
        self.volumeLabel = wx.StaticText(self, size=(50,-1), label="0%",
                                         style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        self.timeSlider = wx.Slider(self, minValue=0, maxValue=0)
        self.timeLabel = wx.StaticText(self, size=(100, -1), label="0:00/0:00",
                                       style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.HandlePlayPause, self.playPauseButton)
        self.Bind(wx.EVT_BUTTON, self.HandleStop, self.stopButton)
        self.Bind(wx.EVT_BUTTON, self.HandleSetTimestamp, self.timestampButton)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.HandleMute, self.muteButton)
        self.Bind(wx.EVT_SLIDER, self.HandleVol, self.volumeSlider)
#        self.Bind(wx.EVT_SLIDER, self.HandleTime, self.timeSlider)

        # sizers
        self.editorButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.editorButtonSizer.Add(self.timestampButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(self.playPauseButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.buttonSizer.Add(self.stopButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.buttonSizer.AddStretchSpacer()
        self.buttonSizer.Add(self.editorButtonSizer, 0, wx.EXPAND)
        self.buttonSizer.Hide(self.editorButtonSizer) # only shown in Edit Mode
        self.buttonSizer.AddStretchSpacer()
        self.buttonSizer.Add(self.muteButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.buttonSizer.Add(self.volumeSlider, 0, wx.ALIGN_CENTER_VERTICAL)
        self.buttonSizer.Add(self.volumeLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.timeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timeSizer.Add(self.timeSlider, 1, wx.ALIGN_CENTER_VERTICAL)
        self.timeSizer.Add(self.timeLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.controlSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlSizer.Add(self.timeSizer, 0, wx.EXPAND)
        self.controlSizer.Add(self.buttonSizer, 0, wx.EXPAND)

        self.viewerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.viewerSizer.Add(self.player, 1, wx.EXPAND)
        self.viewerSizer.Add(self.lyricsViewer, 1, wx.EXPAND)
        self.viewerSizer.Add(self.lyricsEditor, 1, wx.EXPAND)
        self.viewerSizer.Hide(self.lyricsEditor)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.viewerSizer, 1, wx.EXPAND)
        self.mainSizer.Add(self.controlSizer, 0, wx.EXPAND)

        self.SetSizerAndFit(self.mainSizer)

        # timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.HandleTimer, self.timer)

        # flag to indicate which mode we're in
        self.editMode = False

        self.Show()

    def HandleOpen(self, evt):
        self.HandleStop(None)

        dialog = wx.FileDialog(self)

        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
            filename = dialog.GetFilename()

            # Show lyrics, if available
            if os.path.splitext(filename)[1] == ".mp3":
                try:
                    self.lyricsViewer.SetLyrics(lyrics3v2.load(lyrics3v2.read(filepath)))
                except ValueError:
                    pass

            self.player.Load(filepath)

            # Hide lyrics viewer if there are no lyrics
            if self.lyricsViewer.IsEmpty():
                self.viewerSizer.Hide(self.lyricsViewer)
            else:
                self.viewerSizer.Show(self.lyricsViewer)

            # Hide player screen if there's no video
            if self.player.GetBestSize() == (0,0):
                self.viewerSizer.Hide(self.player)
            else:
                self.viewerSizer.Show(self.player)

            self.viewerSizer.Layout()

            title = filename
            self.SetTitle(u'{} - Karaoke-chan'.format(title))

            self.volumeSlider.SetValue(int(self.player.GetVolume() * 100))
            self.volumeLabel.SetLabelText("{}%".format(int(self.player.GetVolume() * 100)))
            self.HandleTimer(None)

    def HandleExit(self, evt):
        self.player.Stop()
        self.Close()

    def HandlePlayPause(self, evt):
        if self.playPauseButton.GetValue():
            self.player.Play()
            self.timer.Start(milliseconds=500)
            if self.editMode:
                self.lyricsEditor.SetFocus()
        else:
            self.player.Pause()
            self.timer.Stop()
            if self.editMode:
                self.lyricsViewer.SetLyrics(self.lyricsEditor.GetLyrics())

    def HandleStop(self, evt):
        self.timer.Stop()
        self.player.Stop()
        self.timeSlider.SetMax(0)
        self.timeSlider.SetValue(0)
        self.timeLabel.SetLabelText("0:00/0:00")
        self.playPauseButton.SetValue(False)

    def HandleMute(self, evt):
        if self.muteButton.GetValue():
            self.player.SetVolume(0)
        else:
            self.player.SetVolume(self.volumeSlider.GetValue() / 100.0)

    def HandleVol(self, evt):
        self.player.SetVolume(self.volumeSlider.GetValue() / 100.0)
        self.volumeLabel.SetLabelText("{}%".format(self.volumeSlider.GetValue()))

    def HandleTimer(self, evt):
        length = self.player.Length() / 1000
        time = self.player.Tell() / 1000
        self.timeSlider.SetMax(length)
        self.timeSlider.SetValue(time)
        self.timeLabel.SetLabelText("{}:{:02}/{}:{:02}".format(time/60, time%60, length/60, length%60))

    def HandleSetTimestamp(self, evt):
        self.lyricsEditor.SetTimestamp()

    def HandleEdit(self, evt):
        self.editMode = True

        self.fileMenu.Enable(wx.ID_EDIT, False)
        self.fileMenu.Enable(wx.ID_SAVE, True)
        self.fileMenu.Enable(wx.ID_CLOSE, True)

        self.buttonSizer.Show(self.editorButtonSizer)
        self.buttonSizer.Layout()
        self.viewerSizer.Show(self.lyricsEditor)
        self.viewerSizer.Layout()

        if self.lyricsViewer.lyrics is not None:
            self.lyricsEditor.LoadLyrics(self.lyricsViewer.lyrics)

    def HandleSave(self, evt):
        pass

    def HandleClose(self, evt):
        self.editMode = False

        self.fileMenu.Enable(wx.ID_EDIT, True)
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)

        self.buttonSizer.Hide(self.editorButtonSizer)
        self.buttonSizer.Layout()
        self.viewerSizer.Hide(self.lyricsEditor)
        self.viewerSizer.Layout()

if __name__ == "__main__":
    app = wx.App(False)
    player = KaraokePlayer(None, title="Karaoke-chan")
    player.Show()
    app.MainLoop()
