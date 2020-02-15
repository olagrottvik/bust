import tkinter as tk
from collections import namedtuple

from gui.gui_utils import Singleton


@Singleton
class GuiGlobals:
    def __init__(self):
        self.root = tk.Tk()
        self.framewidth = self.root.winfo_screenwidth() // 2
        self.frameheight = (9 * self.framewidth) // 16


class GuiComponent:
    def cfg(self):
        raise NotImplementedError


