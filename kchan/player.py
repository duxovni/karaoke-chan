import audioread
from pygame import mixer
music = mixer.music


class Player(object):
    def __init__(self, state_callback):
        self.state_callback = state_callback
        self.duration = 0
        mixer.init()
        self.has_music = False

    def Load(self, filename):
        with audioread.audio_open(filename) as f:
            self.duration = int(f.duration * 1000)
            self.samplerate = f.samplerate
            self.channels = f.channels
        mixer.quit()
        mixer.init(frequency=self.samplerate, channels=self.channels)
        music.load(filename)
        self.pos = 0
        self.has_music = True

    def Length(self):
        return self.duration

    def Tell(self):
        if self.has_music:
            if music.get_busy():
                return self.pos + music.get_pos()
            else:
                return self.pos
        return 0

    def playing(self):
        return self.has_music and music.get_busy()

    def state_change(self):
        self.state_callback()

    def Pause(self):
        if self.has_music and music.get_busy():
            self.pos = self.Tell()
            music.stop()
            self.state_change()

    def Stop(self):
        if self.has_music:
            self.pos = 0
            music.stop()
            self.state_change()

    def Play(self):
        if self.has_music and not music.get_busy():
            music.play(0, self.pos / 1000.0)
            self.state_change()

    def GetVolume(self):
        return music.get_volume()

    def SetVolume(self, vol):
        music.set_volume(vol)

    def GetPlaybackRate(self):
        return self.samplerate

    def Seek(self, pos):
        if not self.has_music:
            return
        self.pos = pos
        if music.get_busy():
            music.stop()
            music.play(0, pos / 1000.0)
        self.state_change()
