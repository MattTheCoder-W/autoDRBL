#!/usr/bin/env python3
import os
import subprocess
import sys


"""
Usage:
	./autouseradd.py sList sInterface
		-> sList - MAC list of new users separated with ; (UPDATE for only user updating)
		-> sInterface - name of network interface that users are connected to

	Example:
		./autouseradd.py 'mac1;mac2;mac3' enp0s8


This script contains is full automation of adding new computers
to DRBL server network.


Author: Mateusz Wasaznik 3hSP
"""


# Check for root privilidges
if os.geteuid() != 0:
	print(yellow("Please run this script as a root!"))
	exit()


if not len(sys.argv) == 3:
	print("Usage: ./autouseradd.py sList sInterface")
	print("\tsList - MAC list of new users separated with ; (UPDATE for user upadating)")
	print("\tsInterface - name of network interface that users are connected to")
	exit()

sList = sys.argv[1]
sInterface = sys.argv[2]

try:
	subprocess.check_output(['ifconfig', sInterface],
    	stderr=subprocess.STDOUT)
except subprocess.CalledProcessError:
	print("Specified interface doesn't exists or is not up")
	exit()

print("All arguments are correct!")

if sList != "UPDATE":
	lMACs = sList.split(";")

	print(lMACs)

	lAntiMACs = []
	with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "r") as f:
		lCurMACs = [x.strip() for x in f.readlines()]
		for iID, sCurNewMAC in enumerate(lMACs):
			for sCurMAC in lCurMACs:
				if sCurNewMAC == sCurMAC:
					print("MAC:", sCurMAC, "is already a user! Skipping it...")
					lAntiMACs.append(iID)

	with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "a") as f:
		for iID, sCurMAC in enumerate(lMACs):
			if iID in lAntiMACs:
				continue

			f.write(sCurMAC+"\n")


#######

with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "r") as f:
	iUserNum = len(f.readlines())

print(f"Detected {iUserNum} users")

with open("confs/drblpush-template.conf", "r") as f:
	conf = f.readlines()
	for i, line in enumerate(conf):
		if "~" in line:
			conf[i] = line.replace("~", str(iUserNum))
		if "$" in line:
			conf[i] = line.replace("$", f"macadr-{sInterface}.txt")
		if "@" in line:
			conf[i] = line.replace("@", sInterface)
	with open("confs/drblpush.conf", "w") as out:
		out.writelines(conf)

print("Created new config file!")

os.system('yes "" | sudo drblpush -d -c drblpush.conf')

print("DONE!")
