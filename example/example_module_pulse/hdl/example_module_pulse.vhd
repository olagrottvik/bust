library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.axi_pkg.all;
use work.example_module_pulse_pif_pkg.all;

entity example_module_pulse is

  port (

    -- AXI Bus Interface
    axi_clk      : in  std_logic;
    axi_areset_n : in  std_logic;
    axi_in       : in  t_axi_interconnect_to_slave;
    axi_out      : out t_axi_slave_to_interconnect
    );

end entity example_module_pulse;

architecture behavior of example_module_pulse is

  signal axi_pulse_regs : t_example_module_pulse_pulse_regs := c_example_module_pulse_pulse_regs;

begin

  i_example_module_pulse_axi_pif : entity work.example_module_pulse_axi_pif
    port map (
      axi_pulse_regs => axi_pulse_regs,
      clk            => axi_clk,
      areset_n       => axi_areset_n,
      awaddr         => axi_in.awaddr(C_EXAMPLE_MODULE_PULSE_ADDR_WIDTH-1 downto 0),
      awvalid        => axi_in.awvalid,
      awready        => axi_out.awready,
      wdata          => axi_in.wdata(C_EXAMPLE_MODULE_PULSE_DATA_WIDTH-1 downto 0),
      wvalid         => axi_in.wvalid,
      wready         => axi_out.wready,
      bresp          => axi_out.bresp,
      bvalid         => axi_out.bvalid,
      bready         => axi_in.bready,
      araddr         => axi_in.araddr(C_EXAMPLE_MODULE_PULSE_ADDR_WIDTH-1 downto 0),
      arvalid        => axi_in.arvalid,
      arready        => axi_out.arready,
      rdata          => axi_out.rdata(C_EXAMPLE_MODULE_PULSE_DATA_WIDTH-1 downto 0),
      rresp          => axi_out.rresp,
      rvalid         => axi_out.rvalid,
      rready         => axi_in.rready
      );

end architecture behavior;