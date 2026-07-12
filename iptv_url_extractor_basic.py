import tkinter as tk
from tkinter import filedialog, messagebox
import re
from urllib.parse import urlparse, parse_qs, unquote

# Extracts URLs and filters those that look like IPTV playlist links (.m3u/.m3u8)
URL_REGEX = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>\"\]\)]+)")


def normalize_url(u: str) -> str:
    u = u.strip().rstrip('.,;:!?)"]}')
    if u.lower().startswith("www."):
        u = "http://" + u
    return u


def looks_like_iptv_playlist(url: str, allow_m3u8: bool = True, allow_query_m3u: bool = True) -> bool:
    """Heuristics:
    - URL path ends with .m3u (and optionally .m3u8)
    - OR query contains keys/values mentioning m3u/m3u8 (optional)
    """
    try:
        parsed = urlparse(url)
        path = (parsed.path or "").lower()

        if path.endswith(".m3u"):
            return True
        if allow_m3u8 and path.endswith(".m3u8"):
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
    urls = []
    for m in URL_REGEX.finditer(text):
        urls.append(normalize_url(m.group(1)))
    return urls


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("URL Extractor (IPTV playlists: .m3u/.m3u8)")
        self.geometry("1000x650")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        tk.Button(top, text="Otvori datoteku…", command=self.open_file).pack(side="left")
        tk.Button(top, text="Izvuci URL-ove", command=self.run_extract).pack(side="left", padx=8)
        tk.Button(top, text="Kopiraj rezultate", command=self.copy_results).pack(side="left")
        tk.Button(top, text="Spremi rezultate…", command=self.save_results).pack(side="left", padx=8)
        tk.Button(top, text="Ocisti", command=self.clear_all).pack(side="right")

        opts = tk.Frame(self)
        opts.pack(fill="x", padx=10, pady=(0, 8))

        self.var_m3u8 = tk.BooleanVar(value=True)
        self.var_query = tk.BooleanVar(value=True)
        self.var_dedupe = tk.BooleanVar(value=True)
        self.var_sort_host = tk.BooleanVar(value=False)

        tk.Checkbutton(opts, text="Uključi .m3u8", variable=self.var_m3u8).pack(side="left")
        tk.Checkbutton(opts, text="Prepoznaj m3u u query param.", variable=self.var_query).pack(side="left", padx=10)
        tk.Checkbutton(opts, text="Makni duplikate", variable=self.var_dedupe).pack(side="left", padx=10)
        tk.Checkbutton(opts, text="Sortiraj po serveru (host)", variable=self.var_sort_host).pack(side="left", padx=10)

        panes = tk.PanedWindow(self, orient="horizontal", sashrelief="raised")
        panes.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = tk.Frame(panes)
        right_frame = tk.Frame(panes)

        panes.add(left_frame, stretch="always")
        panes.add(right_frame, stretch="always")

        tk.Label(left_frame, text="Ulaz (zalijepi tekst ili otvori datoteku):").pack(anchor="w")
        self.input_text = tk.Text(left_frame, wrap="word")
        self.input_text.pack(fill="both", expand=True, pady=(5, 0))

        tk.Label(right_frame, text="Rezultati (IPTV playlist URL-ovi):").pack(anchor="w")
        self.output_text = tk.Text(right_frame, wrap="none")
        self.output_text.pack(fill="both", expand=True, pady=(5, 0))

        self.status = tk.StringVar(value="Spreman.")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0, 8))

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Odaberi datoteku",
            filetypes=[
                ("Text files", "*.txt *.log *.csv *.json *.m3u *.m3u8"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", data)
            self.status.set(f"Ucitan fajl: {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu otvoriti datoteku:\n{e}")

    def run_extract(self):
        text = self.input_text.get("1.0", "end")
        urls = extract_urls(text)

        allow_m3u8 = self.var_m3u8.get()
        allow_query = self.var_query.get()

        playlist_urls = [u for u in urls if looks_like_iptv_playlist(u, allow_m3u8, allow_query)]

        if self.var_sort_host.get():
            playlist_urls.sort(key=lambda u: (urlparse(u).hostname or "").lower())

        if self.var_dedupe.get():
            seen = set()
            deduped = []
            for u in playlist_urls:
                if u not in seen:
                    seen.add(u)
                    deduped.append(u)
            playlist_urls = deduped

        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", "\n".join(playlist_urls))

        self.status.set(f"Nađeno URL-ova: {len(urls)} | IPTV lista URL-ova: {len(playlist_urls)}")

    def copy_results(self):
        data = self.output_text.get("1.0", "end").strip()
        if not data:
            messagebox.showinfo("Info", "Nema rezultata za kopiranje.")
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        self.status.set("Rezultati kopirani u clipboard.")

    def save_results(self):
        data = self.output_text.get("1.0", "end").strip()
        if not data:
            messagebox.showinfo("Info", "Nema rezultata za spremanje.")
            return
        path = filedialog.asksaveasfilename(
            title="Spremi rezultate",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data + "\n")
            self.status.set(f"Spremljeno: {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu spremiti datoteku:\n{e}")

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.status.set("Očišćeno.")


if __name__ == "__main__":
    App().mainloop()
