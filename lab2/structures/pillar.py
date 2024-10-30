from Grishanov_id23_3.lab2.structures.canvas import MainCanvas
from threading import Timer


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
