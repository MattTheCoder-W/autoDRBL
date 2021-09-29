#!/usr/bin/env python3
import os
import subprocess


"""
This script contains all neccessary tools for DRBL automation
Author: Mateusz Wasaznik 3hSP
Bugs to fix: None
"""

"""
findIP
	takes:
		-> sMac - MAC address in string variable
		-> sInterface - interface name
						that user with specified MAC is connected to
	returns:
		-> False - if specified MAC was not identified in DRBL files
		-> sFoundIP - found logical IP address in string variable
"""


def findIP(sMac, sInterface, verbose=False):
	# get interface ip to locate IP list file (its name is "clients-of-{IP}.txt")
	sIntIP = subprocess.check_output(['./utilities/drbl-get-ipadd', sInterface]).decode().strip()

	sIPListFile = os.path.join("/etc/drbl", f"clients-of-{sIntIP}.txt")
	# Load IP list
	with open(sIPListFile, "r") as f:
		lIPs = [x.strip() for x in f.readlines()]

	sMACListFile = os.path.join("/etc/drbl", f"macadr-{sInterface}.txt")
	# Load MAC list
	with open(sMACListFile, "r") as f:
		lMACs = [x.strip() for x in f.readlines()]

	if verbose:
		print("Interface IP is:", sIntIP)
		print("List of IPs:", lIPs)
		print("List of MACs:", lMACs)

	# List of MACs and IP should be the same length,
	# if not that means that some of users don't have
	# associated logical address and the autoclone cannot proceed
	if len(lIPs) != len(lMACs):
		print("IP list file and MAC list file are not consistent! Readd all users!")
		return False

	bFound = False
	for i, sCurMAC in enumerate(lMACs):
		if sCurMAC == sMac:
			sFoundIP = lIPs[i]
			bFound = True

	return False if not bFound else sFoundIP


def showActiveUsers(sInterface):
	if not os.path.exists(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt")):
		return False
	lMACs = []
	with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "r") as f:
		for sMAC in f.readlines():
			lMACs.append(sMAC.strip())

	for sMAC in lMACs:
		sFoundIP = findIP(sMAC, sInterface)
		if sFoundIP:
			print(f"{sMAC}\t{sFoundIP}")


if __name__ == "__main__":
	print(findIP("08:00:27:ad:f6:65", "enp0s8"))
	print(showActiveUsers("enp0s8"))
