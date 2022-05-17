#!/usr/bin/env python3
import os
import subprocess
import sys


"""
Oznakowanie nazw zmiennych:
"xNazwaZmiennej" - gdzie x to typ zmiennej (s dla string, i dla int, f dla float, l dla list itp.)
To znakowanie stosuje w wiekszosci moich skryptow w celu usprawnienia pracy ze zmiennymi


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


# sprawdzenie czy uzytkownik jest rootem
if os.geteuid() != 0: # jak nie to mowimy mu papa
	print("Please run this script as a root!")
	exit()


# START - sprawdzanie poprawnosci argumentow
if not len(sys.argv) == 3: # jezeli nie zostala podana odpowiednia liczba argumentow
	# wyswietlana zostaje wtedy strona pomocnicza
	print("Usage: ./autouseradd.py sList sInterface")
	print("\tsList - MAC list of new users separated with ; (UPDATE for user upadating)")
	print("\tsInterface - name of network interface that users are connected to")
	exit()

sList = sys.argv[1]
sInterface = sys.argv[2]

try:
	subprocess.check_output(['ifconfig', sInterface],
    	stderr=subprocess.STDOUT)
except subprocess.CalledProcessError: # jezeli interfejs nie jest aktywny lub nie istnieje
	print("Specified interface doesn't exists or is not up")
	exit()

print("All arguments are correct!")
# END - sprawdzanie poprawnosci argumentow

# jezeli to nie tryb UPDATE (UPDATE to tylko refresh pliku drblpush.conf bez dodawania nowych uzytkownikow)
if sList != "UPDATE":
	lMACs = sList.split(";") # wczytanie listy MACow, ktore sa oddzielone ;

	print(lMACs) # Testowe wypisanie wczytanych MACOW - do usuniecia

	lAntiMACs = [] # tablica na uzytkownikow ktorzy sa juz uzytkownikami DRBL-a (w celu unikniecia duplikatow)
	with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "r") as f:
		lCurMACs = [x.strip() for x in f.readlines()] # wczytanie listy macow z konfiguracji serwera
		for iID, sCurNewMAC in enumerate(lMACs): # petla dla kazdego nowego maca do dodania (z listy lMACs)
			for sCurMAC in lCurMACs: # petla dla kazdego aktualnego maca z pliku konfiguracyjnego
				if sCurNewMAC == sCurMAC: # jezeli wykryty zostanie duplikat to dodajemy go do listy niewaznych macow (lAntiMACs)
					print("MAC:", sCurMAC, "is already a user! Skipping it...")
					lAntiMACs.append(iID) # dodanie tego MAC-u do listy


	# Dodawanie nowych MAC-ow do pliku konfiguracyjnego serwera
	with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "a") as f:
		for iID, sCurMAC in enumerate(lMACs):
			if iID in lAntiMACs: # jezeli mamy doczynienia z niewaznym MAC-iem to go pomijamy
				continue

			f.write(sCurMAC+"\n") # wpisujemy nowego MACA do pliku


####### Tutaj dostep ma juz tryb UPDATE ########

# wczytanie liczby uzytkownikow (potrzebna jest do stworzenia nowego pliku drblpush.conf)
with open(os.path.join("/etc/drbl", f"macadr-{sInterface}.txt"), "r") as f:
	iUserNum = len(f.readlines())

print(f"Detected {iUserNum} users")

# Utworzenie nowego pliku drblpush.conf
with open("confs/drblpush-template.conf", "r") as f:
	conf = f.readlines()
	for i, line in enumerate(conf):
		if "~" in line: # ~ zamienione zostanie na liczbe uzytkownikow
			conf[i] = line.replace("~", str(iUserNum))
		if "$" in line: # $ zostanie zamienione na nazwe pliku z MAC-ami
			conf[i] = line.replace("$", f"macadr-{sInterface}.txt")
		if "@" in line: # @ zostanie zamienione na nazwe interfejsu
			conf[i] = line.replace("@", sInterface)
		# w celu sprawdzenia o co chodzi z tymi symbolami sprawdz plik confs/drblpush-template.conf
		# gdzie odpowiednie symbole sa wpisane w odpowiednie miejsca pliku konfiguracyjnego
	with open("confs/drblpush.conf", "w") as out:
		out.writelines(conf) # zapisanie nowej wersji pliku

print("Created new config file!")


# zastosowanie nowej konfiguracji DRBL-a uwzgledniajacej nowych uzytkownikow 
# (z komenda yes, aby pominac zapytania)
os.system('yes "" | sudo drblpush -d -c $(pwd)/confs/drblpush.conf')

print("DONE!")
