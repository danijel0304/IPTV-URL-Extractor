# IPTV URL Extractor

Desktop aplikacije za pronalaženje IPTV playlist URL-ova (`.m3u` i `.m3u8`)
u tekstu, datotekama i web-sadržaju.

## Datoteke

### `iptv_url_extractor_basic.py`

Osnovna, potpuno lokalna verzija:

- učitava tekstualne datoteke
- pronalazi HTTP i HTTPS URL-ove
- izdvaja `.m3u` i `.m3u8` poveznice
- prepoznaje `m3u` u parametrima URL-a
- uklanja duplikate
- sortira rezultate prema serveru
- kopira ili sprema rezultate u `.txt` datoteku

Ova verzija ne pristupa internetu i ne provjerava rade li pronađene liste.

### `iptv_url_extractor_pro.py`

Napredna verzija s dodatnim mogućnostima:

- preuzima tekst s unesene web-adrese
- podržava crnu i bijelu listu pojmova
- prikazuje najčešće pronađene servere
- brzo provjerava odgovaraju li playlist URL-ovi
- dubinski provjerava može li se dohvatiti sadržaj video-streama
- paralelno provjerava više poveznica
- sprema rezultate kao `.m3u` ili `.txt`

Ova verzija pristupa internetu pri preuzimanju stranice i provjeri poveznica.

## Zahtjevi

- Python 3.8 ili noviji
- Tkinter
- Za Pro verziju: `customtkinter` i `requests`

Na Debian/Ubuntu sustavima Tkinter se po potrebi instalira naredbom:

```bash
sudo apt install python3-tk
```

Python paketi za Pro verziju:

```bash
python3 -m pip install -r requirements.txt
```

## Pokretanje

Osnovna verzija:

```bash
python3 iptv_url_extractor_basic.py
```

Pro verzija:

```bash
python3 iptv_url_extractor_pro.py
```

### Pokretanje bez Winea

Program je Python/Tkinter aplikacija i može raditi nativno na Windowsu i
Linuxu. Wine nije potreban ako se pokreće Python skripta ili build napravljen
za taj operacijski sustav.

Na Linuxu:

```bash
python3 -m pip install -r requirements.txt
./run_pro_linux.sh
```

Na Windowsu:

```bat
py -3 -m pip install -r requirements.txt
run_pro_windows.bat
```

Ako se na Linuxu pokreće Windows `.exe`, sustav ga može otvoriti kroz Wine.
To nije nativno Linux pokretanje. Za Linux treba pokrenuti `.py` datoteku ili
napraviti poseban Linux build na Linux računalu.

### Izrada nativne izvršne datoteke

Windows `.exe` i Linux izvršna datoteka moraju se graditi odvojeno na svojem
operacijskom sustavu.

Windows build:

```bat
py -3 -m pip install pyinstaller -r requirements.txt
py -3 -m PyInstaller --noconfirm --onefile --windowed --name IPTV-URL-Extractor-Pro --collect-all customtkinter iptv_url_extractor_pro.py
```

Linux build:

```bash
python3 -m pip install pyinstaller -r requirements.txt
python3 -m PyInstaller --noconfirm --onefile --windowed --name iptv-url-extractor-pro --collect-all customtkinter iptv_url_extractor_pro.py
```

Rezultat se nalazi u mapi `dist/`.

## Korištenje

1. Otvorite datoteku ili zalijepite tekst u lijevo polje.
2. Podesite željene filtre.
3. Kliknite gumb za izvlačenje URL-ova.
4. Pregledajte rezultate u desnom polju.
5. Kopirajte rezultate ili ih spremite u datoteku.

U Pro verziji web-adresu možete unijeti u gornje polje, a zatim odabrati
preuzimanje sadržaja. Mrežne provjere šalju HTTP zahtjeve prema pronađenim
adresama.

## Napomena

Program koristi heuristiku. Pronađena poveznica nije nužno valjana, aktivna
ili dostupna. Program koristite samo za sadržaj i sustave za koje imate
odgovarajuće dopuštenje.
