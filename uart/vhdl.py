import re

from uart.utils import indent_string


def sync_process(clk_name, reset_name, process_name, reset_string, logic_string, active_low=True):
    s = process_name + " : process(" + clk_name + ")\n"
    s += "begin\n"
    s += indent_string("if rising_edge(" + clk_name + ") then\n")
    s += indent_string("if " + reset_name + " = ", 2)

    if active_low:
        s += "'0'"
    else:
        s += "'1'"

    s += " then\n"

    s += indent_string(reset_string, 3)
    s += "\n"
    s += indent_string("else\n", 2)

    s += indent_string(logic_string, 3)
    s += "\n"
    s += indent_string("end if;\n", 2)
    s += indent_string("end if;\n")
    s += "end process " + process_name + ";\n"
    return s


def async_process(clk_name, reset_name, process_name, reset_string, logic_string, active_low=True):
    s = process_name + " : process(" + clk_name + ", " + reset_name  +")\n"
    s += "begin\n"
    s += indent_string("if " + reset_name + " = ")

    if active_low:
        s += "'0'"
    else:
        s += "'1'"

    s += " then\n"

    s += indent_string(reset_string, 2)
    s += "\n"
    s += indent_string("elsif rising_edge(" + clk_name + ") then\n")

    s += indent_string(logic_string, 2)
    s += "\n"
    s += indent_string("end if;\n")
    s += "end process " + process_name + ";\n"

    return s


def comb_process(process_name, logic_string):
    s = process_name + " : process(all)\n"
    s += "begin\n\n"

    s += indent_string(logic_string)

    s += "end process " + process_name + ";\n"

    return s


def get_identifier(msg):
    while True:
        try:
            identifier = input(msg)
            is_valid_VHDL(identifier)
            return identifier
        except Exception as e:
            print(e)


def is_VHDL_keyword(string):
    keywords = ['abs', 'access', 'after', 'alias', 'all', 'and', 'architecture', 'array',
                'assert', 'assume', 'assume_guarantee', 'attribute', 'begin', 'block',
                'body', 'buffer', 'bus', 'case', 'component', 'configuration', 'constant',
                'context', 'cover', 'default', 'disconnect', 'downto', 'else', 'elsif',
                'end', 'entity', 'exit', 'fairness', 'file', 'for', 'force', 'function',
                'generate', 'generic', 'group', 'guarded', 'if', 'impure', 'in', 'inertial',
                'inout', 'is', 'label', 'library', 'linkage', 'literal', 'loop', 'map',
                'mod', 'nand', 'new', 'next', 'nor', 'not', 'null', 'of', 'on', 'open',
                'or', 'others', 'out', 'package', 'parameter', 'port', 'postponed',
                'procedure', 'process', 'property', 'protected', 'pure', 'range', 'record',
                'register', 'reject', 'release', 'rem', 'report', 'restrict',
                'restrict_guarantee', 'return', 'rol', 'ror', 'select', 'sequence',
                'severity', 'shared', 'signal', 'sla', 'sll', 'sra', 'srl', 'strong',
                'subtype', 'then', 'to', 'transport', 'type', 'unaffected', 'units', 'until',
                'use', 'variable', 'vmode', 'vprop', 'vunit', 'wait', 'when', 'while',
                'with', 'xnor', 'xor']

    return string in keywords
    

def contain_spaces(string):
    return ' ' in string


def start_with_alphabetic_letter(string):
    return string[0].isalpha()


def ends_with_underscore(string):
    return string.endswith('_')


def contain_two_successive_underscores(string):
    return '__' in string


def is_only_alpfanum_(string):
    regex = re.compile(r'\W')
    return regex.search(string) is None


def is_valid_VHDL(string):
    if is_VHDL_keyword(string):
        raise InvalidVHDLIdentifier(string + " - identifier cannot contain VHDL keywords.")
    if contain_spaces(string):
        raise InvalidVHDLIdentifier(string + " - identifiers cannot contain spaces.")
    if not start_with_alphabetic_letter(string):
        raise InvalidVHDLIdentifier(string + " - identifiers must start with an alphabetic letter.")
    if ends_with_underscore(string):
        raise InvalidVHDLIdentifier(string + " - identifiers cannot end with underscore.")
    if contain_two_successive_underscores(string):
        raise InvalidVHDLIdentifier(string + " - identifiers cannot contain two successive underscores.")
    if not is_only_alpfanum_(string):
        raise InvalidVHDLIdentifier(string + " - identifiers may only contain alphabetic letters (‘A’ to ‘Z’ and ‘a’ to ‘z’), decimal digits (‘0’ to ‘9’) and the underline character (‘_’)")


class InvalidVHDLIdentifier(Exception):

    def __init__(self, msg):
        s = "\nError in parsing identifier: " + msg
        super().__init__(s)
