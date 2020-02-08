from itertools import chain

from gui.frames import Frame1, Frame2, Frame3


frame_1_buttons = {
    "Module Name": "string",
    "Bus Type": "dropdown",
    "Reset Mode": "dropdown",
    "Comp Lib ": "string",
    "Data Width": "string",
    "Address Width": "string",
}

frame_2_buttons = {
    "Base Address": "string",
    "Clock Name": "string",
    "Register Select": "string",
}

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

# explicitly using the Frame object names as keys
frame_buttons = {
    Frame1.__name__: frame_1_buttons,
    Frame2.__name__: frame_2_buttons,
    Frame3.__name__: frame_3_buttons,
}


all_buttons = list(chain(*[k.keys() for k in frame_buttons.values()]))
