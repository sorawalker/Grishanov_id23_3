from tkinter import *
from constants import *
from math import cos, sin, radians


class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.pack()
        self.angle = 0
        self.main_circle_id = self.draw_main_circle()
        self.moving_dot_id = self.draw_moving_dot()

    def draw_main_circle(self) -> int:
        circle_x1 = WINDOW_WIDTH / 2 - CIRCLE_RADIUS
        circle_x2 = WINDOW_WIDTH / 2 + CIRCLE_RADIUS
        circle_y1 = WINDOW_HEIGHT / 2 - CIRCLE_RADIUS
        circle_y2 = WINDOW_HEIGHT / 2 + CIRCLE_RADIUS

        return self.create_oval(circle_x1, circle_y1, circle_x2, circle_y2)

    def draw_moving_dot(self) -> int:
        dot_x1 = WINDOW_WIDTH / 2 - CIRCLE_RADIUS - DOT_RADIUS
        dot_x2 = WINDOW_WIDTH / 2 - CIRCLE_RADIUS + DOT_RADIUS
        dot_y1 = WINDOW_HEIGHT / 2 - DOT_RADIUS
        dot_y2 = WINDOW_HEIGHT / 2 + DOT_RADIUS

        return self.create_oval(dot_x1, dot_y1, dot_x2, dot_y2, outline='aqua', fill='aqua')

    def move_dot(self) -> None:
        if self.angle >= 360:
            self.angle = 0

        x = WINDOW_WIDTH / 2 - CIRCLE_RADIUS * cos(radians(self.angle))
        y = WINDOW_HEIGHT / 2 - CIRCLE_RADIUS * sin(radians(self.angle))

        self.coords(self.moving_dot_id, x - DOT_RADIUS, y - DOT_RADIUS, x + DOT_RADIUS, y + DOT_RADIUS)

        self.angle += DOT_DIRECTION * DOT_SPEED
        self.after(25, self.move_dot)


def main():
    root = Tk()
    root.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    canvas = MainCanvas(root)
    root.after(50, canvas.move_dot)
    root.mainloop()


if __name__ == '__main__':
    main()
