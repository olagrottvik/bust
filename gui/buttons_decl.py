import copy

from itertools import chain

from gui.frames import Frame1, Frame2, Frame3
from gui.gui_utils import rgetattr, rsetattr

frame_1_buttons = {
    "Module Name": "string",
    "Bus Type": "dropdown",
    "Reset Mode": "string",
    "Comp Lib": "string",
    "Data Width": "string",
    "Address Width": "string",
}

frame_1_button_module_attrs = {
    "Module Name": "name",
    "Bus Type": ("bus.bus_type", "bus.supported_bus"),
    "Reset Mode": "bus.bus_reset",
    "Comp Lib": "bus.comp_library",
    "Data Width": "data_width",
    "Address Width": "addr_width",
}


def frame_1_button_data(module):
    """button translation from Module to dict in Frame 1."""
    buttons = button_data_from_obj(module, frame_1_button_module_attrs)
    return buttons


def button_data_from_obj(obj, attrs):
    buttons = {}
    for k, v in attrs.items():
        if isinstance(v, tuple):
            if callable(v[1]):
                buttons[k] = (rgetattr(obj, v[0]), v[1](obj))
            else:
                buttons[k] = (rgetattr(obj, v[0]), rgetattr(obj, v[1]))
        else:
            buttons[k] = rgetattr(obj, v)
    return buttons


def module_from_frame_1(module, buttons):
    for k in frame_1_button_module_attrs.keys():
        newval = buttons[k].getvalue()
        attrkey = frame_1_button_module_attrs[k]
        m_attr = attrkey if type(attrkey) is str else attrkey[0]
        rsetattr(module, m_attr, newval)


frame_2_buttons = {
    "Register Select": "dropdown",
}


def frame_2_button_data(module):
    registers = None
    if module.registers:
        regnames = [reg.name for reg in module.registers]
        registers = (regnames[0], regnames)
    buttons = {"Register Select": registers}
    return buttons


def module_from_frame_2(module):
    pass


frame_3_buttons = {
    "Register Name": "string",
    "Description": "string",
    "Register Mode": "dropdown",
    "Register Type": "dropdown",
    "Register Length": "string",
    "Register Address": "string",
    "Register Reset": "string",
    "Field": "separator",
    "Field Name": "dropdown",
    "Field Type": "dropdown",
    "Field Length": "string",
    "Field Reset": "string",
    "Field Description": "string",
}

frame_3_button_register_attrs = {
    "Register Name": "name",
    "Description": "description",
    "Register Mode": ("mode", "supported_modes"),
    "Register Type": ("sig_type", "supported_types"),
    "Register Length": "length",
    "Register Address": "address",
    "Register Reset": "reset",
}


frame_3_button_field_attrs = {
    "Field Type": ("sig_type", "supported_types"),
    "Field Length": "length",
    "Field Reset": "reset",
    "Field Description": "description",
}


def frame_3_button_data(register, field=None):
    buttons_reg = button_data_from_obj(register, frame_3_button_register_attrs)
    if field:
        field_reg = button_data_from_obj(field, frame_3_button_field_attrs)
        # field possible names is a register attribute. special exception
        field_reg["Field Name"] = (field.name, [f.name for f in register.fields])

        return dict(buttons_reg, **field_reg)
    return buttons_reg

def register_from_frame_3(register):
    pass

def module_from_frame_3(module):
    pass


# explicitly using the Frame object names as keys
frame_buttons = {
    Frame1.__name__: frame_1_buttons,
    Frame2.__name__: frame_2_buttons,
    Frame3.__name__: frame_3_buttons,
}


all_buttons = list(chain(*[k.keys() for k in frame_buttons.values()]))
