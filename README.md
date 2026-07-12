# IPTV URL Extractor

[English](#english) | [Hrvatski](#hrvatski)

## English

Desktop applications for finding IPTV playlist URLs (`.m3u` and `.m3u8`) in
text, local files, and web content.

### Files

#### `iptv_url_extractor_basic.py`

Basic fully local version:

- loads text files
- finds HTTP and HTTPS URLs
- extracts `.m3u` and `.m3u8` links
- detects `m3u` in URL query parameters
- removes duplicates
- sorts results by host
- copies or saves results to a `.txt` file

This version does not access the internet and does not check whether found
playlists are working.

#### `iptv_url_extractor_pro.py`

Advanced version with extra features:

- downloads text from an entered web address
- supports blacklist and whitelist filters
- shows the most common discovered servers
- quickly checks whether playlist URLs respond
- deeply checks whether video stream content can be reached
- checks multiple links in parallel
- saves results as `.m3u` or `.txt`

This version accesses the internet when downloading a web page and when
checking links.

### Requirements

- Python 3.8 or newer
- Tkinter
- For the Pro version: `customtkinter` and `requests`

On Debian/Ubuntu systems, install Tkinter if needed:

```bash
sudo apt install python3-tk
```

Install Python packages for the Pro version:

```bash
python3 -m pip install -r requirements.txt
```

### Running

Basic version:

```bash
python3 iptv_url_extractor_basic.py
```

Pro version:

```bash
python3 iptv_url_extractor_pro.py
```

#### Running without Wine

This is a Python/Tkinter application and can run natively on Windows and Linux.
Wine is not required when you run the Python script or a build created for the
same operating system.

On Linux:

```bash
python3 -m pip install -r requirements.txt
./run_pro_linux.sh
```

On Windows:

```bat
py -3 -m pip install -r requirements.txt
run_pro_windows.bat
```

If you run a Windows `.exe` on Linux, the system may open it through Wine. That
is not native Linux execution. For Linux, run the `.py` file or create a
separate Linux build on a Linux machine.

#### Creating native executables

Windows `.exe` and Linux executables must be built separately on their own
operating systems.

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

The output will be created in the `dist/` folder.

### Usage

1. Open a file or paste text into the left text area.
2. Adjust the filters.
3. Click the URL extraction button.
4. Review the results in the right text area.
5. Copy the results or save them to a file.

In the Pro version, you can enter a web address in the top field and download
its content. Network checks send HTTP requests to the found addresses.

### Note

The program uses heuristics. A discovered link is not necessarily valid, active,
or accessible. Use this program only with content and systems you are authorized
to access.

## Hrvatski

Desktop aplikacije za pronalaženje IPTV playlist URL-ova (`.m3u` i `.m3u8`) u
tekstu, lokalnim datotekama i web-sadržaju.

### Datoteke

#### `iptv_url_extractor_basic.py`

Osnovna, potpuno lokalna verzija:

- učitava tekstualne datoteke
- pronalazi HTTP i HTTPS URL-ove
- izdvaja `.m3u` i `.m3u8` poveznice
- prepoznaje `m3u` u parametrima URL-a
- uklanja duplikate
- sortira rezultate prema serveru
- kopira ili sprema rezultate u `.txt` datoteku

Ova verzija ne pristupa internetu i ne provjerava rade li pronađene liste.

#### `iptv_url_extractor_pro.py`

Napredna verzija s dodatnim mogućnostima:

- preuzima tekst s unesene web-adrese
- podržava crnu i bijelu listu pojmova
- prikazuje najčešće pronađene servere
- brzo provjerava odgovaraju li playlist URL-ovi
- dubinski provjerava može li se dohvatiti sadržaj video-streama
- paralelno provjerava više poveznica
- sprema rezultate kao `.m3u` ili `.txt`

Ova verzija pristupa internetu pri preuzimanju stranice i provjeri poveznica.

### Zahtjevi

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

### Pokretanje

Osnovna verzija:

```bash
python3 iptv_url_extractor_basic.py
```

Pro verzija:

```bash
python3 iptv_url_extractor_pro.py
```

#### Pokretanje bez Winea

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

Ako se na Linuxu pokreće Windows `.exe`, sustav ga može otvoriti kroz Wine. To
nije nativno Linux pokretanje. Za Linux treba pokrenuti `.py` datoteku ili
napraviti poseban Linux build na Linux računalu.

#### Izrada nativne izvršne datoteke

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

### Korištenje

1. Otvorite datoteku ili zalijepite tekst u lijevo polje.
2. Podesite željene filtre.
3. Kliknite gumb za izvlačenje URL-ova.
4. Pregledajte rezultate u desnom polju.
5. Kopirajte rezultate ili ih spremite u datoteku.

U Pro verziji web-adresu možete unijeti u gornje polje, a zatim odabrati
preuzimanje sadržaja. Mrežne provjere šalju HTTP zahtjeve prema pronađenim
adresama.

### Napomena

Program koristi heuristiku. Pronađena poveznica nije nužno valjana, aktivna ili
dostupna. Program koristite samo za sadržaj i sustave za koje imate
odgovarajuće dopuštenje.
