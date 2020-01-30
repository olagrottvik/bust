"""@package module
Contains the Module class and relevant exceptions

"""

import json
from collections import OrderedDict

from bust.utils import indent_string
from bust.utils import add_line_breaks
from bust.exceptions import InvalidAddress
from bust.exceptions import InvalidRegister
from bust.register import Register
from bust.vhdl import is_valid_VHDL
from bust.vhdl import is_unique


class Module:
    """! @brief Managing module information

    Contain the name of the module, the bus type and addr and data width specification +
    description of the module.
    """

    def __init__(self, mod, bus, settings):
        """! @brief
        """
        try:
            self.bus = bus
            self.settings = settings
            self.registers = []
            self.addresses = []

            is_valid_VHDL(mod['name'])
            self.name = mod['name']
            self.description = mod['description']
            self.description_with_breaks = add_line_breaks(mod['description'], 25)
            self.version = None
            self.git_hash = None

            self.addr_width = bus.addr_width
            self.data_width = bus.data_width

            if 'byte_addressable' in mod:
                if mod['byte_addressable'] == 'True':
                    self.byte_addressable = True
                else:
                    self.byte_addressable = False
            else:
                if self.bus.bus_type == 'axi': # axi usually is byte addressable
                    self.byte_addressable = True
                else:
                    self.byte_addressable = False


            for reg in mod['register']:
                self.add_register(reg)

        except Exception as e:
            print(e)
            exit(2)

    def add_register(self, reg):
        if self.register_valid(reg):
            if "address" in reg:
                addr = int(reg['address'], 16)
                if self.is_address_free(addr):
                    if self.is_address_out_of_range(addr):
                        raise RuntimeError("Address " + hex(addr) +
                                           " is definitely out of range...")
                    self.addresses.append(addr)
                    self.registers.append(Register(reg, addr, self.data_width))
                else:
                    raise InvalidAddress(reg['name'], addr)
            else:
                addr = self.get_next_address()
                self.addresses.append(addr)
                self.registers.append(Register(reg, addr, self.data_width))
        else:
            raise InvalidRegister(reg)

    def return_module_pkg_VHDL(self):
        s = 'library ieee;\n'
        s += 'use ieee.std_logic_1164.all;\n'
        s += 'use ieee.numeric_std.all;\n\n'
        s += '\n'
        s += "package " + self.name + "_pif_pkg is"
        s += "\n\n"

        par = ''
        par += "constant C_" + self.name.upper()
        par += "_ADDR_WIDTH : natural := " + str(self.addr_width) + ";\n"
        par += "constant C_" + self.name.upper()
        par += "_DATA_WIDTH : natural := " + str(self.data_width) + ";\n"
        par += "\n"

        par += "subtype t_" + self.name + "_addr is "
        par += "std_logic_vector(C_" + self.name.upper() + "_ADDR_WIDTH-1 "
        par += "downto 0);\n"

        par += "subtype t_" + self.name + "_data is "
        par += "std_logic_vector(C_" + self.name.upper() + "_DATA_WIDTH-1 "
        par += "downto 0);\n"
        par += "\n"

        for reg in self.registers:
            par += "constant C_ADDR_" + reg.name.upper()
            par += " : t_" + self.name + "_addr := " + str(self.addr_width)
            par += 'X"' + '%X' % reg.address + '";\n'
        par += '\n'
        s += indent_string(par)

        if self.count_rw_regs() > 0:
            s += indent_string("-- RW Register Record Definitions\n\n")

            # Create all types for RW registers with records
            for reg in self.registers:
                if reg.mode == "rw" and reg.sig_type == "fields":
                    s += indent_string("type t_" + self.name + "_rw_")
                    s += reg.name + " is record\n"

                    for field in reg.fields:
                        s += indent_string(field.name, 2) + " : "
                        if field.sig_type == "slv":
                            s += "std_logic_vector(" + str(field.length - 1)
                            s += " downto 0);\n"
                        elif field.sig_type == "sl":
                            s += "std_logic;\n"
                        else:
                            raise RuntimeError(
                                "Something went wrong..." + field.sig_type)
                    s += indent_string("end record;\n\n")

            # The RW register record type
            s += indent_string("type t_" + self.name + "_rw_regs is record\n")
            for reg in self.registers:
                if reg.mode == "rw":
                    s += indent_string(reg.name, 2) + " : "
                    if reg.sig_type == "default" or (reg.sig_type == "slv" and reg.length == self.data_width):
                        s += "t_" + self.name + "_data;\n"
                    elif reg.sig_type == "slv":
                        s += "std_logic_vector(" + \
                            str(reg.length - 1) + " downto 0);\n"
                    elif reg.sig_type == "sl":
                        s += "std_logic;\n"
                    elif reg.sig_type == "fields":
                        s += "t_" + self.name + "_rw_" + reg.name + ";\n"
                    else:
                        raise RuntimeError("Something went wrong...")
            s += indent_string("end record;\n")
            s += "\n"

            s += indent_string("-- RW Register Reset Value Constant\n\n")

            s += indent_string("constant c_") + self.name + "_rw_regs : t_"
            s += self.name + "_rw_regs := (\n"
            gen = [reg for reg in self.registers if reg.mode == 'rw']

            for i, reg in enumerate(gen):
                par = ''
                par += reg.name + ' => '

                # RW default values must be declared
                if reg.sig_type == 'default' or reg.sig_type == 'slv':
                    if reg.reset == "0x0":
                        par += "(others => '0')"
                    else:
                        par += str(reg.length) + 'X"'
                        par += format(int(reg.reset, 16), 'X') + '"'

                elif reg.sig_type == 'fields':

                    if len(reg.fields) > 1:
                        par += '(\n'
                    else:
                        par += '('

                    for j, field in enumerate(reg.fields):
                        if len(reg.fields) > 1:
                            par += indent_string(field.name + ' => ')
                        else:
                            par += field.name + ' => '

                        if field.sig_type == 'slv':

                            if field.reset == "0x0":
                                par += "(others => '0')"
                            else:
                                par += str(field.length) + 'X"'
                                par += format(int(field.reset, 16), 'X') + '"'

                        elif field.sig_type == 'sl':
                            par += "'" + format(int(field.reset, 16), 'X') + "'"

                        if j < len(reg.fields) - 1:
                            par += ',\n'

                    par += ')'

                elif reg.sig_type == 'sl':
                    par += "'" + format(int(reg.reset, 16), 'X') + "'"

                if i < len(gen) - 1:
                    par += ','
                else:
                    par += ');'
                par += '\n'

                s += indent_string(par, 2)
            s += '\n'

        if self.count_ro_regs() > 0:

            s += indent_string("-- RO Register Record Definitions\n\n")

            # Create all types for RO registers with records
            for reg in self.registers:
                if reg.mode == "ro" and reg.sig_type == "fields":
                    s += indent_string("type t_" + self.name + "_ro_")
                    s += reg.name + " is record\n"

                    for field in reg.fields:
                        s += indent_string(field.name, 2) + " : "
                        if field.sig_type == "slv":
                            s += "std_logic_vector(" + str(field.length - 1)
                            s += " downto 0);\n"
                        elif field.sig_type == "sl":
                            s += "std_logic;\n"
                        else:
                            raise RuntimeError("Something went wrong...")
                    s += indent_string("end record;\n\n")

            # The RO register record type
            s += indent_string("type t_" + self.name + "_ro_regs is record\n")
            for reg in self.registers:
                if reg.mode == "ro":
                    s += indent_string(reg.name, 2) + " : "
                    if reg.sig_type == "default" or (reg.sig_type == "slv" and reg.length == self.data_width):
                        s += "t_" + self.name + "_data;\n"
                    elif reg.sig_type == "slv":
                        s += "std_logic_vector(" + \
                            str(reg.length - 1) + " downto 0);\n"
                    elif reg.sig_type == "sl":
                        s += "std_logic;\n"
                    elif reg.sig_type == "fields":
                        s += "t_" + self.name + "_ro_" + reg.name + ";\n"
                    else:
                        raise RuntimeError(
                            "Something went wrong... What now?" + reg.sig_type)
            s += indent_string("end record;\n")
            s += "\n"

            s += indent_string("-- RO Register Reset Value Constant\n\n")

            s += indent_string("constant c_") + self.name + "_ro_regs : t_"
            s += self.name + "_ro_regs := (\n"
            gen = [reg for reg in self.registers if reg.mode == 'ro']

            for i, reg in enumerate(gen):
                par = ''
                par += reg.name + ' => '

                # RO default values must be declared
                if reg.sig_type == 'default' or reg.sig_type == 'slv':
                    if reg.reset == "0x0":
                        par += "(others => '0')"
                    else:
                        par += str(reg.length) + 'X"'
                        par += format(int(reg.reset, 16), 'X') + '"'

                elif reg.sig_type == 'fields':
                    if len(reg.fields) > 1:
                        par += '(\n'
                    else:
                        par += '('

                    for j, field in enumerate(reg.fields):
                        if len(reg.fields) > 1:
                            par += indent_string(field.name + ' => ')
                        else:
                            par += field.name + ' => '

                        if field.sig_type == 'slv':

                            if field.reset == "0x0":
                                par += "(others => '0')"
                            else:
                                par += str(field.length) + 'X"'
                                par += format(int(field.reset, 16), 'X') + '"'

                        elif field.sig_type == 'sl':
                            par += "'" + format(int(field.reset, 16), 'X') + "'"

                        if j < len(reg.fields) - 1:
                            par += ',\n'

                    par += ')'

                elif reg.sig_type == 'sl':
                    par += "'" + format(int(reg.reset, 16), 'X') + "'"

                else:
                    raise RuntimeError(
                        "Something went wrong... What now?" + reg.sig_type)

                if i < len(gen) - 1:
                    par += ','
                else:
                    par += ');'
                par += '\n'

                s += indent_string(par, 2)

        if self.count_pulse_regs() > 0:
            s += indent_string("-- PULSE Register Record Definitions\n\n")

            # Create all types for PULSE registers with records
            for reg in self.registers:
                if reg.mode == "pulse" and reg.sig_type == "fields":
                    s += indent_string("type t_" + self.name + "_pulse_")
                    s += reg.name + " is record\n"

                    for field in reg.fields:
                        s += indent_string(field.name, 2) + " : "
                        if field.sig_type == "slv":
                            s += "std_logic_vector(" + str(field.length - 1)
                            s += " downto 0);\n"
                        elif field.sig_type == "sl":
                            s += "std_logic;\n"
                        else:
                            raise RuntimeError(
                                "Something went wrong..." + field.sig_type)
                    s += indent_string("end record;\n\n")

            # The PULSE register record type
            s += indent_string("type t_" + self.name + "_pulse_regs is record\n")
            for reg in self.registers:
                if reg.mode == "pulse":
                    s += indent_string(reg.name, 2) + " : "
                    if reg.sig_type == "default" or (reg.sig_type == "slv" and reg.length == self.data_width):
                        s += "t_" + self.name + "_data;\n"
                    elif reg.sig_type == "slv":
                        s += "std_logic_vector(" + \
                            str(reg.length - 1) + " downto 0);\n"
                    elif reg.sig_type == "sl":
                        s += "std_logic;\n"
                    elif reg.sig_type == "fields":
                        s += "t_" + self.name + "_pulse_" + reg.name + ";\n"
                    else:
                        raise RuntimeError("Something went wrong...")
            s += indent_string("end record;\n")
            s += "\n"

            s += indent_string("-- PULSE Register Reset Value Constant\n\n")

            s += indent_string("constant c_") + self.name + "_pulse_regs : t_"
            s += self.name + "_pulse_regs := (\n"
            gen = [reg for reg in self.registers if reg.mode == 'pulse']

            for i, reg in enumerate(gen):
                par = ''
                par += reg.name + ' => '

                # RW default values must be declared
                if reg.sig_type == 'default' or reg.sig_type == 'slv':
                    if reg.reset == "0x0":
                        par += "(others => '0')"
                    else:
                        par += str(reg.length) + 'X"'
                        par += format(int(reg.reset, 16), 'X') + '"'

                elif reg.sig_type == 'fields':

                    if len(reg.fields) > 1:
                        par += '(\n'
                    else:
                        par += '('

                    for j, field in enumerate(reg.fields):
                        if len(reg.fields) > 1:
                            par += indent_string(field.name + ' => ')
                        else:
                            par += field.name + ' => '

                        if field.sig_type == 'slv':

                            if field.reset == "0x0":
                                par += "(others => '0')"
                            else:
                                par += str(field.length) + 'X"'
                                par += format(int(field.reset, 16), 'X') + '"'

                        elif field.sig_type == 'sl':
                            par += "'" + format(int(field.reset, 16), 'X') + "'"

                        if j < len(reg.fields) - 1:
                            par += ',\n'

                    par += ')'

                elif reg.sig_type == 'sl':
                    par += "'" + format(int(reg.reset, 16), 'X') + "'"

                if i < len(gen) - 1:
                    par += ','
                else:
                    par += ');'
                par += '\n'

                s += indent_string(par, 2)
            s += '\n'

        s += '\n'

        s += "end package " + self.name + "_pif_pkg;"

        return s

    def return_module_VHDL(self):
        s = 'library ieee;\n'
        s += 'use ieee.std_logic_1164.all;\n'
        s += 'use ieee.numeric_std.all;\n\n'
        s += '-- User Libraries Start\n\n'
        s += '-- User Libraries End\n'
        s += '\n'
        if self.bus.comp_library != "work":
            s += "library " + self.bus.comp_library + ";\n"
        s += 'use ' + self.bus.comp_library + '.' + self.bus.bus_type + '_pkg.all;\n'
        s += 'use work.' + self.name + '_pif_pkg.all;\n'
        s += '\n'

        s += 'entity ' + self.name + ' is\n'
        s += '\n'
        s += indent_string('generic (\n')
        par = '-- User Generics Start\n\n'
        par += '-- User Generics End\n'
        par += '-- ' + self.bus.bus_type.upper() + ' Bus Interface Generics\n'
        par += 'g_' + self.bus.bus_type + '_baseaddr        : std_logic_vector(' + str(self.bus.addr_width - 1)
        par += " downto 0) := (others => '0'));\n"

        s += indent_string(par, 2)

        s += indent_string('port (\n')
        par = '-- User Ports Start\n\n'
        par += '-- User Ports End\n'
        par += '-- ' + self.bus.bus_type.upper() + ' Bus Interface Ports\n'
        par += self.bus.bus_type + '_' + self.bus.get_clk_name() + '      : in  std_logic;\n'
        par += self.bus.bus_type + '_' + self.bus.get_reset_name() + ' : in  std_logic;\n'
        par += self.bus.bus_type + '_in       : in  t_' + \
            self.bus.bus_type + '_interconnect_to_slave;\n'
        par += self.bus.bus_type + '_out      : out t_' + \
            self.bus.bus_type + '_slave_to_interconnect\n'
        par += ');\n'
        s += indent_string(par, 2)
        s += '\n'
        s += 'end entity ' + self.name + ';\n'
        s += '\n'

        s += 'architecture behavior of ' + self.name + ' is\n'
        s += '\n'
        par = '-- User Architecture Start\n\n'
        par += '-- User Architecture End\n\n'
        s += indent_string(par)

        s += indent_string("-- " + self.bus.bus_type.upper() + " output signal for user readback\n")
        par = "signal " + self.bus.bus_type + "_out_i : t_" + self.bus.bus_type
        par += "_slave_to_interconnect;\n"
        s += indent_string(par)

        s += indent_string("-- Register Signals\n")
        if self.count_rw_regs() > 0:
            s += indent_string('signal ' + self.bus.bus_type + '_rw_regs    : t_')
            s += self.name + '_rw_regs    := c_' + self.name + '_rw_regs;\n'
        if self.count_ro_regs() > 0:
            s += indent_string('signal ' + self.bus.bus_type + '_ro_regs    : t_')
            s += self.name + '_ro_regs    := c_' + self.name + '_ro_regs;\n'
        if self.count_pulse_regs() > 0:
            s += indent_string('signal ' + self.bus.bus_type + '_pulse_regs : t_')
            s += self.name + '_pulse_regs := c_' + self.name + '_pulse_regs;\n'

        if self.count_rw_regs() + self.count_ro_regs() + self.count_pulse_regs() > 0:
            s += '\n'

        s += 'begin\n'
        s += '\n'

        par = '-- User Logic Start\n\n'
        par += '-- User Logic End\n\n'
        s += indent_string(par)

        s += indent_string(self.bus.bus_type + "_out <= " + self.bus.bus_type + "_out_i;\n\n")

        s += indent_string(self.get_instantiation("i_{}_{}_pif".format(self.name, self.bus.bus_type)))

        s += '\n'
        s += 'end architecture behavior;'

        return s

    def get_instantiation(self, instance_name, intern_out=True):
        s = instance_name + ' '
        s += ': entity work.' + self.name + '_' + self.bus.bus_type + '_pif\n'
        s += indent_string('generic map (\n')
        par = 'g_' + self.bus.bus_type + '_baseaddr      => C_BASEADDR)\n'
        s += indent_string(par, 2)

        s += indent_string('port map (\n')
        if intern_out:
            inter = '_i'
        else:
            inter = ''

        par = ''
        if self.count_rw_regs() > 0:
            par += self.bus.bus_type + '_rw_regs         => ' + self.bus.bus_type + '_rw_regs,\n'
        if self.count_ro_regs() > 0:
            par += self.bus.bus_type + '_ro_regs         => ' + self.bus.bus_type + '_ro_regs,\n'
        if self.count_pulse_regs() > 0:
            par += self.bus.bus_type + '_pulse_regs      => ' + self.bus.bus_type + '_pulse_regs,\n'

        par += self.bus.get_clk_name() + '                 => ' + self.bus.bus_type + '_' + self.bus.get_clk_name() + ',\n'
        par += self.bus.get_reset_name() + '            => ' + self.bus.bus_type + '_' + self.bus.get_reset_name() + ',\n'
        par += 'awaddr              => ' + self.bus.bus_type + '_in.awaddr(C_'
        par += self.name.upper() + '_ADDR_WIDTH-1 downto 0),\n'
        par += 'awvalid             => ' + self.bus.bus_type + '_in.awvalid,\n'
        par += 'awready             => ' + self.bus.bus_type + '_out{0}.awready,\n'.format(inter)
        par += 'wdata               => ' + self.bus.bus_type + '_in.wdata(C_'
        par += self.name.upper() + '_DATA_WIDTH-1 downto 0),\n'
        par += 'wvalid              => ' + self.bus.bus_type + '_in.wvalid,\n'
        par += 'wready              => ' + self.bus.bus_type + '_out{0}.wready,\n'.format(inter)
        par += 'bresp               => ' + self.bus.bus_type + '_out{0}.bresp,\n'.format(inter)
        par += 'bvalid              => ' + self.bus.bus_type + '_out{0}.bvalid,\n'.format(inter)
        par += 'bready              => ' + self.bus.bus_type + '_in.bready,\n'
        par += 'araddr              => ' + self.bus.bus_type + '_in.araddr(C_'
        par += self.name.upper() + '_ADDR_WIDTH-1 downto 0),\n'
        par += 'arvalid             => ' + self.bus.bus_type + '_in.arvalid,\n'
        par += 'arready             => ' + self.bus.bus_type + '_out{0}.arready,\n'.format(inter)
        par += 'rdata               => ' + self.bus.bus_type + '_out{0}.rdata(C_'.format(inter)
        par += self.name.upper() + '_DATA_WIDTH-1 downto 0),\n'
        par += 'rresp               => ' + self.bus.bus_type + '_out{0}.rresp,\n'.format(inter)
        par += 'rvalid              => ' + self.bus.bus_type + '_out{0}.rvalid,\n'.format(inter)
        par += 'rready              => ' + self.bus.bus_type + '_in.rready\n'
        par += ');\n'
        s += indent_string(par, 2)
        return s

    def return_JSON(self, include_address=False):
        """! @brief Returns JSON string

        """
        dic = OrderedDict()
        mod = OrderedDict()
        dic["settings"] = self.settings.return_JSON()
        dic["bus"] = self.bus.return_JSON()
        dic["module"] = OrderedDict()

        mod["name"] = self.name
        mod["description"] = self.description
        if self.version is not None:
            mod["version"] = self.version
        if self.git_hash is not None:
            mod["git_hash"] = self.git_hash


        mod["register"] = []

        for i, reg in enumerate(self.registers):
            reg_dic = OrderedDict()

            reg_dic["name"] = reg.name
            reg_dic["mode"] = reg.mode
            if reg.mode == 'pulse':
                reg_dic["num_cycles"] = reg.num_cycles
            reg_dic["type"] = reg.sig_type

            if include_address:
                reg_dic["address"] = str(hex(reg.address))

            if (reg.sig_type != "default" and reg.sig_type != "fields" and
                    reg.sig_type != "sl"):
                reg_dic["length"] = reg.length

            if reg.sig_type != "fields":
                reg_dic["reset"] = reg.reset

            if reg.sig_type == "fields" and len(reg.fields) > 0:
                reg_dic["fields"] = []
                for field in reg.fields:
                    reg_dic["fields"].append(field.return_dic())

            reg_dic["description"] = reg.description

            mod["register"].append(reg_dic)

        dic["module"] = mod
        return json.dumps(dic, indent=4)

    def get_next_address(self):
        """! @brief Will get the next address based on the byte-addressed scheme

        """
        addr = 0
        found_addr = False
        while (not found_addr):
            if self.is_address_out_of_range(addr):
                raise RuntimeError("Address " + hex(addr) + " is definitely out of range...")
            if self.is_address_free(addr):
                self.addresses.append(addr)
                return addr
            else:
                if self.byte_addressable:
                    addr += self.data_width // 8  # force integer division to prevent float
                else:
                    addr += 1

    def is_address_out_of_range(self, addr):
        """ Returns True if address is out of range, False if not"""

        if addr > pow(2, self.addr_width) - 1:
            return True

        return False

    def is_address_free(self, addr):
        """Returns True if address is not been used in the module, False if it already taken"""
        for address in self.addresses:
            if address == addr:
                return False
        # If loop completes without matching addresses
        return True

    def is_address_byte_based(self, addr):
        """Returns True if address is divisable by number of bytes in module data width"""

        if addr % (self.data_width / 8) == 0:
            return True
        else:
            return False

    def update_addresses(self):
        self.addresses = []
        for reg in self.registers:
            addr = self.get_next_address()
            self.addresses.append(addr)
            reg.address = addr

    def register_valid(self, reg):
        """Returns True if register is semi-valid. May raise exceptions which must be catched"""

        # Check if all required register keys exists
        if not (set(("name", "mode", "type", "description")).issubset(reg) or
                set(("name", "mode", "fields", "description")).issubset(reg)):
            return False

        """Check if name is valid VHDL, if not it will raise an exception which must be
        catched in calling function"""
        is_valid_VHDL(reg['name'])

        """Get a list of the currently used reg names and compare the chosen reg names to this list
        If it is already taken it will raise an exception which must be catched in calling function"""
        reg_names = [r.name for r in self.registers]
        is_unique(reg['name'], reg_names)

        return True

    def count_ro_regs(self):
        return len([reg for reg in self.registers if reg.mode == 'ro'])

    def count_rw_regs(self):
        return len([reg for reg in self.registers if reg.mode == 'rw'])

    def count_pulse_regs(self):
        return len([reg for reg in self.registers if reg.mode == 'pulse'])

    def __str__(self):
        string = "Name: " + self.name + "\n"
        string += "Address width: " + str(self.addr_width) + "\n"
        string += "Data width: " + str(self.data_width) + "\n"
        string += "Description: " + self.description + "\n\n"
        string += "Registers: \n"
        for i, reg in enumerate(self.registers):
            string += indent_string(str(reg), 1)
        return string
