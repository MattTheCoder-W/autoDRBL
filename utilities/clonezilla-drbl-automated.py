#!/usr/bin/env python3

import os
from curtsies.fmtfuncs import yellow, red, blue, green, bold

def askyn(content):
	answ = None
	while True:
		answ = input(content)
		if not answ.lower() in ['y', 'n']:
			print(red("Choose correct answer!"))
			continue
		answ = True if answ.lower() == "y" else False
		break
	return answ

def secureInput(content, nospaces=False, numeric=False):
	while True:
		answ = input(content)
		if not answ:
			print(bold(red("Please specify value!")))
			continue
		if nospaces:
			if " " in answ:
				print(bold(red("No spaces allowed!")))
				continue
		if numeric:
			if not answ.isnumeric():
				print(bold(red("This value has to be numeric!")))
				continue
			answ = int(answ)
		break
	return answ

filter = askyn("Do you want to select specific users?: ")

print("Avaliable images:")
images = os.listdir("/home/partimag/")
for i, img in enumerate(images):
	print(f"[{i}] {img}")

while True:
	try:
		img_name = images[secureInput("Select image id: ", numeric=True)]
	except IndexError:
		print(bold(red("Specified value is out of id-s range!")))
		continue
	break

if filter:
	print("Select mac-list file:")

	macFiles = []
	for file in os.listdir("/etc/drbl/"):
		if file.startswith("macadr-"):
			macFiles.append(file)

	for i, file in enumerate(macFiles):
		print(f"[{i}] {file}")

	while True:
		fileName = secureInput("$> ", numeric=True)
		if fileName not in range(0, len(macFiles)):
			print(red("Value out of range!"))
			continue
		fileName = macFiles[fileName]
		print(green(f"Selected file: {fileName}"))
		break

	users = []
	with open(f"/etc/drbl/{fileName}", "r") as f:
		for line in f.readlines():
			if not "#" in line.strip():
				users.append(line.strip())
	for i, user in enumerate(users):
		print(f"[{i}] {user}")
	selection = secureInput("Type users id-s separated by spaces (eg. 0 1 2 3): ")
	selUsers = []
	for uId in selection.split(" "):
		try:
			# selUsers.append(users[int(uId)]) # Old version (not working)
			for file in os.listdir("/etc/drbl/"):
				if "clients-of" in file and file.endswith(".txt"):
					with open(os.path.join("/etc/drbl", file)) as iptab:
						lines = iptab.readlines()
						curIp = lines[int(uId)].strip()
						print(f"Resolved {users[int(uId)]} as {curIp}")
						selUsers.append(curIp)
		except IndexError:
			print(bold(red(f"User ID: {uId} is out of user range! Skipping it...")))
		except ValueError:
			pass

	usersPart = " " + " ".join(selUsers)

	cmd = f'sudo drbl-ocs -g auto -e1 auto -e2 -x -r -j2 -k1 -sc0 -icds -p reboot -h "{usersPart}" -l en_US.UTF-8 startdisk restore {img_name} sda'
else:
	cmd = f"sudo drbl-ocs -g auto -e1 auto -e2 -x -r -j2 -k1 -sc0 -icds -p reboot -l en_US.UTF-8 startdisk restore {img_name} sda"

print(green("Deploying image..."))
os.system(cmd)

print(green("DONE!"))
