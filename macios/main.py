from kivy.config import Config

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

from floppy_bird import GameWorld


class MainMenuScreen(Screen):
    def on_enter(self):
        # Rebuild each time to ensure correct sizing
        self.clear_widgets()

        btn = Button(text='Start Floppy Bird', size_hint=(None, None), size=(260, 70), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        def start_game(_btn):
            self.manager.current = 'game'

        btn.bind(on_release=start_game)
        self.add_widget(btn)


class GameScreen(Screen):
    def on_enter(self):
        if not hasattr(self, 'gameworld'):
            self.gameworld = GameWorld()
            self.add_widget(self.gameworld)

        # Schedule the game update and pipe spawning
        self._dt_event = Clock.schedule_interval(self.gameworld.update, 1.0 / 60.0)
        self._spawn_event = Clock.schedule_interval(self.gameworld.spawn_pipe, 1.8)

    def on_leave(self):
        # Properly cancel the intervals when leaving the screen to prevent crashes
        if hasattr(self, '_dt_event'):
            self._dt_event.cancel()
        if hasattr(self, '_spawn_event'):
            self._spawn_event.cancel()


class RootApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm


if __name__ == '__main__':
    RootApp().run()
