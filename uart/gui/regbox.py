import tkinter as tk
from uart.register import Register
from uart.field import Field
from collections import OrderedDict
from math import ceil
from typing import List


class RegToBoxes():
    """Make nice boxes from a register"""

    def __init__(self, master, reg, col, row):
        self.master = master
        self.reg = reg
        self.reg: Register
        self.col = col
        self.row = row

        self.nbits = self.reg.length
        self.ndrawings = ceil(self.nbits / 16) if self.nbits else 1  # always 1 or more
        self.drawings = [None] * self.ndrawings
        self.drawings: List[RegBoxes]
        self.init_drawings()

    def init_drawings(self):
        for i in range(self.ndrawings):
            rb = RegBoxes(row=self.row + self.ndrawings - i,
                          col=self.col,
                          master=self.master,
                          nboxes=16, offset=i * 16)
            self.drawings[i] = rb
        self.grey_out_unused_bits()

        self.write_field_names()
        self.make_field_borders()

    def write_field_names(self):
        for field in self.reg.fields:
            field: Field
            text = field.name
            # index for drawings
            start_index = field.pos_low // 16
            stop_index = field.pos_high // 16
            if start_index == stop_index:
                middle = True
            else:
                middle = False
            rb = self.drawings[stop_index]
            rb: RegBoxes
            if middle:
                x0 = rb.get_x_middle(16 - (field.pos_low%16),
                                     15 - (field.pos_high%16))
                anchor = tk.CENTER
            else:
                x0 = ((16-(field.pos_high + 1)) % 16) * rb.box_w + (rb.box_w // 2)
                anchor = tk.W

            y0 = rb.box_h // 2
            print("x0", x0, text)
            rb.canvas.create_text(x0, y0, text=text, anchor=anchor)

    def make_field_borders(self):
        for field in self.reg.fields:
            field: Field
            text = field.name
            # index for drawings
            start_index = field.pos_low // 16
            stop_index = field.pos_high // 16
            rb_top = self.drawings[stop_index]
            rb_bottom = self.drawings[start_index]
            rb_top: RegBoxes
            rb_bottom: RegBoxes
            high_index = 15 - field.pos_high % 16
            low_index = 15 - field.pos_low % 16
            rb_top.draw_border(high_index, left=True)
            rb_bottom.draw_border(low_index, right=True)

    def grey_out_unused_bits(self):
        not_in_reg = list(range(self.nbits, self.ndrawings * 16))
        print(not_in_reg, self.nbits, self.ndrawings * 16)
        for i, rb in enumerate(self.drawings):
            rb: RegBoxes
            for q in not_in_reg:
                n = q - i * 16
                if n < 16:
                    rb.fill(15 - q % 16)
                    print("filling", q % 16, "of", i)


class RegBoxes():
    """reg boxes in one canvas
    placed on grid with row, col operators."""

    def __init__(self, row, col, master, nboxes=16, offset=0):
        self.offset = offset
        self.master = master
        self.master: tk.Tk
        self.nboxes = nboxes
        self.box_h = 44
        self.box_w = self.box_h
        self.row = row
        self.col = col
        self.boxtexts = [None] * self.nboxes
        self.canvas = tk.Canvas(self.master, bg="White",
                                height=self.box_h, width=self.box_w * self.nboxes,
                                borderwidth=0, highlightthickness=0)
        self.draw_details()
        self.demonumbers()
        self.canvas.grid(row=self.row, column=self.col, padx=5, pady=5)

    def draw_details(self):
        for i in range(self.nboxes):
            x0 = self.box_w * i
            self.make_nice_ticks(x0)

    def draw_border(self, number, left=False, right=False):
        colors = []
        coords = []
        if left:
            colors.append("Black")
            coords.append(number * self.box_w)
        if right:
            colors.append("Black")
            coords.append(number * self.box_w + self.box_w)

        for x, color in zip(coords, colors):
            self.canvas.create_line(x, 5,
                                    x, self.box_h - 5,
                                    width=2, fill=color)

    def make_nice_ticks(self, x0):
        self.canvas.create_line(x0, 5,
                                x0, 0,
                                x0 + self.box_w, 0,
                                x0 + self.box_w, 5,
                                width=2, fill='Black')
        self.canvas.create_line(x0, self.box_h - 5,
                                x0, self.box_h,
                                x0 + self.box_w, self.box_h,
                                x0 + self.box_w, self.box_h - 5,
                                width=2, fill='Black')

    def demonumbers(self, indices=True, centered_text=False):
        for i in range(self.nboxes):
            x0 = int(self.box_w / 2 + (i * self.box_w))
            y0 = self.box_h // 2
            text = str(15 - i)
            if indices:
                self.write_indices(i)
            if centered_text:
                self.update_text(x0, y0, text=text, n=i)

    def update_text(self, x0, y0, text, n):
        self.boxtexts[n] = text
        self.canvas.create_text(x0, y0, text=text, anchor=tk.CENTER)

    def write_indices(self, number):
        x0 = number * self.box_w
        y0 = 7
        anchor = tk.W
        if number == self.nboxes:
            anchor = tk.E
            x0 -= 2

        self.canvas.create_text(x0, y0,
                                text=str(self.nboxes - number - 1 + self.offset),
                                font=("Default", 11),
                                anchor=anchor)

    def clear_all_text(self):
        self.canvas.delete("all")
        self.boxtexts = [None] * self.nboxes
        for i in range(self.nboxes):
            self.fill(i, color="White")
            x0 = i * self.box_w
            self.make_nice_ticks(x0)

    def update_box(self, number):
        x0 = number * self.box_w
        cx = x0 + self.box_w // 2
        cy = self.box_h // 2
        self.update_text(cx, cy, text=self.boxtexts[number], n=number)
        self.make_nice_ticks(x0)
        # self.write_indices(number)

    def fill(self, number, color="Gray"):
        x0 = number * self.box_w
        y0 = 0
        cx = x0 + self.box_w // 2
        cy = self.box_h // 2

        self.canvas.create_rectangle(x0, y0,
                                     x0 + self.box_w, self.box_h,
                                     fill=color, width=0)

        self.update_box(number)

    def box_text(self, number, text):
        self.boxtexts[number] = text
        self.update_box(number)

    def get_x_middle(self, index0, index1):
        start = min(index0, index1)
        end = max(index0, index1)
        startx = start * self.box_w
        endx = end * self.box_w
        middle = startx + (abs((startx - endx)) // 2)
        print(f"start:{startx} stop:{endx}, middle:{middle}")
        return middle


if __name__ == '__main__':
    regdemo = Register(OrderedDict({'name': "demo",
                                    'mode': 'RW',
                                    'type': 'slv',
                                    'length': 21,
                                    'description': "demo register"}), 0xff, 32)
    field_demo = Field("FIELD_0_BOO", "slv", 5, 0x0, "somewhat demo-ish", 3)
    field_demo2 = Field("FIELD_1_FOO", "slv", 7, 0x0, "somewhat demo-ish", 14)
    field_demo3 = Field("FIELD_FILL", "slv", 6, 0x0, "somewhat demo-ish", 8)
    field_demo4 = Field("RST", "sl", 1, 0x0, "somewhat demo-ish", 0)
    field_demo5 = Field("TT", "sl", 1, 0x0, "somewhat demo-ish", 1)
    fdd = field_demo.get_dictionary(True, True)
    regdemo.sig_type = 'field'
    regdemo.fields = [field_demo, field_demo2, field_demo3, field_demo4, field_demo5]
    print(regdemo.__dict__)
    reg_field_demo = regdemo
    root = tk.Tk()
    tt = RegToBoxes(root, reg_field_demo, 0, 0)
    root.mainloop()
