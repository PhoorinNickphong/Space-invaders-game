from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'fullscreen', False)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.core.audio.audio_sdl2 import SoundSDL2
from kivy.graphics import Rectangle,Color,InstructionGroup, BindTexture
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.button import Button

import random

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

        self.player_init = (self.win_w / 2 - 25, self.win_h / 6)

        self.pressed = set()
        self.firing = False
        self.fires = []
        self.enemies = []
        self.lifes = []
        self.buttons = []
        self.deads = []
        self.move_speed = (self.win_w * self.win_h) * .001
        self.kill_count = 1
        self.dead = False

        self.sounds['theme'].play()

        self.groups = {
            'foes': InstructionGroup(),
            'bullets': InstructionGroup(),
            'lifes': InstructionGroup(),
            'explosions': InstructionGroup(),
            'buttons': InstructionGroup()
        }

        self.groups['bullets'].add(Color(0, .7, 1))

        self.canvas.add(self.groups['foes'])
        self.canvas.add(self.groups['lifes'])
        self.canvas.add(self.groups['explosions'])
        self.canvas.after.add(self.groups['bullets'])

        fire_tex = Image(source='images/firing.png').texture.get_region(0, 0, 32, 32)
        
        self.spawn_player()

        self.kill_lbl = Label(text='Score: 0', pos=(self.life_size[0], self.win_h - self.life_size[1] * 4), font_size=30)
        self.add_widget(self.kill_lbl)

        self.restore()

        Clock.schedule_interval(self.start, 0)

    def controller(self, method):
        if method == 'keyboard':
            self.method = method
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._keyboard_down)
            self._keyboard.bind(on_key_up=self._keyboard_up)
        elif method == 'buttons':
            self.method = method
            self.buttons = [
                Button(text='Left', pos=(self.win_w - (self.win_w * .03) - (self.win_w * .1) * 2.1, self.win_h * .1), size=(self.win_w * .1, self.win_h * .1), id='left'),
                Button(text='Right', pos=(self.win_w - (self.win_w * .03) - self.win_w * .1, self.win_h * .1), size=(self.win_w * .1, self.win_h * .1), id='right'),
                Button(text='Fire', pos=(self.win_w * .03, self.win_h * .1), size=(self.win_w * .1, self.win_h * .1), id='spacebar')
            ]

            for btn in self.buttons:
                btn.bind(state=self._key_press)
                self.add_widget(btn)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._keyboard_down)
        self._keyboard.unbind(on_key_up=self._keyboard_up)
        self._keyboard = None

    def _keyboard_down(self, keyboard, keycode, text, mod):
        self.pressed.add(keycode[1])

    def _keyboard_up(self, keyboard, keycode):
        if keycode[1] in self.pressed:
            self.pressed.remove(keycode[1])

    def _key_press(self, btn, state=None):
        if btn.id in self.pressed:
            self.pressed.remove(btn.id)
        else:
            self.pressed.add(btn.id)
    
    def remove_obj(self, obj):
        self.canvas.remove(obj)

    def spawn_player(self, pos=None):
        with self.canvas:
            self.player = Rectangle(size=self.player_size, pos=self.player_init, source='images/spaceship.png')

    def spawn_enemy(self):
        posx = random.randint(int(self.enemy_size[0]), int(self.win_w - self.enemy_size[0]))
        self.groups['foes'].add(Rectangle(pos=(posx, self.win_h), size=self.enemy_size, source='images/enemy.png', group='enemy'))

    def stop_firing(self, ms):
        self.firing = False

    def fire(self):
        self.firing = True
        self.sounds['fire'].volume = .1
        self.sounds['fire'].play()

        self.groups['bullets'].add(Rectangle(pos=(self.player.pos[0] + self.player_size[0] / 2.2, self.player.pos[1] + self.player.size[1]), size=self.fire_size))
        Clock.schedule_once(self.stop_firing, .1)

    def explode(self, obj):
        tex = Image(source='images/explosion_animate.png').texture
        tex = tex.get_region(0, 0, 32, 32)
        x = Rectangle(size=obj.size, pos=obj.pos, texture=tex)

    def remove_explosion(self, ms):
        for dead in self.deads:
            dead.size = (0, 0)

    def restore(self, btn=None):
        self.life_count = 3
        self.kill_count = 0
        self.sounds['theme'].play()
        for x in range(self.life_count):
            if len(self.get_children('lifes')) < self.life_count:
                if len(self.get_children('lifes')) == 0:
                    self.groups['lifes'].add(Rectangle(size=self.life_size, pos=self.life_size, source='images/life.png'))
                else:
                    self.groups['lifes'].add(Rectangle(size=self.life_size, pos=(self.get_children('lifes')[-1].pos[0] + self.get_children('lifes')[-1].size[0], self.life_size[1]), source='images/life.png'))

    def show_over(self, ms):
        #self.canvas.remove(self.explosion)
        #self.explosion = False
        self.remove_obj(self.explosion)
        self.life_count = 3
        manager.current = 'GameOver'

    def clear(self):
        self.player.pos = self.player_init
        for enemy in self.enemies:
            self.canvas.remove(enemy)
        for fire in self.fires:
            self.canvas.remove(fire)


class MainApp(App):
    def build(self):
        self.window_size = Window.size

if __name__ == '__main__':
    MainApp().run()