#!/usr/bin/env python3
import os
import sys
import subprocess
from curtsies.fmtfuncs import yellow, red, blue, green, bold
from classes.drbltools import findIP
from bs4 import BeautifulSoup as bs


"""
Usage:
	./autoclone.py sImg sInterface
		-> sImg - image folder name form /home/partimag catalog
		-> sInterface - name of network interface that users are connected to

	Example:
		./autoclone.py ubuntu-10 local-macs.txt enp0s8


This script contains is full automation of DRBL image deploying process
and Waking On LAN specified users with automatic restoration of specified
system image

Author: Mateusz Wasaznik 3hSP
"""


def secureInput(content, nospaces=False, numeric=False, inRange=None):
	while True:
		answ = input(content)
		if not answ:
			print("Please specify value!")
			continue
		if nospaces:
			if " " in answ:
				print("No spaces allowed!")
				continue
		if numeric:
			if not answ.isnumeric():
				print("This value has to be numeric!")
				continue
			answ = int(answ)
		if inRange:
			if not int(answ) in inRange:
				print("Number out of range!")
				continue
		break
	return answ


def choiceFromList(lChoices, inputContent=""):
	for i, elem in enumerate(lChoices):
		print(f"[{i}]", elem)

	iChoice = secureInput(inputContent, nospaces=True, numeric=True, inRange=range(0, len(lChoices)))

	return (iChoice, lChoices[iChoice])


def loadxml(sXmlFilePath):
	with open(sXmlFilePath, "r") as f:
		data = f.read()

	BsContent = bs(data, "xml")

	lSale = BsContent.find_all("sala")

	iIdSala, iNumSala = choiceFromList([x.get("num") for x in lSale], "$> ")

	print("Wybrano numer sali:", iNumSala)

	lUserGroups = lSale[iIdSala].find_all("users")

	if len(lUserGroups) > 1:
		sTyp = choiceFromList([x.get("typ") for x in lUserGroups], f"[{iNumSala}]$> ")[1]
	else:
		sTyp = None

	if sTyp is not None:
		print("Wybrano tryb:", sTyp)

	for users in lUserGroups:
		if users.get("typ") == sTyp:
			lMacs = users.text.split()

	return lMacs


def autoclone(args):
	# START Check all script argumets
	if len(args) != 4:
		print("Usage: sudo ./autoclone.py img interface macXmlFile")
		print("\timg - image folder name from /home/partimag/")
		print("\tnterface - network interface name that users are connected to")
		print("\tmacXmlFile - path to .xml file that contains structure of users MACS")
		exit()

	sImg = args[1]
	sInterface = args[2]
	sXmlPath = args[3]

	if not os.path.exists(os.path.join("/home/partimag", sImg)):
		print("Image name doesn't exist! Try finding right name by command: 'ls /home/partimag'")
		exit()

	try:
		subprocess.check_output(['ifconfig', sInterface],
	    	stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError:
		print("Specified interface doesn't exists or is not up")
		exit()

	if not os.path.exists(sXmlPath):
		print("XML file doesn't exist!")
		exit()

	print("All parameters are correct!")
	# END Check all script argumets


	lUsers = loadxml(sXmlPath)

	for i, sUser in enumerate(lUsers):
		print(f"[{i}] {sUser}")

	lMacUsers = lUsers.copy()

	# Convert loaded MACs to user logical IPs (which are stored in drbl files)
	lIPUsers = []
	for sMac in lMacUsers:
		sFoundIP = findIP(sMac, sInterface="enp0s8")
		if not sFoundIP:
			print("MAC:", sMac, "is not in users list!")
			print("This script will automatically add non existing users to DBRL!")
			
			os.system(f"sudo ./autouseradd.py '{';'.join(lUsers)}' {sInterface}")

			sFoundIP = findIP(sMac, sInterface="enp0s8")

		lIPUsers.append(sFoundIP)

	lIPUsers = ' '.join(lIPUsers)
	cmd = f'yes "" | sudo drbl-ocs -g auto -e1 auto -e2 -x -r -j2 -k1 -sc0 -icds -p reboot --hosts " {lIPUsers} " -l en_US.UTF-8 startdisk restore {sImg} sda'

	print(green("Deploying image..."))
	os.system(cmd)

	for sWakeOnLan in lMacUsers:
		os.system(f"sudo etherwake -i {sInterface} {sWakeOnLan}")

	print(green("DONE!"))

if __name__ == "__main__":
	autoclone(sys.argv)
