#!/usr/bin/env python2


from __future__ import division

import os.path
import user
import re
import argparse

import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkFont

import kchan.lyrics as lyrics
import kchan.widgets as kcw
import kchan.timedtext as timedtext
import kchan.formats.lyrics3v2 as lyrics3v2
import kchan.player as player


handler = lambda fn: lambda evt: fn()


class CancelException(Exception):
    pass


def save_dialog():
    answer = tkMessageBox.askquestion(
        'Save changes?', 'You have unsaved changes.  Save before closing?',
        type=tkMessageBox.YESNOCANCEL, default=tkMessageBox.CANCEL)
    if answer == 'yes':
        return True
    if answer == 'no':
        return False
    raise CancelException


class KaraokePlayer(tk.Frame):
    def __init__(self, parent=None, filepath=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('Karaoke-chan')

        # media widget
        self.player = player.Player(self.OnPlayer)

        lyricsFrame = tk.Frame(self)
        lyricsFrame.pack(fill=tk.BOTH, expand=1)

        # lyrics viewer
        font = tkFont.Font(root=self.parent, family='Helvetica', size='12')
        self.lyricsViewer = kcw.LyricsCtrl(lyricsFrame, self.player, font)
        self.lyricsViewer.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        # lyrics editor
        self.lyricsEditor = kcw.LyricsEditor(lyricsFrame, self.player)

        # menu bar
        self.menuBar = tk.Menu(parent)
        parent.config(menu=self.menuBar)

        # file menu
        self.fileMenu = tk.Menu(self.menuBar, tearoff=False)
        self.menuBar.add_cascade(menu=self.fileMenu, label='File')

        self.fileMenu.add_command(command=self.OnOpen, label='Open',
                                  accelerator='Ctrl+O')
        self.bind_all('<Control-o>', handler(self.OnOpen))
        self.fileMenu.add_command(command=self.OnEdit, label='Edit Lyrics',
                                  accelerator='Ctrl+E')
        self.editIndex = self.fileMenu.index(tk.END)
        self.bind_all('<Control-e>', handler(self.OnEdit))
        self.fileMenu.add_command(command=self.OnSave, label='Save',
                                  accelerator='Ctrl+S', state=tk.DISABLED)
        self.saveIndex = self.fileMenu.index(tk.END)
        self.bind_all('<Control-s>', handler(self.OnSave))
        self.fileMenu.add_command(command=self.OnCloseEditor,
                                  label='Close Editor', state=tk.DISABLED)
        self.closeEditorIndex = self.fileMenu.index(tk.END)
        self.fileMenu.add_command(command=self.Close, label='Quit',
                                  accelerator='Ctrl+Q')
        self.bind_all('<Control-q>', handler(self.Close))

        # some menu items are only enabled in Edit Mode

        # timing menu
        self.timingMenu = tk.Menu(self.menuBar, tearoff=False)
        self.menuBar.add_cascade(menu=self.timingMenu, label='Timing')
        self.timingIndex = self.menuBar.index(tk.END)
        # Disable timing menu
        self.menuBar.entryconfig(self.timingIndex, state=tk.DISABLED)
        self.timingMenu.add_command(command=self.lyricsEditor.AddPlaceholder,
                               label='Add Timestamp Placeholder',
                               accelerator='Ctrl+Shift+T')
        self.bind_all('<Control-T>',
                      handler(self.lyricsEditor.AddPlaceholder))
        self.timingMenu.add_command(command=self.lyricsEditor.SetTimestamp,
                               label='Set Timestamp',
                               accelerator='Ctrl+T')
        self.bind_all('<Control-t>', handler(self.lyricsEditor.SetTimestamp))

        # playback menu
        playbackMenu = tk.Menu(self.menuBar, tearoff=False)
        self.menuBar.add_cascade(menu=playbackMenu, label='Playback')
        playbackMenu.add_command(command=self.OnPlayPause, label='Play/Pause',
                                 accelerator='Ctrl+P')
        self.bind_all('<Control-p>', handler(self.OnPlayPause))
        playbackMenu.add_command(command=self.OnStop, label='Stop',
                                 accelerator='Ctrl+Shift+P')
        self.bind_all('<Control-P>', handler(self.OnStop))

        # controls
        controlFrame = tk.Frame(self)
        self.playPauseButton = tk.Button(controlFrame,
                                         command=self.OnPlayPause,
                                         text='Play/Pause')
        self.playPauseButton.pack(side=tk.LEFT)
        stopButton = tk.Button(controlFrame, command=self.OnStop, text='Stop')
        stopButton.pack(side=tk.LEFT)
        timestampButton = tk.Button(controlFrame,
                                    command=self.lyricsEditor.SetTimestamp,
                                    text='Set Timestamp')
        timestampButton.pack()
        self.muteButtonVar = tk.IntVar()
        muteButton = tk.Checkbutton(controlFrame, command=self.OnMute,
                                    text='Mute', variable=self.muteButtonVar)
        muteButton.pack(side=tk.RIGHT)
        self.volumeSliderVar = tk.DoubleVar()
        self.volumeSlider = tk.Scale(controlFrame, command=handler(self.OnVol),
                                     from_=0, to=100, length=100,
                                     tickinterval=100, orient=tk.HORIZONTAL,
                                     variable=self.volumeSliderVar)
        self.volumeSlider.pack(side=tk.RIGHT)
        controlFrame.pack(side=tk.BOTTOM, fill=tk.X, expand=0)

        timeFrame = tk.Frame(self)
        self.timeSliderVar = tk.DoubleVar()
        self.timeSlider = tk.Scale(timeFrame, command=handler(self.OnTimeAny),
                                   from_=0, to=1, orient=tk.HORIZONTAL,
                                   tickinterval=10, resolution=1/1000,
                                   variable=self.timeSliderVar)
        self.timeSlider.pack(fill=tk.X, expand=1)
        self.timeLabel = tk.Label(timeFrame, text='0:00/0:00')
        self.timeLabel.pack(side=tk.RIGHT)
        timeFrame.pack(side=tk.BOTTOM, fill=tk.X, expand=0)

        # flag to indicate which mode we're in
        self.editMode = False

        self.timer = None

        self.pack(fill=tk.BOTH, expand=1)

        # currently loaded file
        if filepath is None:
            self.filepath = None
        else:
            self.OpenFile(filepath)


    def UpdateTime(self, updateSliderTime=True):
        length = self.player.Length()
        time = self.player.Tell()
        if updateSliderTime:
            self.timeSlider.config(to=length / 1000)
            self.timeSlider.set(time / 1000)
        self.timeLabel.config(text="{}:{:02}/{}:{:02}".format(
                int(time / 60000), int(time / 1000) % 60,
                int(length / 60000), int(length / 1000) % 60))
        if self.player.playing():
            self.timer = self.after(100, self.UpdateTime)

    def PromptSave(self):
        try:
            if save_dialog():
                self.OnSave()
            return True
        except CancelException:
            return False

    def OnPlayer(self):
        self.UpdateTime()

        if self.player.playing():
            self.timer = self.after(100, self.UpdateTime)

            if self.editMode:
                self.lyricsEditor.focus_set()
                self.lyricsViewer.SetLyrics(self.lyricsEditor.GetLyrics())
        elif self.timer is not None:
            self.after_cancel(self.timer)

        self.lyricsViewer.OnPlayer()

    def OpenFile(self, filepath):
        self.filepath = filepath
        # Show lyrics, if available
        self.lyricsViewer.ClearLyrics()
        haveLyrics = False
        if os.path.splitext(self.filepath)[1] == '.mp3':
            try:
                self.lyricsViewer.SetLyrics(
                    lyrics3v2.load(lyrics3v2.read(self.filepath)))
                haveLyrics = True
            except ValueError:
                pass

        self.player.Load(self.filepath)

        if self.editMode:
            self.lyricsEditor.LoadLyrics(self.lyricsViewer.lyrics)

        # Hide lyrics viewer if there are no lyrics
        if not haveLyrics and not self.editMode:
            self.lyricsViewer.pack_forget()
        else:
            self.lyricsViewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        title = os.path.basename(self.filepath)
        self.parent.title(u'{} - Karaoke-chan'.format(title))

        self.volumeSlider.set(int(self.player.GetVolume() * 100))
        self.UpdateTime()

    def OnOpen(self):
        self.OnStop()

        if self.editMode and self.filepath is not None and not self.PromptSave():
            return

        path = tkFileDialog.askopenfilename(
            defaultextension='.mp3',
            filetypes=[('MP3 files', '*.mp3'), ('All files', '*')])

        if path:
            self.OpenFile(path)

    def OnClose(self):
        self.player.Stop()
        if (self.editMode and self.lyricsEditor.edit_modified() and not
            self.PromptSave()):
                return
        self.Close()

    def OnPlayPause(self):
        if self.player.playing():
            self.player.Pause()
        else:
            self.player.Play()

    def OnStop(self):
        self.player.Stop()
        self.UpdateTime()

    def OnMute(self):
        if self.muteButtonVar.get():
            self.player.SetVolume(0)
        else:
            self.player.SetVolume(self.volumeSlider.get() / 100)

    def OnVol(self):
        vol = self.volumeSliderVar.get()
        self.player.SetVolume(vol / 100)

    def OnEdit(self):
        if self.editMode:
            return
        self.editMode = True

        self.fileMenu.entryconfig(self.editIndex, state=tk.DISABLED)
        self.fileMenu.entryconfig(self.saveIndex, state=tk.NORMAL)
        self.fileMenu.entryconfig(self.closeEditorIndex, state=tk.NORMAL)
        self.menuBar.entryconfig(self.timingIndex, state=tk.NORMAL)

        self.lyricsViewer.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.lyricsEditor.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)

        self.lyricsEditor.LoadLyrics(self.lyricsViewer.lyrics)

        self.lyricsEditor.focus_set()

    def OnSave(self):
        try:
            lyrics3v2.write(self.filepath,
                            lyrics3v2.dump(self.lyricsEditor.GetLyrics()))
            self.lyricsEditor.DiscardEdits()
        except:
            print "write error"

    def OnCloseEditor(self):
        self.player.Stop()

        if self.lyricsEditor.edit_modified() and not self.PromptSave():
            return

        self.editMode = False

        self.fileMenu.entryconfig(self.editIndex, state=tk.NORMAL)
        self.fileMenu.entryconfig(self.saveIndex, state=tk.DISABLED)
        self.fileMenu.entryconfig(self.closeEditorIndex, state=tk.DISABLED)
        self.menuBar.entryconfig(self.timingIndex, state=tk.DISABLED)

        self.lyricsEditor.pack_forget()
        if self.filepath:
            self.OpenFile(self.filepath)

    def OnTimeAny(self):
        current = self.player.Tell()
        slider = self.timeSliderVar.get() * 1000
        if abs(current - slider) < 100:
            return
        self.player.Seek(slider)
        self.UpdateTime(updateSliderTime=False)

    def Close(self):
        self.parent.destroy()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('filepath', nargs='?')
    args = argparser.parse_args()

    root = tk.Tk()
    app = KaraokePlayer(root, filepath=args.filepath)
    root.mainloop()


if __name__ == '__main__':
    main()
