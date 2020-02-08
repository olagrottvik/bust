import tkinter as tk
from collections import defaultdict
from tkinter import ttk as ttk

from gui.gui_defs import GuiGlobals, GuiComponent
from gui.buttons_decl import frame_buttons


class GuiButtons(GuiComponent):
    def __init__(self, buttonholders):
        """ need parents for placement of buttons."""
        self.buttonholders = buttonholders
        self.buttons_all = []
        self.buttons_dict = defaultdict(
            lambda: defaultdict()
        )  # dynamic 2-level dict, enables creation of buttons_dict[key1][key2] = something type operations

        self.placed_buttons = defaultdict(lambda: defaultdict())

    def cfg(self):
        self.load_buttons()
        self.place_buttons()

    def place_buttons(self):
        for framename, holder in self.buttonholders.items():
            for cnt, (name, button_instance) in enumerate(
                self.buttons_dict[framename].items()
            ):
                col = 0
                button_instance.place(cnt, col)
                self.placed_buttons[framename][name] = button_instance

    def load_buttons(self):
        for framename, holder in self.buttonholders.items():
            inframe_buttons = self._get_button_dicts(framename)
            for text, button in inframe_buttons.items():
                buttonclass = dispatch_button(button)
                b = buttonclass(holder, text)
                # same object to both collections, to keep the option of simply looping through the buttons,
                # or refer to them by frame name
                self.buttons_all.append(b)
                self.buttons_dict[framename][text] = b

    def _get_button_dicts(self, name):
        """lookup for buttons"""
        buttons = {}
        if name in frame_buttons:
            buttons = frame_buttons[name]
        return buttons


class ButtonTypes:
    def __iter__(self):
        return iter([StringButton, DropDownButton, SeparatorButton])


def dispatch_button(button):
    """manual dynamic dispatch"""
    t = [impl for impl in ButtonTypes() if button == impl.type][0]
    print("from", button, "selected", t)
    return t


class SingleButton:
    """! @brief Class for all single buttons with a label."""

    label: ttk.Widget
    box: ttk.Widget
    type: str
    row_offset = 0
    def place(self, row, col):
        self.label.grid(row=row + self.row_offset, column=col, sticky=tk.W + tk.E)
        self.box.grid(row=row + self.row_offset, column=col + 1, pady=2, padx=2, sticky=tk.W + tk.E)


class StringButton(SingleButton):
    type = "string"

    def __init__(self, parent, text):
        self.box = ttk.Entry(parent)
        self.label = ttk.Label(parent, text=text)


class DropDownButton(SingleButton):
    type = "dropdown"

    def __init__(self, parent, text):
        self.box = ttk.Combobox(parent)
        self.label = ttk.Label(parent, text=text)


class SeparatorButton(SingleButton):
    type = "separator"

    def __init__(self, parent, text):
        self.box = ttk.Separator(parent, orient="horizontal")
        self.label = ttk.Label(parent, text=text)

    def place(self, row, col):
        self.label.grid(row=row + self.row_offset, column=col, sticky=tk.W + tk.E)
        self.box.grid(row=row+1 + self.row_offset, column=col, columnspan=2, pady=2, padx=2, sticky=tk.W + tk.E)
        SingleButton.row_offset += 1

if __name__ == "__main__":
    from gui.frames import GuiFrames
    from gui.menus import GuiMenus

    GuiMenus().cfg()
    guiframes = GuiFrames()
    guiframes.cfg()
    bg = GuiButtons(guiframes.buttonholders)
    bg.cfg()
    GuiGlobals().root.mainloop()
