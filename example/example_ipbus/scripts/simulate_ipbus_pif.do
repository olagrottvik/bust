# Set default error behaviour
if {[batch_mode]} {
  onerror {abort all; exit -f -code 1}
} else {
  onerror {abort all}
}

# Shut down running simulation
quit -sim

# Set project paths
set example_ipbus_path "../"
set bus_path "../../../../ipbus-firmware"
set UVVM_path "../../../../UVVM"
set vip_ipbus_path "../../../../vip_ipbus"

# Compile UVVM Dependencies
do $UVVM_path/script/compile_all.do $UVVM_path/script $example_ipbus_path/sim $example_ipbus_path/scripts/component_list.txt

# Set vcom args
set vcom_args "-quiet +cover=sbt"

###########################################################################
# Compile bus source files into library
###########################################################################

# Set up library and sim path
set lib_name "ipbus"
set bus_sim_path "$example_ipbus_path/sim"

# (Re-)Generate library and Compile source files
echo "\nRe-gen lib and compile $lib_name source\n"
if {[file exists $bus_sim_path/$lib_name]} {
  file delete -force $bus_sim_path/$lib_name
}

vlib $bus_sim_path/$lib_name
vmap $lib_name $bus_sim_path/$lib_name

set vhdldirectives "-2008 -work $lib_name"

eval vcom $vcom_args $vhdldirectives $bus_path/components/ipbus_core/firmware/hdl/ipbus_package.vhd

# Compile vip_ipbus Dependencies
do $vip_ipbus_path/scripts/compile_src.do $vip_ipbus_path $vip_ipbus_path/sim


###########################################################################
# Compile source files into library
###########################################################################

# Set up library and sim path
set lib_name "example_ipbus"
set example_ipbus_sim_path "$example_ipbus_path/sim"

# (Re-)Generate library and Compile source files
echo "\nRe-gen lib and compile $lib_name source\n"
if {[file exists $example_ipbus_sim_path/$lib_name]} {
  file delete -force $example_ipbus_sim_path/$lib_name
}

vlib $example_ipbus_sim_path/$lib_name
vmap $lib_name $example_ipbus_sim_path/$lib_name

set vhdldirectives "-2008 -work $lib_name"

eval vcom $vcom_args $vhdldirectives $example_ipbus_path/hdl/example_ipbus_pif_pkg.vhd
eval vcom $vcom_args $vhdldirectives $example_ipbus_path/hdl/example_ipbus_ipb_pif.vhd

###########################################################################
# Compile testbench files into library
###########################################################################
set vcom_args "-quiet"
eval vcom $vcom_args $vhdldirectives $example_ipbus_path/tb/example_ipbus_ipb_pif_tb.vhd

###########################################################################
# Simulate
###########################################################################
vsim -quiet -coverage example_ipbus.example_ipbus_ipb_pif_tb

# Trick to avoid metastability warnings
set NumericStdNoWarnings 1
run 1 ns;
set NumericStdNoWarnings 0
run -all

coverage report
coverage report -html -htmldir covhtmlreport -code bcefst
