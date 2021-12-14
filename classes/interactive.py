#!/usr/bin/env python3


"""
Funkcje do komunikacji użytkownikiem.

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


if __name__ == "__main__": # wywolanie glownej funkcji programu po uruchomieniu skryptu
    print("Ten skrypt jest jedynie do importowania!")

