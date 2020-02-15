from bust.bus import Bus
from bust.module import Module
from bust.settings import Settings
from bust.utils import json_parser
from gui.buttons import GuiButtons
from gui.buttons_decl import frame_1_button_data, frame_2_button_data, frame_3_button_data
from gui.gui_defs import GuiGlobals, BustHolder
from gui.frames import GuiFrames
from gui.menus import GuiMenus

json_file = "../example/example_axi.json"
json_dict = json_parser(json_file)
settings = Settings(json_file, json_dict["settings"])
bus = Bus(json_dict["bus"])
module = Module(json_dict["module"], bus, settings)
mh = BustHolder()
mh.module = module
if __name__ == "__main__":
    GuiMenus().cfg()
    guiframes = GuiFrames()
    guiframes.cfg()
    bt = GuiButtons(guiframes.buttonholders)
    mh.bt = bt
    bt.cfg()
    bdata1 = frame_1_button_data(module)
    bdata2 = frame_2_button_data(module)
    bdata3 = frame_3_button_data(module.registers[7], module.registers[7].fields[0])
    bt.set_buttons(bdata1, bt.buttons_dict["Frame1"])
    bt.set_buttons(bdata2, bt.buttons_dict["Frame2"])
    bt.set_buttons(bdata3, bt.buttons_dict["Frame3"])
    GuiGlobals().root.mainloop()
