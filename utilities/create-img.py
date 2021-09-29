#!/usr/bin/env python3

import os
from curtsies.fmtfuncs import green, blue, yellow, bold, red

def askyn(content):
	answ = None
	while True:
		answ = input(content)
		if not answ.lower() in ['y', 'n']:
			print(bold(red("Choose correct answer!")))
			continue
		answ = True if answ.lower() == "y" else False
		break
	return answ

def secureInput(content, nospaces=False):
	while True:
		answ = input(content)
		if not answ:
			print(bold(red("Please specify value!")))
			continue
		if nospaces:
			if " " in answ:
				print(bold(red("No spaces allowed!")))
				continue
		break
	return answ

os.system('sudo fdisk -l | grep "Disk /"')

disk = secureInput("Source disk name (eg. sda, sdb, hda): ")

name = secureInput("Final image name (no spaces): ", nospaces=True)

convert = askyn("Convert final disk name to sda for clients (y/n)?: ")

print(disk, name, convert)

print(green("Creating image..."))
os.system(f"sudo ocs-sr -q2 -c -j2 -z1p -i 4096 -fsck -senc -p true -or /home/partimag savedisk {name} {disk}")

if convert:
	print(green("Converting names..."))
	os.system(f"sudo cnvt-ocs-dev -b {name} {disk} sda")

print(green("DONE!"))
