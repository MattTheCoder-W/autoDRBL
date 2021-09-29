#!/usr/bin/env python3
import os
import subprocess


"""
Oznakowanie nazw zmiennych:
"xNazwaZmiennej" - gdzie x to typ zmiennej (s dla string, i dla int, f dla float, l dla list itp.)
To znakowanie stosuje w wiekszosci moich skryptow w celu usprawnienia pracy ze zmiennymi


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


# funkcja znajdujaca adres IP uzytkownika o podanym adresie fizycznym MAC
# sMac - adres MAC uzytkownika, sInterface - nazwa interfejsu sieciowego, verbose - tryb gadatliwy (do testow)
def findIP(sMac, sInterface, verbose=False):
	# pozyskanie adresu IP serwera DRBL pod danym interfejsem (gdyz plik zawierajacy adresy IP uzytkownikow nazywa sie clients-of-<IP>.txt)
	sIntIP = subprocess.check_output(['./utilities/drbl-get-ipadd', sInterface]).decode().strip()

	sIPListFile = os.path.join("/etc/drbl", f"clients-of-{sIntIP}.txt") # sciezka do listy adresow IP uzytkownikow

	with open(sIPListFile, "r") as f:
		lIPs = [x.strip() for x in f.readlines()] # wczytanie listy adresow IP

	sMACListFile = os.path.join("/etc/drbl", f"macadr-{sInterface}.txt") # sciezka do listy MAC-ow uzytkownikow

	with open(sMACListFile, "r") as f:
		lMACs = [x.strip() for x in f.readlines()] # wczytanie listy MAC-ow

	if verbose:
		print("Interface IP is:", sIntIP)
		print("List of IPs:", lIPs)
		print("List of MACs:", lMACs)

	# Listy MAC-ow i IP powinny byc tej samej dlugosci (gdyz kazdemu MAC odpowiada jeden adres IP)
	# Jezel tak nie jest oznacza to ze pliki sa nieaktualne lub uszkodzone i w takim wypadku nie mozna kontynuowac
	if len(lIPs) != len(lMACs):
		print("IP list file and MAC list file are not consistent! Readd all users!")
		return False

	bFound = False # falga znalezienia odpowiadajacego adresu IP
	for i, sCurMAC in enumerate(lMACs):
		# jezeli aktualny MAC z listy jest rowny szukanemu macowi to mozna wczytac adres IP o tym samym indeksie w liscie co aktualny MAC
		if sCurMAC == sMac:
			sFoundIP = lIPs[i] # zapisanie do zmiennej znalezionego adresu IP
			bFound = True

	# w przypadku nieznalezienia adresu funkcja zwraca wartosc False co swiadczy o tym, ze uzytkownik nie jest dodany do DRBL-a
	return False if not bFound else sFoundIP


# Funkcja do wyswietlania dodanych uzytkownikow DRBL-a (to tylko dodatek, jest wykorzystywana tylko dla weryfikacji i nie bierze udzialu w automatyzacji)
# sInterface - interfejs sieciowy do sprawdzenia
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
	# w przypadku wywolania tego pliku wywolane zostana funkcje z testowymi argumentami
	# (gdyz ten plik zostal stworzony do bycia imprtowanym przez inne skrypty)
	print(findIP("08:00:27:ad:f6:65", "enp0s8"))
	print(showActiveUsers("enp0s8"))
