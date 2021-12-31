import sys
import network

network_ipv4 = network.Network.routing_table()
assert isinstance(network_ipv4, dict), f"network_ipv4 should be an instance of dict but it's actually {type(network_ipv4)}."
print("Importing network worked!")