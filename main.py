from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.core.audio.audio_sdl2 import SoundSDL2

class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)

        self.win_w = Window.size[0]
        self.win_h = Window.size[1]

        ''' Sizes '''
        self.player_size = (self.win_w * .06, self.win_h * .08)
        self.fire_size = (self.player_size[0] / 10, self.player_size[1] / 2)
        self.enemy_size = (self.win_w * .06, self.win_h * .05)
        self.life_size = (self.win_w * .035, self.win_h * .035)

        self.sounds = {
            'fire': SoundSDL2(source='assets/fire.wav'),
            'player_death': SoundSDL2(source='assets/player_death.wav'),
            'foe_death': SoundSDL2(source='assets/foe_death.wav'),
            'theme': SoundSDL2(source='assets/theme.mp3'),
            'gameover': SoundSDL2(source='assets/gameover.mp3')
        }

class MainApp(App):
    def build(self):
        self.window_size = Window.size

if __name__ == '__main__':
    MainApp().run()