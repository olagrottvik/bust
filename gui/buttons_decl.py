from itertools import chain

from gui.frames import Frame1, Frame2, Frame3

frame_1_buttons = {
    "Module Name": "string",
    "Bus Type": "dropdown",
    "Reset Mode": "string",
    "Comp Lib": "string",
    "Data Width": "string",
    "Address Width": "string",
}


def frame_1_button_data(module):
    buttons = {
        "Module Name": module.name,
        "Bus Type": (module.bus.bus_type, module.bus.supported_bus),
        "Reset Mode": module.bus.bus_reset,
        "Comp Lib": module.bus.comp_library,
        "Data Width": module.data_width,
        "Address Width": module.addr_width,
    }
    return buttons


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

def frame_3_button_data(register, field=None):
    buttons_reg = {
        "Register Name": register.name,
        "Description": register.description,
        "Register Mode": register.mode,
        "Register Type": (register.sig_type, register.supported_types),
        "Register Length": register.length,
        "Register Address": register.address,
        "Register Reset": register.reset,
        }
    if field:
        field_reg = {
            "Field Name": field.name,
            "Field Type": (field.sig_type, field.supported_types),
            "Field Length": field.length,
            "Field Reset": field.reset,
            "Field Description": field.description,
            }
        return dict(buttons_reg, **field_reg)
    return buttons_reg

# explicitly using the Frame object names as keys
frame_buttons = {
    Frame1.__name__: frame_1_buttons,
    Frame2.__name__: frame_2_buttons,
    Frame3.__name__: frame_3_buttons,
}


all_buttons = list(chain(*[k.keys() for k in frame_buttons.values()]))
