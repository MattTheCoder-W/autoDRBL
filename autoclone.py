#!/usr/bin/env python3
import os, sys, subprocess
from classes.drbltools import findIP
from classes.interactive import secureInput, choiceFromList, message
from classes.argtypes import dir_path, file_path, interface
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

# Funkcja do wczytywania listy macow z pliku xml, wraz z wyborem sali oraz typu komputerow
# sXMLFilePath - 
def loadxml(sXmlFilePath: str):
    # Wczytanie zawartosci pliku xml
    data = open(sXmlFilePath, "r").read() 

    # Zaladowanie zawartosci xml do parsera-xml (tutaj BeautifulSoup4)
    BsContent = bs(data, "xml")

    # Pobranie listy sal
    lSale = BsContent.find_all("sala")
    # Wczytanie indeksu wybranej sali oraz jej numeru fizycznego
    iIdSala, iNumSala = choiceFromList([x.get("num") for x in lSale], "$> ")
    message("Wybrano numer sali:" + str(iNumSala))

    # Znalezienie listy grup uzytkownikow
    lUserGroups = lSale[iIdSala].find_all("users")
    
    if len(lUserGroups) > 1:
        # Wczytanie typu komputerow od uzytkownika
        sTyp = choiceFromList([x.get("typ") for x in lUserGroups], f"[{iNumSala}]$> ")[1]
        message(f"Wybrano typ pc: {sTyp}")
    else:
        sTyp = None # nie ma typu komputerow

    lMacs = [users.text.split() for users in lUserGroups if users.get("typ") == sTyp][-1]
    return lMacs


def raise_error(content: str):
    print(f">>> {content} <<<")
    exit(1)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("img", type=dir_path, action="store")
    parser.add_argument("interface", type=interface, action="store")
    parser.add_argument("xml", type=file_path, action="store")
    args = parser.parse_args()
    args = dict(vars(args))
    return args


# Funkcja do automatycznego wczytania obrazu systemu przez uzytkownikow DRBL-a (wraz z WOL)
# args - argumenty komendy (tutaj sys.arv), lecz w przyszlej automatyzacji mozna wywolywac funkcje bezposrednio w pythona
def autoclone():
    args = get_args()

    sImg = args['img'].split("/")[-1]

    message("Image name is: " + sImg)
    sInterface = args['interface']
    sXmlPath = args['xml']

    lMacUsers = loadxml(sXmlPath) # Wczytanie listy MAC-ow z pliku xml (funkcja loadxml)
    for i, sUser in enumerate(lMacUsers):
        print(f"[{i}] {sUser}")

    # START - Zamiana kazdego adresu MAC na adres logiczny uzytkownika wewnatrz sieci DRBL-a
    lIPUsers = [] # tablica na zamienione adresy IPv4
    for sMac in lMacUsers:
        sFoundIP = findIP(sMac, sInterface=sInterface) # Wykorzystanie funkcji z pliku classes/drbltools.py (znalezienie adresu IP dla podanego adresu MAC)
        if not sFoundIP: # Jezeli nie znaleziono uzytkownika
            message(f"MAC: {sMac} is not in users list!")
            message("This script will automatically add non existing users to DBRL!")
            
            os.system(f"sudo ./autouseradd.py '{';'.join(lIPUsers)}' {sInterface}") # Dodanie uzytkownika do DRBL-a (skrypt autouseradd.py)

            sFoundIP = findIP(sMac, sInterface=sInterface) # ponowne znalezienie adresu IP dla nowo dodanego uzytkownika
        lIPUsers.append(sFoundIP) # dolaczenie znalezionego adresu IP do listy adresow uzytkownikow
    # END - Zamiana kazdego adresu MAC na adres logiczny uzytkownika wewnatrz sieci DRBL-a

    sIPUsers = ' '.join(lIPUsers) # zamiana listy adresow IP na tekst (adresy oddzielone sa spacjami zgodnie z skladnia komendy drbl-ocs)
    
    # sformuowanie komendy drbl-ocs do przypisania wczytania obrazu systemu przez znalezionych uzytkownikow
    # komenda "yes" z parametrem "" wciska enter na kazde zapytanie komendy drbl-ocs co pozwala na wywolanie skryptu bez obecnosci uzytkownika
    # (np. przez crona)
    cmd = f'yes "" | sudo drbl-ocs -g auto -e1 auto -e2 -x -r -j2 -k1 -sc0 -icds -p poweroff --hosts " {sIPUsers} " -l en_US.UTF-8 startdisk restore {sImg} sda'

    message("Deploying image...")
    os.system(cmd) # wywolanie sformuowanej komendy

    for sWakeOnLan in lMacUsers:
        os.system(f"sudo etherwake -i {sInterface} {sWakeOnLan}") # wyslanie magic packet dla kazdego uzytkownika
        # UWAGA! nie jest sprawdzane to czy doszedl on do uzytkownika!

    message("DONE!")

if __name__ == "__main__": # wywolanie glownej funkcji programu po uruchomieniu skryptu
    autoclone()
