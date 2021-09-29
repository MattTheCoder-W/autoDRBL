#!/usr/bin/env python3
# To run precreated configuration: drblpush -c drblpush.conf

from curtsies.fmtfuncs import green, yellow, red, bold
import os
import sys


if os.geteuid() != 0:
	print(yellow("Please run this script as a root!"))
	exit()


class Menu:
	def __init__(self, macFile=None):
		self.options = [
			[0, "Add new user MAC", self.addNew],
			[1, "Delete user MAC", self.delUser],
			[2, "List Users", self.listUsers],
			[3, "Save edits", self.deploy],
			[4, "Exit", exit]
		]
		self.msg = ""
		self.macFile = macFile

	def addNew(self, specMac=None):
		if not specMac:
			while True:
				print("ADD_NEW_USER_MAC (^C to go back)")
				mac = secureInput("New User MAC (with ':'): ", nospaces=True, mac=True).lower()

				print(yellow(f"MAC: {mac}"))
				if not askyn("Is it correct (y/n)? "):
					continue
				
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
					with open(f"/etc/drbl/{fileName}", "r") as f:
						for line in f.readlines():
							if line.strip() == mac:
								self.msg=bold(red("This user already exists!"))
								return
					os.system(f"echo {mac} >> /etc/drbl/{fileName}")
					break
				break
			self.msg = green("New user added!")
		elif self.macFile:
			with open(self.macFile, "r") as f:
				lines = [x.strip() for x in f.readlines()]
				if specMac in lines:
					print("This user already exists, skipping!")
					return False
			os.system(f"echo {specMac} >> {self.macFile}")
			return True
		else:
			print("Error: MacFile is not specified, contact the author of this script to fix it!")
			exit()



	def delUser(self):
		while True:
			print("DELETE_USER_MAC (^C to go back)")

			print("Select mac file to edit:")

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
				users = []
				with open(f"/etc/drbl/{fileName}", "r") as f:
					for line in f.readlines():
						if line.count(":") == 5:
							users.append(line.strip())
				for i, user in enumerate(users):
					print(f"[{i}] {user}")
				while True:
					macToDel = secureInput("$> ", numeric=True)
					if macToDel not in range(0, len(users)):
						print(red("Value out of range!"))
						continue

					print(yellow("Deleting " + users[macToDel]))
					users.pop(macToDel)
					
					with open(f"/etc/drbl/{fileName}", "w") as f:
						for user in users:
							f.write(user + "\n")

					self.msg = green("User deleted!")
					break
				break
			break

	def listUsers(self):
		print("LIST_USERS (^C to go back):")

		print("Select mac file to view:")
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

			with open(f"/etc/drbl/{fileName}", "r") as f:
				for i, line in enumerate(f.readlines()):
					print(f"[{i}] {line.strip()}")

			input("...")
			break

	def deploy(self, special=False):
		if not special:
			print("SAVE_EDITS")

			if askyn("Are you sure (y/n)? "):
				print("Select mac file to save:")
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
				userNum = 0
				with open(f"/etc/drbl/{fileName}", "r") as f:
					userNum = len(f.readlines())

				print(green(f"Detected {userNum} users"))

				with open("drblpush-template.conf", "r") as f:
					conf = f.readlines()
					for i, line in enumerate(conf):
						if "~" in line:
							conf[i] = line.replace("~", str(userNum))
						if "$" in line:
							conf[i] = line.replace("$", fileName)
					with open("drblpush.conf", "w") as out:
						out.writelines(conf)

				print(green("Created new config file!"))

				os.system('yes "" | sudo drblpush -d -c drblpush.conf')
			else:
				self.msg = bold(yellow("Changes has not been saved!"))
		elif self.macFile:
			with open(self.macFile, "r") as f:
				userNum = len(f.readlines())

			print(green(f"Detected {userNum} users"))

			with open("drblpush-template.conf", "r") as f:
				conf = f.readlines()
				for i, line in enumerate(conf):
					if "~" in line:
						conf[i] = line.replace("~", str(userNum))
					if "$" in line:
							conf[i] = line.replace("$", self.macFile)
				with open("drblpush.conf", "w") as out:
					out.writelines(conf)

			print(green("Created new config file!"))
			print("HELLO")
			os.system("sudo drblpush --debug -c drblpush.conf -q")
		else:
			print("Error: MacFile is not specified, contact the author of this script to fix it!")
			exit()

	def main(self):
		while True:
			os.system("clear")
			print("USER_MANAGER")
			for option in self.options:
				print(f"{option[0]} > {option[1]}")
			if self.msg:
				print("="*20)
				print(self.msg)
				print("="*20)
				self.msg = ""
			else:
				print("="*20)
			try:
				choice = secureInput("$> ", numeric=True)
			except KeyboardInterrupt:
				print()
				exit()
			if choice not in range(0, len(self.options)):
				self.msg = yellow("Wrong number!")
				continue

			os.system("clear")
			try:
				self.options[choice][2]()
			except KeyboardInterrupt:
				pass


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

def secureInput(content, nospaces=False, numeric=False, mac=False):
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
		if mac:
			if answ.count(":") != 5 or len(answ) != 17:
				print(bold(red("This is not correct MAC address!")))
				continue
		break
	return answ

if "-l=" in '$'.join(sys.argv):
	menu = Menu(macFile="/etc/drbl/macadr-enp0s8.txt")

	print("Running in automation mode!")
	for opt in sys.argv:
		if "-l=" in opt:
			listFile = opt.split("=")[-1]
	print(listFile)
	if not os.path.exists(listFile):
		print("Specified MAC list doesn't exits!")
		exit()
	lMacs = [mac.strip() for mac in open(listFile, "r").readlines()]
	for mac in lMacs:
		print(mac)
		if menu.addNew(specMac=mac):
			print("DONE!")
		else:
			print("ERROR")

	menu.deploy(special=True)
else:
	menu = Menu()

	menu.main()
