from tkinter import *


class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=500, height=500)
        self.pack()

