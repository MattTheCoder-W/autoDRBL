#!/usr/bin/env python3
import sys
import os
from drbltools import showActiveUsers


"""
Usage:
	./listusers.py sInterface
		-> sInterface - name of interface to which users are connected

Author: Mateusz Wasaznik 3hSP
"""

if not len(sys.argv) == 2:
	print("Usage: ./listusers.py sInterface")
	print("\tsInterface - name of interface to which users are connected")
	exit()

sInterface = sys.argv[1]

if not os.path.exists(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt")):
	print("Specified interface is not running on DRBL!")
	exit()

print("All arguments are correct!")


showActiveUsers(sInterface)

print("DONE!")
