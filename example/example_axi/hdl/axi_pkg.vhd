library ieee;
  use ieee.std_logic_1164.all;

package axi_pkg is

  constant c_axi_data_width : natural := 32;
  constant c_axi_addr_width : natural := 32;

  subtype t_axi_data is std_logic_vector(c_axi_data_width - 1 downto 0);
  subtype t_axi_addr is std_logic_vector(c_axi_addr_width - 1 downto 0);

  type t_axi_mosi is record
    araddr  : t_axi_addr;
    arvalid : std_logic;
    awaddr  : t_axi_addr;
    awvalid : std_logic;
    bready  : std_logic;
    rready  : std_logic;
    wdata   : t_axi_data;
    wvalid  : std_logic;
  end record;

  type t_axi_miso is record
    arready : std_logic;
    awready : std_logic;
    bresp   : std_logic_vector(1 downto 0);
    bvalid  : std_logic;
    rdata   : t_axi_data;
    rresp   : std_logic_vector(1 downto 0);
    rvalid  : std_logic;
    wready  : std_logic;
  end record;

end axi_pkg;
