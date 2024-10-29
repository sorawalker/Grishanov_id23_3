from tkinter import *

from Grishanov_id23_3.lab2.structures.bird import Bird
from Grishanov_id23_3.lab2.structures.canvas import MainCanvas
from Grishanov_id23_3.lab2.structures.pillar import Pillar


def main():
    root = Tk()
    root.maxsize(500, 500)
    root.minsize(500, 500)
    canvas = MainCanvas(root)
    pillars = []
    for i in range(1, 5):
        pillar = Pillar(canvas, 3, 5, 70 * i + (50 * (i - 1)), 300)
        pillars.append(pillar)
        pillar.draw()

    birds = []
    for _ in range(10):
        bird = Bird(canvas, 5, pillars)
        birds.append(bird)
        bird.draw()
        bird.fly()

    root.mainloop()


if __name__ == '__main__':
    main()
