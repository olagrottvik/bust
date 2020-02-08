import tkinter as tk
from tkinter import ttk as ttk

from gui.gui_defs import GuiGlobals, GuiComponent


class FrameABC:
    """Important features for a frame"""

    title: str
    frame: ttk.Widget
    buttonholder: ttk.Widget  # the frame itself or the the child in the frame that will hold its buttons


class Frame1(FrameABC):
    def __init__(self):
        framewidth = GuiGlobals().framewidth
        frameheight = GuiGlobals().frameheight

        self.title = "I. Definitions"
        self.frame = ttk.Frame(GuiGlobals().root, width=framewidth, height=frameheight)
        self.buttonholder = self.frame


class Frame2(FrameABC):
    def __init__(self):
        framewidth = GuiGlobals().framewidth
        frameheight = GuiGlobals().frameheight

        self.title = "II. Module"
        self.frame = ttk.Frame(GuiGlobals().root, width=framewidth, height=frameheight)
        self.pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        pane_content_left = ttk.Labelframe(
            self.pane, width=framewidth // 2, height=frameheight // 2
        )
        pane_content_right = ttk.Labelframe(
            self.pane, text="Registers", width=framewidth // 2, height=frameheight // 2,
        )
        self.pane.add(pane_content_left)
        self.pane.add(pane_content_right)
        self.pane.pack(expand=True, fill="both")

        self.buttonholder = pane_content_left


class Frame3(FrameABC):
    def __init__(self):
        framewidth = GuiGlobals().framewidth
        frameheight = GuiGlobals().frameheight

        self.title = "III. Register"
        self.frame = ttk.Frame(GuiGlobals().root, width=framewidth, height=frameheight)
        self.buttonholder = self.frame


class GuiFrames(GuiComponent):
    def __init__(self):
        framewidth = GuiGlobals().framewidth
        frameheight = GuiGlobals().frameheight

        self.panes = ttk.Notebook(
            GuiGlobals().root, width=framewidth, height=frameheight
        )

        self.frames = [Frame1(), Frame2(), Frame3()]
        self.buttonholders = {
            type(frame).__name__: frame.buttonholder
            for frame in self.frames
            if hasattr(frame, "buttonholder")
        }

    def cfg(self):
        all_panes = [(frame.frame, frame.title) for frame in self.frames]
        for pane, title in all_panes:
            self.panes.add(pane, text=title)
        self.panes.pack(fill=tk.X)
