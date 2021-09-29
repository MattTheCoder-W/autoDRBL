# autoDRBL
Automatyzacja serwera DRBL.

## Wymagania
Linux:

```
sudo apt update
sudo apt install etherwake
```

Python 3:

[requirements.txt](requirements.txt)

```
sudo pip3 install -r requirements.txt
pip3 install -r requirements.txt
```

---

## Sposob uzycia

### Przygotowanie
1. Przygotowac obraz sysytemu, znajdujacy sie pod sciezka `/home/partimag/OBRAZ`
2. Ustawic odpowiedni interfejs sieciowy pod serwer DRBL (w przykladzie `enp0s8`)
3. Przygotowac liste MAC adresow w pliku XML zgodnym ze struktura znajdujaca sie w pliku [macs.xml](testFiles/macs.xml)

### Automatyczny WakeOnLAN

`sudo ./autoclone.py img interface xml`

| parametr | opis | przyklad |
| -------- | ---- | -------- |
| `img` | nazwa obrazu | `ubuntu-10` (/home/partimag/ubuntu-10) |
| `interface` | int. sieciowy | `enp0s8` |
| `xml` | plik xml | `testFiles/macs.xml` |

Przyklad:

`sudo ./autoclone.py ubuntu-10 enp0s8 testFiles/macs.xml`

Po wywolaniu tej komendy skrypt:

* sprawdzi poprawnosc podanych argumentow
* wczyta plik xml oraz zaladuje MAC adresy
	- upewni sie ze wszystkie MAC adresy naleza do istniejacych uzytkownikow DRBL, a w przypadku znalezienia nowych adresow, doda je do bazy adresow DRBL-a
* korzystajac z komendy `drbl-ocs` ustawi automatyczne wczytywanie wybranego obrazu systemu przez uzytkownikow
* wysle magic packets, w celu wywolania WakeOnLAN-a dla wybranych uzytkownikow
* Uzytkownicy po poprawnym zaldowaniu obrazu automatycznie sie wylacza