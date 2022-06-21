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

## Sposób użycia

### Przygotowanie
1. Przygotować obraz sysytemu, znajdujacy się pod sciezką `/home/partimag/OBRAZ`
2. Ustawić odpowiedni interfejs sieciowy pod serwer DRBL (w przykladzie `enp0s8`)
3. Przygotować listę MAC adresów w pliku XML zgodnym ze strukturą znajdujacą się w pliku [macs.xml](testFiles/macs.xml)

### Automatyczny WakeOnLAN

`./autoclone.py img interface xml wakeonlan`

| parametr | opis | przykład |
| -------- | ---- | -------- |
| `img` | nazwa obrazu | `ubuntu-10` (/home/partimag/ubuntu-10) |
| `interface` | int. sieciowy | `enp0s8` |
| `xml` | plik xml | `testFiles/macs.xml` |
| `wakeonlan` | czy wykonać wake on lan | `0` lub `1` |

Przykład:

`./autoclone.py ubuntu-10 enp0s8 testFiles/macs.xml 1`

Po wywolaniu tej komendy skrypt:
* sprawdzi poprawność podanych argumentów
* wczyta plik xml oraz załaduje MAC adresy
	- upewni się że wszystkie MAC adresy należą do list istniejacych użytkowników DRBL, a w przypadku znalezienia nowych adresów, doda je do bazy adresów DRBL-a
* korzystając z komendy `drbl-ocs` ustawi automatyczne wczytywanie wybranego obrazu systemu przez użytkowników
* wyśle magic packets, w celu wywołania WakeOnLAN dla wybranych użytkowników
* Użytkownicy po poprawnym załdowaniu obrazu automatycznie się wyłączą
