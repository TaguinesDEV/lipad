import os
import math
import random
from kivy.config import Config

# Force mobile phone aspect ratio
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, Triangle


class Pipe(Widget):
    width_size = NumericProperty(60)
    gap_size = NumericProperty(150)
    gap_y = NumericProperty(300)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gap_y = random.randint(150, 450)
        self.bind(pos=self.update_canvas, size=self.update_canvas, gap_y=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Cardboard tube palette
            outer_color = (0.55, 0.35, 0.15, 1)
            band_color = (0.40, 0.25, 0.10, 1)
            edge_color = (0.25, 0.15, 0.06, 1)

            x = self.x
            w = self.width_size

            bottom_h = self.gap_y - self.gap_size / 2
            top_pipe_y = self.gap_y + self.gap_size / 2
            top_h = (self.parent.height - top_pipe_y) if self.parent else (640 - top_pipe_y)

            # Outer tubes
            Color(*outer_color)
            Rectangle(pos=(x, 0), size=(w, bottom_h))
            Rectangle(pos=(x, top_pipe_y), size=(w, top_h))

            # Cardboard bands
            band_h = max(10, min(22, w // 3))
            Color(*band_color)
            for i in range(3):
                by = 20 + i * (band_h + 6)
                if by + band_h <= bottom_h:
                    Rectangle(pos=(x, by), size=(w, band_h))

            for i in range(3):
                ty = top_pipe_y + 20 + i * (band_h + 6)
                if ty + band_h <= top_pipe_y + top_h:
                    Rectangle(pos=(x, ty), size=(w, band_h))

            # Rounded caps
            cap_r = w / 2
            Color(*edge_color)
            Ellipse(pos=(x, -cap_r), size=(w, w))
            Ellipse(pos=(x, bottom_h - cap_r), size=(w, w))
            Ellipse(pos=(x, top_pipe_y - cap_r), size=(w, w))
            Ellipse(pos=(x, top_pipe_y + top_h - cap_r), size=(w, w))

            # Subtle outline
            Color(0, 0, 0, 0.35)
            Line(rectangle=(x, 0, w, bottom_h), width=1.2)
            Line(rectangle=(x, top_pipe_y, w, top_h), width=1.2)

    def move(self, speed):
        self.x -= speed



class Bird(Widget):
    # Velocity variables
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    size_radius = NumericProperty(20)
    flap_state = NumericProperty(0)  # Used for wing animation

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, flap_state=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            x, y = self.pos
            r = self.size_radius
            
            # 1. Draw the Body (Elongated Ellipse)
            Color(1, 0.85, 0, 1)  # Main Yellow
            Ellipse(pos=(x, y), size=(r * 2.5, r * 2))
            
            # Body Outline
            Color(0.2, 0.1, 0, 1)
            Line(ellipse=(x, y, r * 2.5, r * 2), width=1.5)

            # 2. Draw the Eye
            Color(1, 1, 1, 1) # White part
            eye_size = r * 0.7
            Ellipse(pos=(x + r * 1.5, y + r * 1.1), size=(eye_size, eye_size))
            Color(0, 0, 0, 1) # Pupil
            Ellipse(pos=(x + r * 1.8, y + r * 1.3), size=(eye_size * 0.4, eye_size * 0.4))

            # 3. Draw the Beak
            Color(1, 0.4, 0, 1) # Orange
            beak_points = [
                x + r * 2.3, y + r * 1.1, # Back
                x + r * 3.1, y + r * 0.8, # Tip
                x + r * 2.3, y + r * 0.5  # Bottom
            ]
            Triangle(points=beak_points)
            Color(0.2, 0.1, 0, 1)
            Line(points=beak_points + [beak_points[0], beak_points[1]], width=1.2)

            # 4. Draw the Wing (with flap animation)
            Color(1, 1, 1, 0.8) # Off-white/pale wing
            wing_y_offset = (r * 0.4) * self.flap_state
            wing_pos = (x + r * 0.2, y + r * 0.6 + wing_y_offset)
            Ellipse(pos=wing_pos, size=(r * 1.2, r * 0.8))
            Color(0.2, 0.1, 0, 0.5)
            Line(ellipse=(wing_pos[0], wing_pos[1], r * 1.2, r * 0.8), width=1)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        # Update flap animation based on time
        self.flap_state = math.sin(Clock.get_time() * 15)


class GameWorld(Widget):
    # Make sure taps restart even if they land on overlay labels
    def on_touch_down(self, touch):
        # If game over, restart on *any* touch inside this GameWorld
        if self.game_over:
            self.reset_game()
            return True

        # Otherwise, treat touch as flap
        self.bird.velocity_y = 7
        if self.sound_flap:
            self.sound_flap.play()
        return True

    def _draw_background(self):
        # Simple floppy-style sky + ground (avoid black default)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.60, 0.85, 1.00, 1)  # sky
            Rectangle(pos=(0, 0), size=self.size)

            Color(0.95, 0.85, 0.55, 1)  # paper ground
            ground_h = 60
            Rectangle(pos=(0, 0), size=(self.width, ground_h))

            Color(0.30, 0.20, 0.10, 0.20)
            # ground line
            Line(points=[0, ground_h, self.width, ground_h], width=2)

            # clouds
            Color(1, 1, 1, 0.75)
            for cx, cy, r in [(70, 460, 22), (180, 510, 26), (290, 460, 20)]:
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

    bird = ObjectProperty(None)
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pipes = []
        self.game_over = False

        # Load sounds using absolute paths to avoid directory issues
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        def load_sound(filename):
            path = os.path.join(base_path, filename)
            sound = SoundLoader.load(path)
            return sound
        self.sound_flap = load_sound('flap.wav')
        self.sound_score = load_sound('score.wav')
        self.sound_hit = load_sound('hit.wav')

        # Initialize UI Labels once
        self._score_label = Label(
            text="0",
            font_size='28sp',
            color=(0, 0, 0, 1),
            bold=True,
            size_hint=(None, None),
            size=(120, 40)
        )
        self._gameover_label = Label(
            text="GAME OVER",
            font_size='30sp',
            color=(0.1, 0.05, 0.0, 1),
            bold=True,
            opacity=0
        )
        self._restart_hint = Label(
            text="Tap to restart",
            font_size='16sp',
            color=(0.1, 0.05, 0.0, 1),
            bold=False,
            opacity=0
        )

        # Ensure background is drawn immediately and stays correct on resize
        self.bind(size=self._on_size, pos=self._on_size)
        Clock.schedule_once(lambda *_: self._draw_background(), 0)

        # Spawn the bird object
        self.bird = Bird(pos=(100, 300))
        self.add_widget(self.bird)
        self.add_widget(self._score_label)
        self.add_widget(self._gameover_label)
        self.add_widget(self._restart_hint)

        # Bind canvas update for score text
        self.bind(score=self.update_score_canvas)

    def _on_size(self, *args):
        self._draw_background()
        self._score_label.pos = (self.width/2 - 60, self.height - 48)
        self._gameover_label.pos = (0, self.height/2 - 25)
        self._gameover_label.width = self.width
        self._restart_hint.pos = (0, self.height/2 - 50)
        self._restart_hint.width = self.width

    def update_score_canvas(self, *args):
        self._score_label.text = str(self.score)
        self._gameover_label.opacity = 1 if self.game_over else 0
        self._restart_hint.opacity = 1 if self.game_over else 0

    def spawn_pipe(self, *args):
        if self.game_over:
            return
        new_pipe = Pipe(x=self.width)
        self.add_widget(new_pipe)
        self.pipes.append(new_pipe)



    def update(self, dt):
        if self.game_over:
            return

        # Apply gravity acceleration
        self.bird.velocity_y -= 0.35
        self.bird.move()

        # Handle floor and ceiling collisions
        if self.bird.y <= 0 or (self.bird.top >= self.height):
            self.end_game()

        # Update and check pipes
        pipes_to_remove = []
        for pipe in self.pipes:
            pipe.move(4)  # Speed of pipes moving left

            # Collision Check Logic
            bird_center_x = self.bird.x + self.bird.size_radius
            bird_center_y = self.bird.y + self.bird.size_radius

            # Check if bird is horizontally inside the pipe width
            if (
                # Shrink hitbox by 5 pixels for "forgiveness"
                pipe.x < bird_center_x + (self.bird.size_radius - 5)
                and pipe.x + pipe.width_size > bird_center_x - (self.bird.size_radius - 5)
            ):
                lower_limit = pipe.gap_y - pipe.gap_size / 2
                upper_limit = pipe.gap_y + pipe.gap_size / 2
                # Trigger game over if bird hits top or bottom sections of the pipe
                if bird_center_y - self.bird.size_radius < lower_limit or bird_center_y + self.bird.size_radius > upper_limit:
                    self.end_game()

            # Point scoring logic (when bird crosses right edge of a pipe)
            if not hasattr(pipe, "passed") and pipe.x + pipe.width_size < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.sound_score:
                    self.sound_score.play()
                print(f"Score: {self.score}")

            # Queue off-screen pipes for deletion
            if pipe.x < -pipe.width_size:
                pipes_to_remove.append(pipe)

        # Clean up old widgets
        for pipe in pipes_to_remove:
            self.remove_widget(pipe)
            self.pipes.remove(pipe)

    def end_game(self):
        self.game_over = True
        if self.sound_hit:
            self.sound_hit.play()
        self.update_score_canvas()
        print("Game Over! Click anywhere to restart.")

    def reset_game(self):
        # Clear current level state
        for pipe in self.pipes:
            self.remove_widget(pipe)
        self.pipes.clear()

        self.bird.pos = (100, 300)
        self.bird.velocity_y = 0
        self.score = 0
        self.game_over = False
        self.update_score_canvas()


class FloppyBirdApp(App):
    def build(self):
        game = GameWorld()
        # Run update function 60 times a second
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        # Spawn a new obstacle pipe every 1.8 seconds
        Clock.schedule_interval(game.spawn_pipe, 1.8)
        return game


if __name__ == "__main__":
    FloppyBirdApp().run()
