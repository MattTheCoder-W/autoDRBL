#!/usr/bin/env python3
import os
import sys
import subprocess
from curtsies.fmtfuncs import yellow, red, blue, green, bold
from classes.drbltools import findIP
from bs4 import BeautifulSoup as bs
import argparse


"""
Oznakowanie nazw zmiennych:
"xNazwaZmiennej" - gdzie x to typ zmiennej (s dla string, i dla int, f dla float, l dla list itp.)
To znakowanie stosuje w wiekszosci moich skryptow w celu usprawnienia pracy ze zmiennymi

Usage:
    ./autoclone.py sImg sInterface macXmlFile
        -> sImg - image folder name form /home/partimag catalog
        -> sInterface - name of network interface that users are connected to
        -> macXmlFile - file with xml structure with mac addresses of clients
    Example:
        ./autoclone.py ubuntu-10 enp0s8 testFiles/macs.xml


This script contains is full automation of DRBL image deploying process
and Waking On LAN specified users with automatic restoration of specified
system image

Author: Mateusz Wasaznik 3hSP
"""


# Ta funkcja pozwala na proszenie uzytkownika w nieskonczonej petli do momentu popdania odpowiedzi spelniajacej kryteria
# content - tresc zapytania, nospaces - czy nie zezwalac na spacje, numeric - czy odpowiedz ma byc liczba, inRange - zakres w jakim ma byc odpowiedz
def secureInput(content, nospaces=False, numeric=False, inRange=None):
    while True:
        answ = input(content)
        if not answ: # Jezeli brak odpowiedzi
            print("Please specify value!")
            continue
        if nospaces:
            if " " in answ: # jezeli spacja w odpowiedzi
                print("No spaces allowed!")
                continue
        if numeric:
            if not answ.isnumeric(): # jezeli odpowiedz nie jest liczba
                print("This value has to be numeric!")
                continue
            answ = int(answ)
        if inRange:
            if not int(answ) in inRange: # jezeli odpowiedz jest poza zakresem
                print("Number out of range!")
                continue
        break
    return answ


# Tekstowy wybor elementu z listy przez uzytkownika
# lChoices - lista z wyborami, inputContent - tresc zapytania (jak content w secureInput())
def choiceFromList(lChoices, inputContent=""):
    for i, elem in enumerate(lChoices):
        print(f"[{i}]", elem)

    # wywolanie funkcji secureInput zwracajacej zweryfikowana odpowiedz,
    # ktora ma nie miec spacji, ma byc liczba, oraz ma znajdowac sie w zakresie indeksow podanej listy
    iChoice = secureInput(inputContent, nospaces=True, numeric=True, inRange=range(0, len(lChoices)))

    return (iChoice, lChoices[iChoice])


# Funkcja do wczytywania listy macow z pliku xml, wraz z wyborem sali oraz typu komputerow
# sXMLFilePath - 
def loadxml(sXmlFilePath):
    with open(sXmlFilePath, "r") as f:
        data = f.read() # Wczytanie zawartosci pliku xml

    BsContent = bs(data, "xml") # Zaladowanie zawartosci xml do parsera-xml (tutaj BeautifulSoup4)

    lSale = BsContent.find_all("sala") # Znalezienie listy sal

    iIdSala, iNumSala = choiceFromList([x.get("num") for x in lSale], "$> ") # Wczytanie indeksu wybranej sali oraz jej numeru fizycznego

    print("Wybrano numer sali:", iNumSala)

    lUserGroups = lSale[iIdSala].find_all("users") # Znalezienie listy grup uzytkownikow

    if len(lUserGroups) > 1: # jezeli jest wiecej niz 1 grupa uzytkownikow oznacza to, ze sa one podzielone ze wzgledu na typ komputerow
        sTyp = choiceFromList([x.get("typ") for x in lUserGroups], f"[{iNumSala}]$> ")[1] # Wczytanie typu komputerow od uzytkownika
    else: # jest tylko jedna grupa bez podzialu na typ komp.
        sTyp = None # nie ma typu komputerow

    if sTyp is not None:
        print("Wybrano tryb:", sTyp)

    for users in lUserGroups:
        if users.get("typ") == sTyp: # jezeli typ grupy z listy grup uzytkownikow zgadza sie z wybranym typem
            lMacs = users.text.split() # Wczytanie listy MAC adresow

    return lMacs


def usage_page():
    print("Usage: sudo ./autoclone.py img interface macXmlFile")
    print("\timg - image folder name from /home/partimag/")
    print("\tnterface - network interface name that users are connected to")
    print("\tmacXmlFile - path to .xml file that contains structure of users MACS")
    exit()


def raise_error(content):
    print(f">>> {content} <<<")
    exit(1)


def dir_path(string):
    if os.path.exists(string):
        if os.path.isdir(string):
            return string
        raise NotADirectoryError(string)
    raise FileNotFoundError(string)


def file_path(string): 
    if os.path.exists(string):
        if not os.path.isdir(string):
            return string
        print(string, "is directory, not a file!")
        exit(1)
    raise FileNotFoundError(string)


def interface(string):
    try:
        subprocess.check_output(['ifconfig', string], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError: # Jezeli interfejs nie jest uruchomiony lub nie istnieje
        raise_error("Specified interface doesn't exists or is not up")
    return string


# Funkcja do automatycznego wczytania obrazu systemu przez uzytkownikow DRBL-a (wraz z WOL)
# args - argumenty komendy (tutaj sys.arv), lecz w przyszlej automatyzacji mozna wywolywac funkcje bezposrednio w pythona
def autoclone(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("img", type=dir_path, action="store")
    parser.add_argument("interface", type=interface, action="store")
    parser.add_argument("xml", type=file_path, action="store")
    args = parser.parse_args()
    args = dict(vars(args))

    sImg = args['img'].split("/")[-1]

    print("Image name is:", sImg)

    exit()

    sInterface = args['interface']
    sXmlPath = args['xml']

    lMacUsers = loadxml(sXmlPath) # Wczytanie listy MAC-ow z pliku xml (funkcja loadxml)
    for i, sUser in enumerate(lMacUsers):
        print(f"[{i}] {sUser}")

    print("MACS:", lMacUsers)

    # START - Zamiana kazdego adresu MAC na adres logiczny uzytkownika wewnatrz sieci DRBL-a
    lIPUsers = [] # tablica na zamienione adresy IPv4
    for sMac in lMacUsers:
        sFoundIP = findIP(sMac, sInterface=sInterface) # Wykorzystanie funkcji z pliku classes/drbltools.py (znalezienie adresu IP dla podanego adresu MAC)
        if not sFoundIP: # Jezeli nie znaleziono uzytkownika
            print("MAC:", sMac, "is not in users list!")
            print("This script will automatically add non existing users to DBRL!")
            
            os.system(f"sudo ./autouseradd.py '{';'.join(lIPUsers)}' {sInterface}") # Dodanie uzytkownika do DRBL-a (skrypt autouseradd.py)

            sFoundIP = findIP(sMac, sInterface=sInterface) # ponowne znalezienie adresu IP dla nowo dodanego uzytkownika
        print("Found IP:", sFoundIP)
        lIPUsers.append(sFoundIP) # dolaczenie znalezionego adresu IP do listy adresow uzytkownikow
    # END - Zamiana kazdego adresu MAC na adres logiczny uzytkownika wewnatrz sieci DRBL-a

    print(lIPUsers)

    sIPUsers = ' '.join(lIPUsers) # zamiana listy adresow IP na tekst (adresy oddzielone sa spacjami zgodnie z skladnia komendy drbl-ocs)
    
    # sformuowanie komendy drbl-ocs do przypisania wczytania obrazu systemu przez znalezionych uzytkownikow
    # komenda "yes" z parametrem "" wciska enter na kazde zapytanie komendy drbl-ocs co pozwala na wywolanie skryptu bez obecnosci uzytkownika
    # (np. przez crona)
    cmd = f'yes "" | sudo drbl-ocs -g auto -e1 auto -e2 -x -r -j2 -k1 -sc0 -icds -p reboot --hosts " {sIPUsers} " -l en_US.UTF-8 startdisk restore {sImg} sda'

    print(green("Deploying image..."))
    os.system(cmd) # wywolanie sformuowanej komendy

    for sWakeOnLan in lMacUsers:
        os.system(f"sudo etherwake -i {sInterface} {sWakeOnLan}") # wyslanie magic packet dla kazdego uzytkownika
        # UWAGA! nie jest sprawdzane to czy doszedl on do uzytkownika!

    print(green("DONE!"))

if __name__ == "__main__": # wywolanie glownej funkcji programu po uruchomieniu skryptu
    autoclone(sys.argv)
