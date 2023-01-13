# nxdigital
A Python library that facilitates manipulating models of digital circuits using networkx graphs

nxdigital is meant to be a simple tool for rapid prototyping of EDA algorithms. The circuit is stored as a bypartite graph, with wires and modules stored as two different vertex types. As the name suggests, it's based on the networkx library.

Currently implemented features: 
 * Load and dump netlist in bench format (ISCAS89) - Useful for recreating many scientific publications
 * Dump netlist as structural Verilog - Intended to test circuit function using testbenches, and with Verilog-compatible synthesis tools
 * Reverse topological ordering of the nets

Upcoming features: 
Probably things that enable more practical applications...
