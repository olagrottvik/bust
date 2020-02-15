import tkinter as tk
from collections import defaultdict
from functools import partial
from tkinter import ttk as ttk

from gui.buttons_decl import frame_buttons
from gui.callbacks import frame_callbacks
from gui.gui_defs import GuiComponent


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
        self.register_callbacks()

    def register_callbacks(self):
        for framename, button_dict in self.buttons_dict.items():
            if framename in frame_callbacks:
                for button_name, fun in frame_callbacks[framename].items():
                    self.buttons_dict[framename][button_name].bind(fun)

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

    @staticmethod
    def set_buttons(button_vals, buttons_in_frame):
        for k, v in buttons_in_frame.items():
            if k in button_vals:
                tmp = button_vals[k]
                if type(tmp) is tuple:
                    v.setvalue(*tmp)
                else:
                    v.setvalue(tmp)

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
    return t


class SingleButton:
    """! @brief Class for all single buttons with a label."""

    label: ttk.Widget
    box: ttk.Widget
    type: str
    row_offset = 0

    def place(self, row, col):
        self.label.grid(row=row + self.row_offset, column=col, sticky=tk.W + tk.E)
        self.box.grid(
            row=row + self.row_offset,
            column=col + 1,
            pady=2,
            padx=2,
            sticky=tk.W + tk.E,
        )

    def getvalue(self):
        return None

    def setvalue(self, value, *args):
        pass


class StringButton(SingleButton):
    type = "string"

    def __init__(self, parent, text):
        self.box = ttk.Entry(parent)
        self.label = ttk.Label(parent, text=text)

    def getvalue(self):
        return self.box.get()

    def setvalue(self, value, *args):
        self.box.delete(0, tk.END)
        self.box.insert(0, str(value))


class DropDownButton(SingleButton):
    type = "dropdown"

    def __init__(self, parent, text):
        self.box = ttk.Combobox(parent, state="readonly")
        self.label = ttk.Label(parent, text=text)
        self._opts = []  # must be a list to keep ordering.

    def getvalue(self):
        return self.box.get()

    def setvalue(self, value, *args):
        try:
            # duck typing for optlist
            optlist = args[0]
            for elem in optlist:
                if elem not in self._opts:
                    self._opts.append(str(elem))
        except IndexError:
            pass
        self.box["values"] = list(self._opts)
        self.box.set(value)

    def bind(self, callback):
        callback_f = partial(callback, self)
        self.box.bind(
            "<<ComboboxSelected>>", callback_f, add=True
        )  # add instead of overwrite


class SeparatorButton(SingleButton):
    type = "separator"

    def __init__(self, parent, text):
        self.box = ttk.Separator(parent, orient="horizontal")
        self.label = ttk.Label(parent, text=text)

    def place(self, row, col):
        self.label.grid(row=row + self.row_offset, column=col, sticky=tk.W + tk.E)
        self.box.grid(
            row=row + 1 + self.row_offset,
            column=col,
            columnspan=2,
            pady=2,
            padx=2,
            sticky=tk.W + tk.E,
        )
        SingleButton.row_offset += 1


if __name__ == "__main__":
    pass
    # from gui.frames import GuiFrames
    # from gui.menus import GuiMenus
    #
    # GuiMenus().cfg()
    # guiframes = GuiFrames()
    # guiframes.cfg()
    # bg = GuiButtons(guiframes.buttonholders)
    # bg.cfg()
    # GuiGlobals().root.mainloop()
