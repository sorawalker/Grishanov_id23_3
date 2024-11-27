import random
import json
from tkinter import *
from threading import Timer

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

        self.root = root
        self.is_paused = False
        self.bind("<Button-1>", self.on_click)
        self.pillars = []
        self.birds = []
        self.auto_spawn_bird_timer = None
        self.repair_timer = None
        self.bird_spawn_interval = base_settings['BIRDS_SPAWN_INTERVAL']
        self.pillar_repair_interval = base_settings['PILLARS_REPAIR_INTERVAL']
        self.pillar_durability = base_settings['PILLARS_DURABILITY']
        self.bird_spawn_timer = None

        self.create_controls()

        self.init_pillars()
        self.init_birds()
        self.auto_spawn_bird()

    def create_controls(self):
        control_frame = Frame(self.root)
        control_frame.pack(side=TOP, fill=X, pady=10)

        Label(control_frame, text="Pillar Durability:").pack(side=LEFT, padx=5)
        self.pillar_durability_box = Spinbox(control_frame, from_=1, to=15, increment=1, width=5,
                                             command=self.update_pillar_durability)
        self.pillar_durability_box.pack(side=LEFT, padx=5)
        self.pillar_durability_box.delete(0, END)
        self.pillar_durability_box.insert(0, str(self.pillar_durability))

        Label(control_frame, text="Pillar Repair Interval:").pack(side=LEFT, padx=5)
        self.pillar_spawn_interval_box = Spinbox(control_frame, from_=1, to=15, increment=1, width=5,
                                                 command=self.update_pillar_repair_interval)
        self.pillar_spawn_interval_box.pack(side=LEFT, padx=5)
        self.pillar_spawn_interval_box.delete(0, END)
        self.pillar_spawn_interval_box.insert(0, str(self.pillar_repair_interval))

        Label(control_frame, text="Bird Spawn Interval:").pack(side=LEFT, padx=5)
        self.bird_spawn_interval_box = Spinbox(control_frame, from_=1, to=15, increment=1, width=5,
                                               command=self.update_bird_spawn_interval)
        self.bird_spawn_interval_box.pack(side=LEFT, padx=5)
        self.bird_spawn_interval_box.delete(0, END)
        self.bird_spawn_interval_box.insert(0, str(self.bird_spawn_interval))

        self.pause_button = Button(control_frame, text="Pause", command=self.pause_handler).pack(side=LEFT, padx=5)

    def pause_handler(self):
        self.is_paused = not self.is_paused

    def spawn_bird(self):
        bird = Bird(self, random.randint(1, 6))
        self.birds.append(bird)
        bird.draw()
        bird.fly()

    def auto_spawn_bird(self):
        def spawn_bird_with_timer():
            self.spawn_bird()
            self.auto_spawn_bird()

        timer = Timer(self.bird_spawn_interval, spawn_bird_with_timer)
        timer.start()

    def update_pillar_durability(self):
        try:
            self.pillar_durability = int(self.pillar_durability_box.get())
        except ValueError:
            pass

    def update_bird_spawn_interval(self):
        try:
            self.bird_spawn_interval = int(self.bird_spawn_interval_box.get())
        except ValueError:
            pass

    def update_pillar_repair_interval(self):
        try:
            self.pillar_repair_interval = int(self.pillar_spawn_interval_box.get())
        except ValueError:
            pass

    def on_click(self, event):
        x, y = event.x, event.y

        new_pillar = Pillar(self, x,
                            y)
        self.pillars.append(new_pillar)
        new_pillar.draw()

    def init_pillars(self):
        for i in range(1, 6):
            pillar = Pillar(self,
                            70 * i + (50 * (i - 1)), WINDOW_HEIGHT - 200)
            self.pillars.append(pillar)
            pillar.draw()
        self.pack()

    def init_birds(self):
        for _ in range(base_settings['BIRDS_COUNT']):
            self.spawn_bird()
        self.pack()


class Pillar:

    def __init__(self, canvas: MainCanvas, x: int, y: int):
        self.canvas = canvas
        self.count_birds = 0
        self.x = x
        self.break_pillar_flag = False
        self.y = y
        self.repair_timer = None
        self.post_id = None
        self.beam_id = None
        self.is_fixed = True
        self.check_birds()

    def draw(self):
        self.post_id = self.canvas.create_rectangle(self.x, self.y, self.x + 10, WINDOW_HEIGHT, fill='gray',
                                                    outline='gray')
        self.beam_id = self.canvas.create_rectangle(self.x - 30, self.y, self.x + 40, self.y + 10, fill='gray',
                                                    outline='gray')

    def increase_birds_count(self):
        self.count_birds += 1

    def decrease_birds_count(self):
        self.count_birds -= 1

    def break_pillar(self):
        if not self.break_pillar_flag:
            self.canvas.itemconfigure(self.beam_id, state='hidden')
            self.canvas.itemconfigure(self.post_id, state='hidden')
            self.is_fixed = False
            self.break_pillar_flag = True
            self.repair_timer = Timer(self.canvas.pillar_repair_interval, self.fix_pillar)
            self.repair_timer.start()

    def fix_pillar(self):
        self.canvas.itemconfigure(self.beam_id, state='normal')
        self.canvas.itemconfigure(self.post_id, state='normal')
        self.is_fixed = True
        self.break_pillar_flag = False

    def check_birds(self):
        if self.is_fixed:
            if self.count_birds >= self.canvas.pillar_durability:
                self.break_pillar()

        self.canvas.after(100, self.check_birds)


class Bird:

    def __init__(self, canvas: MainCanvas, sitting_time: int):
        self.is_leave = False
        self.leave_timer = None
        self.sitting_time = sitting_time
        self.canvas = canvas
        self.x = random.randint(50, WINDOW_WIDTH - 200)
        self.y = -100
        self.animation_progress = False
        self.bird_id = None
        self.is_can_fly = True
        self.current_pillar = None
        self.check_pause()

    def draw(self):
        self.bird_id = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.coords(self.bird_id, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

    def check_pause(self):
        if self.leave_timer is not None:
            if self.canvas.is_paused:
                self.leave_timer.cancel()
            else:
                try:
                    self.leave_timer.start()
                except RuntimeError:
                    pass

        self.canvas.after(50, self.check_pause)

    def animation(self, x, y, on_animation_ended=None):
        self.is_can_fly = False
        if not self.animation_progress:
            self.animation_progress = True
            dx = x - self.x
            dy = y - self.y
            self.x = x
            self.y = y
            length = (dx ** 2 + dy ** 2) ** .5
            step = 10
            step_x = step / length * dx
            step_y = step / length * dy

            progress = 0

            def animate():
                if not self.canvas.is_paused:
                    nonlocal progress
                    progress += step
                    if progress < length:
                        self.canvas.move(self.bird_id, step_x, step_y)
                        self.canvas.after(40, animate)
                    else:
                        self.canvas.coords(self.bird_id, x - 10, y - 10, x + 10, y + 10)
                        self.animation_progress = False
                        if self.current_pillar is None and not self.is_leave:
                            self.is_can_fly = True
                            if self.can_seat():
                                self.choose_random_pillar()
                            else:
                                self.fly()
                        if on_animation_ended is not None:
                            on_animation_ended()
                else:
                    self.canvas.after(50, animate)

            animate()

    def can_seat(self):
        return any([pillar.is_fixed for pillar in self.canvas.pillars])

    def is_pillar_broken(self):
        if not self.current_pillar.is_fixed:
            if self.leave_timer is not None:
                self.leave_timer.cancel()
            self.is_can_fly = True
            self.fly_away()
            self.current_pillar = None
        elif self.current_pillar is not None:
            self.canvas.after(100, self.is_pillar_broken)

    def fly_away(self):
        self.fly()
        self.current_pillar.decrease_birds_count()

    def leave(self):
        self.is_leave = True
        self.is_can_fly = True
        self.leave_timer = None

        self.animation(*random.choice([[i, -10] for i in range(-10, 500, 10)]))

    def choose_random_pillar(self):
        available_pillars = list(filter(lambda x: x.is_fixed, self.canvas.pillars))
        self.current_pillar = available_pillars[random.randint(0, len(available_pillars) - 1)]
        if self.current_pillar.is_fixed:
            self.is_can_fly = False

            def on_animation():
                self.current_pillar.increase_birds_count()
                self.leave_timer = Timer(self.sitting_time, self.leave)
                self.leave_timer.start()
                self.is_pillar_broken()

            self.animation(
                random.randrange(self.current_pillar.x - 30, self.current_pillar.x + 30, random.randint(1, 10)),
                self.current_pillar.y, on_animation_ended=on_animation)
        else:
            self.current_pillar = None
            self.fly()

    def fly(self):
        if self.is_can_fly and not self.is_leave:
            x = random.randint(10, 1200)
            y = random.randint(10, 700)

            def on_animation():
                self.canvas.after(50, self.fly)

            self.animation(x, y, on_animation_ended=on_animation)


try:
    with open("settings.json", 'r') as settings:
        base_settings = json.load(settings)
except FileNotFoundError:
    base_settings = {
        'BIRDS_COUNT': 5,
        'PILLARS_DURABILITY': 2,
        'PILLARS_REPAIR_INTERVAL': 5,
        'BIRD_SPAWN_INTERVAL': 3,
    }
    with open('settings.json', 'w') as settings:
        json.dump(base_settings, settings)


def main():
    root = Tk()
    root.maxsize(1280, 768)
    root.minsize(1280, 768)
    canvas = MainCanvas(root)
    root.mainloop()


if __name__ == '__main__':
    main()
