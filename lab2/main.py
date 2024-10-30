import random
from tkinter import *

from structures.bird import Bird
from structures.canvas import MainCanvas
from structures.pillar import Pillar
import json

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
    for i in range(1, 6):
        pillar = Pillar(canvas, base_settings['PILLARS_DURABILITY'], base_settings['PILLARS_REPAIR_INTERVAL'], 70 * i + (50 * (i - 1)), 300)
        pillars.append(pillar)
        pillar.draw()

    birds = []
    for _ in range(base_settings['BIRDS_COUNT']):
        bird = Bird(canvas, random.randint(1,6), pillars)
        birds.append(bird)
        bird.draw()
        bird.fly()

    root.mainloop()


if __name__ == '__main__':
    main()
