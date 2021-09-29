# autoDRBL
Automatyzacja serwera DRBL.

## Wymagania
Linux:

```
sudo apt update
sudo apt install etherwake
```

Python 3:

```
sudo pip3 install -r requirements.txt
pip3 install -r requirements.txt
```

---

## Sposob uzycia

### Przygotowanie
1. Przygotowac obraz sysytemu, znajdujacy sie pod sciezka `/home/partimag/OBRAZ`
2. Ustawic odpowiedni interfejs sieciowy pod serwer DRBL (w przykladzie `enp0s8`)
3. Przygotowac liste MAC adresow w pliku XML zgodnym ze struktura znajdujaca sie pod `testFiles/macs.xml` [requirements.txt](requirements.txt)

### Automatyczny WakeOnLAN

`sudo ./autoclone.py img interface xml`

| parametr | opis | przyklad |
| -------- | ---- | -------- |
| img | nazwa obrazu | ubuntu-10 (/home/partimag/ubuntu-10) |
| interface | int. sieciowy | enp0s8 |
| xml | plik xml | testFiles/macs.xml |