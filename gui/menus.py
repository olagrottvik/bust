import tkinter as tk

from gui.gui_defs import GuiGlobals, GuiComponent


class GuiMenus(GuiComponent):
    def __init__(self):
        self.menu = tk.Menu(GuiGlobals().root)
        self.filemenu = tk.Menu(self.menu)
        self.specialmenu = tk.Menu(self.menu)

    def cfg(self):
        GuiGlobals().root.config(menu=self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.menu.add_cascade(label="Specials", menu=self.specialmenu)

        self.register_commands()

    def register_commands(self):
        self.specialmenu.add_command(
            label="Reverse field order", command=lambda x: print("ut")
        )
        self.filemenu.add_command(label="Quit", command=GuiGlobals().root.quit)