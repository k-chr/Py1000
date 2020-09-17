from . import QWidget, QObject, QSound, QSoundEffect, path, randint, QUrl

class SoundManager(QObject):

    def __init__(self, parent: QWidget =None):
        self.parent = parent
        self.bg_sound = None

    def play_background_sound(self):
        self.bg_sound = QSoundEffect(self.parent)
        self.bg_sound.setSource(QUrl.fromLocalFile(path.join('sounds', 'background.wav')))
        self.bg_sound.setLoopCount(QSoundEffect.Infinite)
        self.bg_sound.setVolume(0.009)
        self.bg_sound.play()

    def stop_background_sound(self):
        if self.bg_sound is not None:
            self.bg_sound.stop()

    def play_random_card_sound(self):
        num = randint(1,8)
        QSound(path.join('sounds', 'c' + str(num) + '.wav'), self.parent).play()
