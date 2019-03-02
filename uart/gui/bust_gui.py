import tkinter as tk
import tkinter.ttk as ttk
from collections import OrderedDict

from uart.vhdl import is_valid_VHDL
from uart.bus import Bus
from uart.module import Module
from uart.register import Register
from uart.field import Field
from uart.gui.regbox import RegToBoxes
import json

blank_reg_dict = OrderedDict({'name': "demo",
                              'mode': 'RW',
                              'type': 'slv',
                              'length': 30,
                              'description': "demo register"})
blank_reg = Register(blank_reg_dict, 0x1, 32)
blank_mod = OrderedDict({'name': "blank_mod",
                         'description': "blank description",
                         'register': [blank_reg_dict]})
default_bus = Bus(OrderedDict({'type': 'axi',
                               'data_width': 32,
                               'addr_width': 32}))
NEWREG = "new register"
NEWFIELD = "new field"


class BusOptionCb:
    def __init__(self, row, column, values, text, parent):
        self.box = ttk.Combobox(parent)
        self.box['values'] = values
        self.box.set(values[0])
        self.label = ttk.Label(parent, text=text)

        self.label.grid(row=row, column=column, sticky=tk.W)
        self.box.grid(row=row, column=column + 1, pady=2, padx=2)

    def get(self):
        return self.box.get()

    def set(self, text):
        self.box.set(text)

    def setopts(self, opts):
        self.box['values'] = opts

    def addopt(self, opt):
        opts = self.box['values']
        opts.append(opt)
        self.setopts(opts)


class BusOptionEntry:
    def __init__(self, row, column, value, text, parent):
        self.box = ttk.Entry(parent)
        self.box.insert(0, value)
        self.label = ttk.Label(parent, text=text)

        self.label.grid(row=row, column=column, sticky=tk.W)
        self.box.grid(row=row, column=column + 1, pady=2, padx=2, sticky=tk.E + tk.W)  # E + W is trick to fill.
        print("creating")
        print(self.__dict__)

    def get(self):
        return self.box.get()

    def set(self, text):
        self.box.delete(0, tk.END)
        self.box.insert(0, text)


class Vars():
    ntb = 0
    ntb_prev = 0
    busframe = 0
    moduleframe = 1
    regframe = 2
    warningframe = 3
    escpack = False
    erif_called = 0


class Counter():
    def __init__(self):
        self.n = -1

    def cnt(self):
        self.n += 1
        return self.n


class BustGui():
    def __init__(self):
        self.root = tk.Tk()
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Quit", command=self.root.quit)

        self.framewidth = self.root.winfo_screenwidth() // 2
        self.frameheight = (9 * self.framewidth) // 16
        # panes. Setting the size to hor resolution // 3 !
        self.panes = ttk.Notebook(self.root, width=self.framewidth, height=self.frameheight)
        self.f0 = ttk.Frame(self.root, width=self.framewidth, height=self.frameheight)
        self.f1 = ttk.Frame(self.root, width=self.framewidth, height=self.frameheight)
        # lf_regs = ttk.Labelframe(f1, text='Registers')
        self.f_popup = ttk.Frame(self.root, width=self.framewidth, height=self.frameheight)
        self.f3 = ttk.Frame(self.root, width=self.framewidth, height=self.frameheight)
        # first pane, which would get widgets gridded into it:
        self.p = ttk.Panedwindow(self.f1, orient=tk.HORIZONTAL)
        # f1_cont = ttk.Labelframe(p, width=100, height=100)
        self.f1_cont = ttk.Labelframe(self.p, width=self.framewidth // 2, height=self.frameheight // 2)
        self.lf_regs = ttk.Labelframe(self.p, text='Registers', width=self.framewidth // 2,
                                      height=self.frameheight // 2)  # second pane
        self.pack_panes()

        # bus tab buttons
        btb = Counter()
        self.module_name = BusOptionEntry(row=btb.cnt(), column=0, value="example_module", text="Module Name",
                                          parent=self.f0)
        self.bus_sel_type = BusOptionCb(row=btb.cnt(), column=0, values=Bus.supported_bus, text="Bus Type",
                                        parent=self.f0)
        self.reset_mode = BusOptionCb(row=btb.cnt(), column=0, values=Bus.supported_reset, text="Reset Mode",
                                      parent=self.f0)
        self.comp_library = BusOptionEntry(row=btb.cnt(), column=0, value=Bus.default_comp_library, text="Comp lib",
                                           parent=self.f0)
        self.data_width = BusOptionEntry(row=btb.cnt(), column=0, value="32", text="Data width", parent=self.f0)
        self.address_width = BusOptionEntry(row=btb.cnt(), column=0, value="32", text="Address width", parent=self.f0)

        # module tab buttons
        mtb = Counter()
        self.baseaddr = BusOptionEntry(row=mtb.cnt(), column=0, value="0xffaa0000", text="Base Address",
                                       parent=self.f1_cont)
        self.clock_name = BusOptionEntry(row=mtb.cnt(), column=0, value='clk', text="Clock Name", parent=self.f1_cont)
        self.register_sel = BusOptionCb(row=mtb.cnt(), column=0, values=['reg_a', 'reg_b', 'demo', 'new register'],
                                        text="Register select", parent=self.f1_cont)
        self.apply_button_bus = ttk.Button(self.f0, text="print JSON", command=self.update_json_bus)
        self.apply_button_bus.grid(row=99, column=99)

        self.register_sel.box.bind("<<ComboboxSelected>>", self.enter_regedit)
        # register_sel.box.bind("<Button-1>", printsome)
        # ??

        # Register tab buttons
        rtb = Counter()
        self.regname = BusOptionCb(row=rtb.cnt(), column=0, values=["reg name"], text="Register name", parent=self.f3)
        self.regdesc = BusOptionEntry(row=rtb.cnt(), column=0, value="description", text="Description", parent=self.f3)
        self.regmode = BusOptionCb(row=rtb.cnt(), column=0, values=Register.supported_modes, text="Register mode",
                                   parent=self.f3)
        self.reglen = BusOptionEntry(row=rtb.cnt(), column=0, value="32", text="Register Length", parent=self.f3)
        self.regaddr = BusOptionEntry(row=rtb.cnt(), column=0, value="0x0", text="Register Address", parent=self.f3)
        # fields
        self.field_label = ttk.Label(self.f3, text="Field")
        self.field_label.grid(row=rtb.cnt(), column=0, sticky=tk.W)
        self.reg_field_sep = ttk.Separator(self.f3, orient='horizontal')
        self.reg_field_sep.grid(row=rtb.cnt(), columnspan=2, sticky=tk.E + tk.W)
        # self.reg_field_sep.place(x=0,y=26, relwidth=1) # kinda works
        # self.reg_field_sep.place()#(sticky=tk.E + tk.W)
        self.fieldname = BusOptionCb(row=rtb.cnt(), column=0, values=["field name"], text="field name", parent=self.f3)
        self.fieldtype = BusOptionCb(row=rtb.cnt(), column=0, values=Field.supported_types, text="field type",
                                     parent=self.f3)
        self.fieldlen = BusOptionEntry(row=rtb.cnt(), column=0, value="0", text="Field Length", parent=self.f3)
        self.update_field_butt = ttk.Button(self.f3, text="Update Field", command=self.update_field)
        self.update_field_butt.grid(row=rtb.cnt(), column=0, sticky=tk.E + tk.W, columnspan=2)
        # decor
        self.regbox = RegToBoxes(self.f3, blank_reg, row=0, col=2)
        self.regbox_label = tk.StringVar()
        self.regbox_label_box = tk.Label(self.f3, textvariable=self.regbox_label)
        self.regbox_label_box.grid(row=3, column=2)
        # bindings.

        self.regname.box.bind("<<ComboboxSelected>>", self.update_register_entries)
        self.regdesc.box.bind("<<ComboboxSelected>>", self.update_register_entries)
        self.regmode.box.bind("<<ComboboxSelected>>", self.update_register_entries)
        self.regaddr.box.bind("<Return>", self.update_register_entries)
        self.reglen.box.bind("<Return>", self.update_register_entries)
        self.regname.box.bind("<Return>", self.update_register_entries)
        # self.regname.box.bind("<Button-1>", self.printsome)

        # register stuff:
        self.mod = Module(blank_mod, default_bus)

        self.initialize_bus_frame()

        self.initialize_mod_frame()

        self.current_reg = None

        self.current_reg: Register
        self.initialize_reg_frame()

        self.initialize_fields()

        print(self.mod.__dict__)
        print([str(x) for x in self.mod.registers])

    def update_register_entries(self, e):
        print("updating register values")
        self.current_reg: Register
        self.current_reg.name = self.regname.get()
        self.current_reg.description = self.regdesc.get()
        self.current_reg.length = int(self.reglen.get(),0 )
        self.current_reg.address = int(self.regaddr.get(), 0)
        #
        self.regbox_label.set(self.current_reg.name)
        print(self.current_reg)
        self.regbox.update(self.current_reg)

    def initialize_reg_frame(self):
        name = self.register_sel.get()
        if name in self.get_field_names():
            reg = self.get_register_by_name(name)
            reg: Register
        else:  # new register.
            reg = Register({'name': "demo",
                            'mode': 'RW',
                            'type': 'default',
                            'length': 32,
                            'description': "demo register"}, 0x0, 32)

        self.regname.set(name)
        self.regdesc.set(reg.description)
        self.regmode.set(reg.mode)
        self.reglen.set(reg.length)
        self.regbox.update(reg)
        self.current_reg = reg
        self.regbox_label.set(self.current_reg.name)
        self.regname.setopts([x.name for x in self.mod.registers])


    def initialize_fields(self):
        reg = self.current_reg
        reg: Register
        fieldnames = [x.name for x in reg.fields]
        self.fieldname.box['values'] = fieldnames + [NEWFIELD]
        print("regname", reg.name, "fieldnames", fieldnames)

        fieldname = "not set"
        self.fieldname.set(fieldname)
        if fieldnames:  # are there field?
            field = self.get_field_by_name(reg.fields, fieldname)
            self.fieldtype.set(field.sig_type)
            self.fieldlen.set(field.length)
            self.regbox.write_field_names()
        else:
            print("field is empty bitch")
            self.fieldtype.set("none")
            self.fieldlen.set("none")
            self.regbox.write_regname()

    def get_field_by_name(self, fields, name):
        return list(filter(lambda x: x.name == name, fields))[0]

    def get_register_by_name(self, name):
        """get a specific register from the module register list. Works sort of like list.index"""
        return list(filter(lambda x: x.name == name, self.mod.registers))[0]

    def get_field_names(self):
        return [x.name for x in self.mod.registers]

    def initialize_mod_frame(self):
        self.baseaddr.set(self.mod.baseaddr)
        self.clock_name.set(self.mod.bus.get_clk_name())
        try:
            name = self.mod.registers[0].name
        except IndexError:  # no registers ---
            name = "demoregister"
        regnames = [reg.name for reg in self.mod.registers]
        self.register_sel.box['values'] = regnames + [NEWREG]
        self.register_sel.set(name)

        self.update_disp_reg_names([str(reg) for reg in self.mod.registers])

    def initialize_bus_frame(self):
        """get ALL module values from self.mod, and set the corresponding
        gui elements in the bus notebook frame"""
        self.module_name.set(self.mod.name)
        self.bus_sel_type.set(self.mod.bus.bus_type)
        self.reset_mode.set(self.mod.bus.bus_reset)
        self.comp_library.set(self.mod.bus.comp_library)
        self.data_width.set(self.mod.data_width)
        self.address_width.set(self.mod.addr_width)

    def update_field(self):
        print("update field")
        name = self.fieldname.get()
        is_valid_VHDL(name)
        type = self.fieldtype.get()
        assert type in Field.supported_types, str(type) + "not in supported field types"
        # fields are made by fields.append(field_dict)

    def pack_panes(self):
        self.p.add(self.f1_cont)
        self.p.add(self.lf_regs)
        self.p.pack(expand=True, fill='both')
        self.panes.add(self.f0, text="I. Definitions")
        self.panes.add(self.f1, text="II. Module")
        self.panes.add(self.f3, text="Register")
        self.panes.add(self.f_popup, text="Warning")
        self.panes.pack(fill=tk.X)

        # defaults:
        self.panes.hide(Vars.warningframe)
        self.root.bind("<KeyRelease>", self.keyup)
        self.panes.bind("<<NotebookTabChanged>>", self.update_notebook_tab)

    def printsome(self, e):
        print("focus out !!!")
        print(self.regname.box.get())

    def enter_regedit(self, e):
        e: tk.EventType.Selection
        print("editing register", e.char, e.__dict__)
        self.initialize_reg_frame()
        newreg_name = self.register_sel.get()
        print(newreg_name)
        self.panes.select(Vars.regframe)
        self.regname.box.set(self.register_sel.get())

        regdemo = Register(OrderedDict({'name': "demo",
                                        'mode': 'RW',
                                        'type': 'default',
                                        'length': 31,
                                        'description': "demo register"}), 0xff, 32)
        # self.update_disp_reg_names(['reg a', 'reg b', regdemo.__str__()])

    def update_json_bus(self):
        bus_settings = OrderedDict({'type': self.bus_sel_type.get(),
                                    'reset': self.reset_mode.get(),
                                    'comp_library': self.comp_library.get(),
                                    'data_width': self.data_width.get(),
                                    'addr_width': self.address_width.get()})
        self.bus = Bus(bus_settings)
        print(bus_settings)
        print(json.dumps(self.bus.return_JSON()))
        print(self.bus.return_bus_pkg_VHDL())
        print(self.bus.return_axi_pif_VHDL())
        print(self.bus.return_bus_pif_VHDL())

    def keyup(self, e):
        e: tk.EventType.KeyRelease
        print('up', e.char, str(e), e.__dict__, "\n", e.state, e.widget)
        if e.keysym == "Escape":
            print("escape pressed!")
            self.panes.focus_force()  # for no entries out of tab
            self.escape_frame()
        # if e.keysym == "Tab" and e.state & 0b1:
        #     old = self.panes.index(self.panes.select())
        #     new = ((old + 1) % 2)
        #     if new == 0:
        #         self.panes.select(Vars.busframe)
        #     if new == 1:
        #         self.panes.select(Vars.moduleframe)

    def keyup_esc(self, e):
        e: tk.EventType.KeyRelease
        if e.keysym == "Escape":
            print("escape pressed in popup, quitting")
            self.root.quit()
        else:
            # reset
            self.esc_reset(e)

    def esc_reset(self, e):
        self.root.bind("<KeyRelease>", self.keyup)
        self.panes.select(Vars.ntb_prev)
        self.panes.hide(Vars.warningframe)

    def escape_frame(self):
        # panes.select(f_popup.winfo_id())
        self.panes.select(Vars.warningframe)
        self.root.bind("<KeyRelease>", self.keyup_esc)
        self.root.bind("<KeyRelease>", self.keyup_esc)
        if Vars.escpack is False:  # can only call pack ONCE!
            self.eframebutt = tk.Button(self.f_popup, text="Really exit? [ESC]", command=self.root.quit)
            self.eframebutt.pack(fill=tk.X)
            Vars.escpack = True

    def update_notebook_tab(self, e):
        Vars.ntb_prev = Vars.ntb
        Vars.ntb = self.panes.index(self.panes.select())

    def update_disp_reg_names(self, reg_txt):
        # parent = lf_regs
        labels = []
        for i, reg in enumerate(reg_txt):
            l = ttk.Label(self.lf_regs, text=reg)
            l.grid(row=i, sticky=tk.W)
            labels.append(l)
        return labels


if __name__ == '__main__':
    BG = BustGui()
    BG.root.mainloop()
