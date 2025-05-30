import random
import json
from tkinter import *
from threading import Timer


class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=500, height=500)
        self.pack()


class Pillar:

    def __init__(self, canvas: MainCanvas, max_birds: int, recovery_time: int, x: int, y: int):
        self.max_birds = max_birds
        self.canvas = canvas
        self.recovery_time = recovery_time
        self.count_birds = 0
        self.x = x
        self.break_pillar_flag = False
        self.y = y
        self.post_id = None
        self.beam_id = None
        self.is_fixed = True
        self.check_birds()

    def draw(self):
        self.post_id = self.canvas.create_rectangle(self.x, self.y, self.x + 10, self.y + 200, fill='gray',
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
            timer = Timer(self.recovery_time, self.fix_pillar)
            timer.start()

    def fix_pillar(self):
        self.canvas.itemconfigure(self.beam_id, state='normal')
        self.canvas.itemconfigure(self.post_id, state='normal')
        self.is_fixed = True
        self.break_pillar_flag = False

    def check_birds(self):
        if self.is_fixed:
            if self.count_birds >= self.max_birds:
                self.break_pillar()

        self.canvas.after(100, self.check_birds)


class Bird:

    def __init__(self, canvas: MainCanvas, sitting_time: int, pillars: [Pillar]):
        self.is_leave = False
        self.leave_timer = None
        self.sitting_time = sitting_time
        self.canvas = canvas
        self.x = random.randint(50, 550)
        self.y = random.randint(50, 250)
        self.animation_progress = False
        self.bird_id = None
        self.is_can_fly = True
        self.pillars = pillars
        self.current_pillar = None

    def draw(self):
        self.bird_id = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.coords(self.bird_id, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

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

            animate()

    def can_seat(self):
        return any([pillar.is_fixed for pillar in self.pillars])

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

        self.animation(*random.choice([[i, -10] for i in range(-10, 500, 10)]))

    def choose_random_pillar(self):
        available_pillars = list(filter(lambda x: x.is_fixed, self.pillars))
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
            x = random.randint(10, 490)
            y = random.randint(10, 240)

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
    }
    with open('settings.json', 'w') as settings:
        json.dump(base_settings, settings)


def main():
    root = Tk()
    root.maxsize(500, 500)
    root.minsize(500, 500)
    canvas = MainCanvas(root)
    pillars = []
    for i in range(1, 5):
        pillar = Pillar(canvas, base_settings['PILLARS_DURABILITY'], base_settings['PILLARS_REPAIR_INTERVAL'],
                        70 * i + (50 * (i - 1)), 300)
        pillars.append(pillar)
        pillar.draw()

    birds = []
    for _ in range(base_settings['BIRDS_COUNT']):
        bird = Bird(canvas, random.randint(1, 6), pillars)
        birds.append(bird)
        bird.draw()
        bird.fly()

    root.mainloop()


if __name__ == '__main__':
    main()
