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


def handler(fn):
    """Helper function to make simple event handlers"""
    def evtHandler(evt):
        fn()
    return evtHandler


class KaraokePlayer(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # media widget
        self.player = wxm.MediaCtrl(self)
        self.Bind(wxm.EVT_MEDIA_STATECHANGED, self.HandlePlayer, self.player)

        # lyrics viewer
        self.lyricsViewer = kcw.LyricsCtrl(self, self.player)

        # lyrics editor
        self.lyricsEditor = kcw.LyricsEditor(self, self.player)

        # menu bar
        self.menuBar = wx.MenuBar()
        self.SetMenuBar(self.menuBar)

        # file menu
        self.fileMenu = wx.Menu()
        self.menuBar.Append(self.fileMenu, "&File")

        self.fileMenu.Append(wx.ID_OPEN)
        self.fileMenu.Append(wx.ID_EDIT)
        self.fileMenu.Append(wx.ID_SAVE)
        self.fileMenu.Append(wx.ID_CLOSE)
        self.fileMenu.Append(wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.HandleOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.HandleEdit, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.HandleSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.HandleClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.HandleExit, id=wx.ID_EXIT)

        # timing menu
        self.timingMenu = wx.Menu()
        self.menuBar.Append(self.timingMenu, "&Timing")

        self.placeholderItem = self.timingMenu.Append(wx.ID_ANY,
                                                      "Add Timestamp Placeholder\tCTRL+SHIFT+T")
        self.timestampItem = self.timingMenu.Append(wx.ID_ANY, "Set Timestamp\tCTRL+T")

        self.Bind(wx.EVT_MENU, handler(self.lyricsEditor.AddPlaceholder),
                  self.placeholderItem)
        self.Bind(wx.EVT_MENU, handler(self.lyricsEditor.SetTimestamp),
                  self.timestampItem)

        # playback menu
        self.playbackMenu = wx.Menu()
        self.menuBar.Append(self.playbackMenu, "&Playback")

        self.playPauseItem = self.playbackMenu.Append(wx.ID_ANY, "Play/Pause\tCTRL+P")
        self.stopItem = self.playbackMenu.Append(wx.ID_ANY, "Stop\tCTRL+SHIFT+P")

        self.Bind(wx.EVT_MENU, self.HandlePlayPause, self.playPauseItem)
        self.Bind(wx.EVT_MENU, self.HandleStop, self.stopItem)

        # these are only enabled in Edit Mode
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
        for item in self.timingMenu.GetMenuItems():
            item.Enable(False)

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
        self.Bind(wx.EVT_BUTTON, handler(self.lyricsEditor.SetTimestamp),
                  self.timestampButton)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.HandleMute, self.muteButton)
        self.Bind(wx.EVT_SLIDER, self.HandleVol, self.volumeSlider)

        self.sliding = False
        self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.HandleTimeSliding, self.timeSlider)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.HandleTimeReleased, self.timeSlider)
        self.Bind(wx.EVT_SLIDER, self.HandleTimeAny, self.timeSlider)

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
        self.Bind(wx.EVT_TIMER, handler(self.UpdateTime), self.timer)

        # flag to indicate which mode we're in
        self.editMode = False

        # currently loaded file
        self.filepath = None

        self.Show()

    def UpdateTime(self, updateSliderTime=True):
        length = self.player.Length()
        time = self.player.Tell()
        if updateSliderTime:
            self.timeSlider.SetMax(length)
            self.timeSlider.SetValue(time)
        self.timeLabel.SetLabelText("{}:{:02}/{}:{:02}".format(time/60000, (time/1000)%60,
                                                               length/60000, (length/1000)%60))

    def HandlePlayer(self, evt):
        self.UpdateTime()

        if self.player.GetState() == wxm.MEDIASTATE_PLAYING:
            self.timer.Start(milliseconds=100)
            self.playPauseButton.SetValue(True)

            if self.editMode:
                self.lyricsEditor.SetFocus()
                self.lyricsViewer.SetLyrics(self.lyricsEditor.GetLyrics())
        else:
            self.timer.Stop()
            if not self.sliding:
                self.playPauseButton.SetValue(False)

        self.lyricsViewer.HandlePlayer(evt)

    def OpenFile(self, filepath):
        self.filepath = filepath
        # Show lyrics, if available
        self.lyricsViewer.ClearLyrics()
        if os.path.splitext(self.filepath)[1] == ".mp3":
            try:
                self.lyricsViewer.SetLyrics(lyrics3v2.load(lyrics3v2.read(self.filepath)))
            except ValueError:
                pass

        self.player.Load(self.filepath)

        if self.editMode:
            if self.lyricsViewer.lyrics:
                self.lyricsEditor.LoadLyrics(self.lyricsViewer.lyrics)
            else:
                self.lyricsEditor.Clear()

        # Hide lyrics viewer if there are no lyrics
        if self.lyricsViewer.IsEmpty() and not self.editMode:
            self.viewerSizer.Hide(self.lyricsViewer)
        else:
            self.viewerSizer.Show(self.lyricsViewer)

        # Hide player screen if there's no video
        if self.player.GetBestSize() == (0,0):
            self.viewerSizer.Hide(self.player)
        else:
            self.viewerSizer.Show(self.player)

        self.viewerSizer.Layout()

        title = os.path.basename(self.filepath)
        self.SetTitle(u'{} - Karaoke-chan'.format(title))

        self.volumeSlider.SetValue(int(self.player.GetVolume() * 100))
        self.volumeLabel.SetLabelText("{}%".format(int(self.player.GetVolume() * 100)))
        self.UpdateTime()

    def HandleOpen(self, evt):
        self.HandleStop(None)

        dialog = wx.FileDialog(self)

        if dialog.ShowModal() == wx.ID_OK:
            self.OpenFile(dialog.GetPath())

    def HandleExit(self, evt):
        self.player.Stop()
        self.Close()

    def HandlePlayPause(self, evt):
        if self.player.GetState() == wxm.MEDIASTATE_PLAYING:
            self.player.Pause()
        else:
            self.player.Play()

    def HandleStop(self, evt):
        self.player.Stop()

    def HandleMute(self, evt):
        if self.muteButton.GetValue():
            self.player.SetVolume(0)
        else:
            self.player.SetVolume(self.volumeSlider.GetValue() / 100.0)

    def HandleVol(self, evt):
        self.player.SetVolume(self.volumeSlider.GetValue() / 100.0)
        self.volumeLabel.SetLabelText("{}%".format(self.volumeSlider.GetValue()))

    def HandleEdit(self, evt):
        self.editMode = True

        self.fileMenu.Enable(wx.ID_EDIT, False)
        self.fileMenu.Enable(wx.ID_SAVE, True)
        self.fileMenu.Enable(wx.ID_CLOSE, True)
        for item in self.timingMenu.GetMenuItems():
            item.Enable(True)

        self.buttonSizer.Show(self.editorButtonSizer)
        self.buttonSizer.Layout()
        self.viewerSizer.Show(self.lyricsViewer)
        self.viewerSizer.Show(self.lyricsEditor)
        self.viewerSizer.Layout()

        if self.lyricsViewer.lyrics is not None:
            self.lyricsEditor.LoadLyrics(self.lyricsViewer.lyrics)

        self.lyricsEditor.SetFocus()

    def HandleSave(self, evt):
        try:
            lyrics3v2.write(self.filepath, lyrics3v2.dump(self.lyricsEditor.GetLyrics()))
        except:
            print "write error"

    def HandleClose(self, evt):
        self.editMode = False

        self.fileMenu.Enable(wx.ID_EDIT, True)
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
        for item in self.timingMenu.GetMenuItems():
            item.Enable(False)

        self.buttonSizer.Hide(self.editorButtonSizer)
        self.buttonSizer.Layout()
        self.viewerSizer.Hide(self.lyricsEditor)
        self.viewerSizer.Layout()
        self.OpenFile(self.filepath)

    def HandleTimeSliding(self, evt):
        self.sliding = True
        self.player.Pause()

    def HandleTimeReleased(self, evt):
        self.sliding = False
        if self.playPauseButton.GetValue():
            self.player.Play()

    def HandleTimeAny(self, evt):
        self.player.Seek(self.timeSlider.GetValue())
        self.UpdateTime(updateSliderTime=False)

if __name__ == "__main__":
    app = wx.App(False)
    player = KaraokePlayer(None, title="Karaoke-chan")
    player.Show()
    app.MainLoop()
