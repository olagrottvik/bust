from functools import partial

from gui.buttons_decl import frame_3_button_data
from gui.frames import Frame2, Frame3
from gui.gui_defs import BustHolder
from gui.gui_utils import get_register_from_name, first


def register_select(button, event):
    print("called register select!", event)
    val = button.getvalue()
    print("my value is", val)
    bdata3 = build_frame3(val)
    _update_frame3_buttons(bdata3)


def build_frame3(regsel_name, field_idx=0):
    module = BustHolder().module
    reg = get_register_from_name(module, regsel_name)
    fields = reg.fields
    if fields:
        print("found fields", fields)
        bdata3 = frame_3_button_data(reg, reg.fields[field_idx])
    else:
        bdata3 = frame_3_button_data(reg)
    return bdata3


def field_select(button, event):
    print(button, event)
    val = button.getvalue()
    bt = BustHolder().bt
    module = BustHolder().module
    regname = bt.buttons_dict[Frame2.__name__]["Register Select"].getvalue()
    reg = get_register_from_name(module, regname)
    field_idx = _index_reg_field(reg, val)
    bdata3 = build_frame3(regname, field_idx)
    _update_frame3_buttons(bdata3)


def _index_reg_field(reg, field_name):
    return first([cnt for cnt, r in enumerate(reg.fields) if r.name == field_name])


frame_2_callbacks = {"Register Select": register_select}
frame_3_callbacks = {"Field Sel": field_select}


def _update_frame3_buttons(bdata3):
    bt = BustHolder().bt
    bt.set_buttons(bdata3, bt.buttons_dict["Frame3"])


frame_callbacks = {
    Frame2.__name__: frame_2_callbacks,
    Frame3.__name__: frame_3_callbacks,
}
