import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
from urllib.parse import urlparse, parse_qs, unquote
import requests
import threading
import concurrent.futures
from collections import Counter

# --- OSNOVNA LOGIKA ---
URL_REGEX = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>\"\]\)]+)")

def normalize_url(u: str) -> str:
    u = u.strip().rstrip('.,;:!?)"]}')
    if u.lower().startswith("www."):
        u = "http://" + u
    return u

def looks_like_iptv_playlist(url: str, allow_m3u8: bool = True, allow_query_m3u: bool = True) -> bool:
    try:
        parsed = urlparse(url)
        path = (parsed.path or "").lower()

        if path.endswith(".m3u") or (allow_m3u8 and path.endswith(".m3u8")):
            return True

        if allow_query_m3u:
            qs = parse_qs(parsed.query)
            for k, vals in qs.items():
                if "m3u" in (k or "").lower():
                    return True
                for v in vals:
                    v_l = unquote(v).lower()
                    if "m3u" in v_l or "m3u8" in v_l:
                        return True
        return False
    except Exception:
        return False

def extract_urls(text: str):
    return [normalize_url(m.group(1)) for m in URL_REGEX.finditer(text)]

# --- GLAVNA APLIKACIJA ---
class IptvExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IPTV URL Extractor Pro (Deep Check Edition)")
        self.geometry("1250x800")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.extracted_urls = []

        # --- 1. GORNJA TRAKA (Web Scraping & Učitavanje) ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))

        ctk.CTkButton(self.frame_top, text="📂 Otvori datoteku", command=self.open_file, width=140).pack(side="left", padx=(0, 10))

        self.web_url_entry = ctk.CTkEntry(self.frame_top, placeholder_text="Zalijepi URL web stranice (npr. forum, pastebin)...", width=400)
        self.web_url_entry.pack(side="left", padx=10)
        ctk.CTkButton(self.frame_top, text="🌐 Povuci s weba", command=self.scrape_web, width=140, fg_color="#005A9E", hover_color="#004578").pack(side="left", padx=10)

        # --- 2. TRAKA S AKCIJAMA ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkButton(self.frame_actions, text="⚡ 1. Izvuci URL-ove", command=self.run_extract, width=140, fg_color="#2FA572", hover_color="#107C41").pack(side="left", padx=(0, 10))

        self.btn_fast_check = ctk.CTkButton(self.frame_actions, text="🔍 Brza provjera", command=lambda: self.start_check("fast"), width=130, fg_color="#D97706", hover_color="#B45309")
        self.btn_fast_check.pack(side="left", padx=5)

        self.btn_deep_check = ctk.CTkButton(self.frame_actions, text="🎬 Dubinska provjera videa", command=lambda: self.start_check("deep"), width=180, fg_color="#9333EA", hover_color="#7E22CE")
        self.btn_deep_check.pack(side="left", padx=5)

        ctk.CTkButton(self.frame_actions, text="📋 Kopiraj", command=self.copy_results, width=100).pack(side="left", padx=10)
        ctk.CTkButton(self.frame_actions, text="💾 Spremi (.m3u)", command=self.save_results, width=130).pack(side="left", padx=5)
        ctk.CTkButton(self.frame_actions, text="🗑️ Očisti sve", command=self.clear_all, width=100, fg_color="#C93B3B", hover_color="#932323").pack(side="right")

        # --- 3. FILTERI I OPCIJE ---
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.var_m3u8 = ctk.BooleanVar(value=True)
        self.var_dedupe = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(self.frame_options, text="Uključi .m3u8", variable=self.var_m3u8).pack(side="left", padx=15, pady=10)
        ctk.CTkCheckBox(self.frame_options, text="Makni duplikate", variable=self.var_dedupe).pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(self.frame_options, text="Crna lista:").pack(side="left", padx=(20, 5))
        self.blacklist_entry = ctk.CTkEntry(self.frame_options, width=120, placeholder_text="npr. pastebin")
        self.blacklist_entry.pack(side="left", padx=5)

        ctk.CTkLabel(self.frame_options, text="Bijela lista:").pack(side="left", padx=(15, 5))
        self.whitelist_entry = ctk.CTkEntry(self.frame_options, width=120, placeholder_text="npr. github")
        self.whitelist_entry.pack(side="left", padx=5)

        # --- 4. GLAVNI DIO (Tekst okviri) ---
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(1, weight=1)
        self.frame_main.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_main, text="Ulazni tekst:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkLabel(self.frame_main, text="Rezultati (IPTV liste):", font=("Arial", 14, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))

        self.input_text = ctk.CTkTextbox(self.frame_main, wrap="word", font=("Consolas", 12))
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self.output_text = ctk.CTkTextbox(self.frame_main, wrap="none", font=("Consolas", 12))
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        self.lbl_analytics = ctk.CTkLabel(self.frame_main, text="Analitika servera: Nema podataka", font=("Arial", 12), text_color="gray", justify="left")
        self.lbl_analytics.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(5, 0))

        # --- 5. STATUS BAR & PROGRESS BAR ---
        self.frame_status = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_status.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.frame_status.grid_columnconfigure(0, weight=1)

        self.status = ctk.StringVar(value="Spreman.")
        self.status_label = ctk.CTkLabel(self.frame_status, textvariable=self.status, anchor="w", font=("Arial", 12, "bold"))
        self.status_label.grid(row=0, column=0, sticky="w")

        # Progress bar (Inicijalno skriven)
        self.progress_bar = ctk.CTkProgressBar(self.frame_status, mode="determinate", width=300, progress_color="#2FA572")
        self.progress_bar.grid(row=0, column=1, sticky="e")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove() # Skrivamo ga na početku

    # --- FUNKCIJE ZASLONA ---
    def update_status(self, msg):
        self.status.set(msg)
        self.update_idletasks()

    def update_progress_ui(self, current, total, msg):
        """Sigurno ažuriranje GUI-ja iz pozadinske dretve."""
        self.status.set(msg)
        if total > 0:
            self.progress_bar.set(current / total)
        self.update_idletasks()

    # --- FUNKCIJE EKSTRAKCIJE ---
    def scrape_web(self):
        url = self.web_url_entry.get().strip()
        if not url: return
        if not url.startswith("http"): url = "http://" + url

        self.update_status(f"⏳ Povlačim podatke s {url}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.input_text.delete("0.0", "end")
            self.input_text.insert("0.0", response.text)
            self.update_status(f"✅ Podaci uspješno povučeni!")
        except Exception as e:
            self.update_status("❌ Greška pri preuzimanju.")

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.input_text.delete("0.0", "end")
                self.input_text.insert("0.0", f.read())
            self.update_status(f"📂 Učitana datoteka.")

    def run_extract(self):
        text = self.input_text.get("0.0", "end")
        urls = extract_urls(text)
        playlist_urls = [u for u in urls if looks_like_iptv_playlist(u, self.var_m3u8.get(), True)]

        blacklist = [w.strip().lower() for w in self.blacklist_entry.get().split(",") if w.strip()]
        whitelist = [w.strip().lower() for w in self.whitelist_entry.get().split(",") if w.strip()]

        filtered_urls = [u for u in playlist_urls if not any(b in u.lower() for b in blacklist)]
        if whitelist:
            filtered_urls = [u for u in filtered_urls if any(w in u.lower() for w in whitelist)]

        if self.var_dedupe.get():
            filtered_urls = list(dict.fromkeys(filtered_urls))

        self.extracted_urls = filtered_urls
        self.refresh_output_window()
        self.update_analytics()
        self.update_status(f"✅ Analiza gotova | Prikazano: {len(filtered_urls)}")

    def refresh_output_window(self):
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", "\n".join(self.extracted_urls))

    def update_analytics(self):
        if not self.extracted_urls:
            self.lbl_analytics.configure(text="Analitika servera: Nema podataka")
            return
        domains = [urlparse(u).netloc for u in self.extracted_urls]
        top_domains = Counter(domains).most_common(3)
        self.lbl_analytics.configure(text="🔥 Top 3 servera: " + " | ".join([f"{dom} ({cnt}x)" for dom, cnt in top_domains]))

    # --- PROVJERE LINKOVA ---
    def check_fast(self, url):
        headers = {"User-Agent": "VLC/3.0.18 LibVLC/3.0.18", "Accept": "*/*"}
        try:
            res = requests.get(url, headers=headers, timeout=5, stream=True, allow_redirects=True)
            if res.status_code == 200 and 'text/html' not in res.headers.get('Content-Type', '').lower():
                chunk = res.raw.read(2048).decode('utf-8', errors='ignore').lower()
                if any(tag in chunk for tag in ["#extm3u", "#extinf", ".ts", ".m3u8"]):
                    return url
        except Exception:
            pass
        return None

    def check_deep(self, url):
        headers = {"User-Agent": "VLC/3.0.18 LibVLC/3.0.18", "Accept": "*/*"}
        try:
            res = requests.get(url, headers=headers, timeout=8, stream=True, allow_redirects=True)
            if res.status_code != 200 or 'text/html' in res.headers.get('Content-Type', '').lower():
                return None

            content = res.raw.read(15360).decode('utf-8', errors='ignore')
            stream_url = None

            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and line.startswith('http'):
                    stream_url = line
                    break

            if not stream_url:
                return None

            stream_res = requests.get(stream_url, headers=headers, timeout=5, stream=True)
            if stream_res.status_code == 200:
                video_chunk = stream_res.raw.read(1024)
                if len(video_chunk) > 0:
                    return url

        except Exception:
            pass
        return None

    def start_check(self, mode="fast"):
        if not self.extracted_urls:
            messagebox.showinfo("Info", "Prvo izvuci linkove!")
            return

        self.btn_fast_check.configure(state="disabled")
        self.btn_deep_check.configure(state="disabled")

        # Pokaži i resetiraj Progress Bar
        self.progress_bar.grid()
        self.progress_bar.set(0)

        threading.Thread(target=self._live_check_thread, args=(mode,), daemon=True).start()

    def _live_check_thread(self, mode):
        working_urls = []
        total = len(self.extracted_urls)

        workers = 20 if mode == "fast" else 8
        check_func = self.check_fast if mode == "fast" else self.check_deep

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(check_func, url): url for url in self.extracted_urls}
            checked = 0
            for future in concurrent.futures.as_completed(futures):
                checked += 1
                result = future.result()
                if result: working_urls.append(result)

                status_text = f"🔍 Brza provjera" if mode == "fast" else "🎬 Dubinska provjera"
                msg = f"{status_text}: {checked}/{total} | Rade: {len(working_urls)}"

                # Prebacujemo ažuriranje ekrana na glavnu dretvu kako program ne bi smrznuo
                self.after(0, self.update_progress_ui, checked, total, msg)

        self.extracted_urls = working_urls
        self.after(0, self.finish_check)

    def finish_check(self):
        self.refresh_output_window()
        self.update_analytics()
        self.btn_fast_check.configure(state="normal")
        self.btn_deep_check.configure(state="normal")

        # Sakrij Progress bar kada je gotovo
        self.progress_bar.grid_remove()
        self.update_status(f"✅ Provjera završena! Ispravnih listi: {len(self.extracted_urls)}")

    def save_results(self):
        if not self.extracted_urls: return
        path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U Playlist", "*.m3u"), ("Text file", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    if path.endswith(".m3u"):
                        f.write("#EXTM3U\n")
                        for i, url in enumerate(self.extracted_urls):
                            f.write(f"#EXTINF:-1, Lista {i+1} (Pro Extractor)\n{url}\n")
                    else:
                        f.write("\n".join(self.extracted_urls))
                self.update_status(f"💾 Spremljeno!")
            except Exception as e:
                messagebox.showerror("Greška", f"Ne mogu spremiti datoteku:\n{e}")

    def copy_results(self):
        data = self.output_text.get("0.0", "end").strip()
        if data:
            self.clipboard_clear()
            self.clipboard_append(data)
            self.update_status("📋 Rezultati kopirani.")

    def clear_all(self):
        self.input_text.delete("0.0", "end")
        self.output_text.delete("0.0", "end")
        self.extracted_urls = []
        self.update_status("🗑️ Očišćeno.")

if __name__ == "__main__":
    app = IptvExtractorApp()
    app.mainloop()
