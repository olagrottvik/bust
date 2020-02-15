from functools import partial

from gui.buttons_decl import frame_3_button_data
from gui.frames import Frame2
from gui.gui_defs import BustHolder
from gui.gui_utils import get_register_from_name


def register_select(button, event):
    print("called register select!", event)
    val = button.getvalue()
    print("my value is", val)
    module = BustHolder().module
    reg = get_register_from_name(module, val)
    fields = reg.fields
    if fields:
        print("found fields", fields)
        bdata3 = frame_3_button_data(reg, reg.fields[0])
    else:
        bdata3 = frame_3_button_data(reg)
    _update_frame3_buttons(bdata3)


frame_2_callbacks = {"Register Select": register_select}


def _update_frame3_buttons(bdata3):
    bt = BustHolder().bt
    bt.set_buttons(bdata3, bt.buttons_dict["Frame3"])


frame_callbacks = {
    Frame2.__name__: frame_2_callbacks
    }