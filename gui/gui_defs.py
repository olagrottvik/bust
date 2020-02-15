import tkinter as tk

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


@Singleton
class BustHolder:
    pass


class GuiInititializer:
    """
    Initialize the globals required to connect
    with the bust objects.
    """
    def __init__(self, module, buttons):
        bh = BustHolder()
        bh.module = module
        bh.bt = buttons
