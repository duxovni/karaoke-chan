import audioread
from pygame import mixer
music = mixer.music
import time
import wx
import wx.media as wxm


PAUSED = wxm.MEDIASTATE_PAUSED
PLAYING = wxm.MEDIASTATE_PLAYING


class PyGameMediaCtrl(wx.Control):
    def __init__(self, *args, **kwargs):
        super(PyGameMediaCtrl, self).__init__(*args, **kwargs)
        mixer.init()

    def Load(self, filename):
        with audioread.audio_open(filename) as f:
            self.duration = int(f.duration * 1000)
            self.samplerate = f.samplerate
            self.channels = f.channels
        mixer.quit()
        mixer.init(frequency=self.samplerate, channels=self.channels)
        music.load(filename)
        self.pos = 0

    def Length(self):
        return self.duration

    def Tell(self):
        if music.get_busy():
            return self.pos + music.get_pos()
        else:
            return self.pos

    def GetState(self):
        return PLAYING if music.get_busy() else PAUSED

    def state_change(self):
        wx.PostEvent(self.GetEventHandler(),
                     wx.PyCommandEvent(wxm.EVT_MEDIA_STATECHANGED.typeId,
                                       self.GetId()))

    def Pause(self):
        if music.get_busy():
            self.pos = self.Tell()
            music.stop()
            wx.CallAfter(self.state_change)

    def Stop(self):
        if music.get_busy():
            self.pos = 0
            music.stop()
            wx.CallAfter(self.state_change)

    def Play(self):
        if not music.get_busy():
            music.play(0, self.pos / 1000.0)
            wx.CallAfter(self.state_change)

    def GetVolume(self):
        return music.get_volume()

    def SetVolume(self, vol):
        music.set_volume(vol)

    def GetPlaybackRate(self):
        return self.samplerate

    def Seek(self, pos):
        self.pos = pos
        if music.get_busy():
            music.stop()
            music.play(0, pos / 1000.0)

    def GetBestSize(self):
        return (0, 0)

if __name__ == '__main__':
    main()
