import tkinter as tk
from tkinter import messagebox, colorchooser
import tkinter.font as tkfont
from input_module import upload_text_file, export_text_file
from preprocessing import preprocess_text
from customization import apply_custom_style, load_settings, save_settings
from tts_module import TextToSpeech

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personalized Reading Aid for Dyslexics")
        self.root.geometry("1350x770")
        self.root.configure(bg="#f7ede2")
        self.root.minsize(1100, 600)
        self.settings = load_settings()
        self.fonts = ["OpenDyslexic", "Arial", "Sans-serif"]
        try:
            tkfont.Font(family="OpenDyslexic")
        except:
            self.fonts = ["Arial", "Sans-serif"]
            self.settings["font_family"] = "Arial"

        self.tts = TextToSpeech()
        self.tts.set_callback(self._on_tts_highlight)
        self.tts.set_highlight_mode(self.settings.get("highlight_mode", "word"))

        self._build_gui()
        self._refresh_custom_style()
        self._clear_highlight()

    def _build_gui(self):
        # Title bar
        title = tk.Label(
            self.root,
            text="Personalized Reading Aid for Dyslexics",
            font=("Arial", 23, "bold"),
            pady=10,
            bg="#f6e3c5",
            fg="#47342c"
        )
        title.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Main body: Left text area, Right sidebar container (horizontal for both sidebars)
        container = tk.Frame(self.root, bg="#fae2b5")
        container.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=6)
        self.root.grid_columnconfigure(1, weight=4)

        # LEFT: Input & Output (make both height=5)
        text_area = tk.Frame(container, bg="#fff7ef", bd=1, relief="flat")
        text_area.grid(row=0, column=0, padx=(24, 12), pady=16, sticky="nsew")
        text_area.grid_rowconfigure(1, weight=1)
        text_area.grid_rowconfigure(4, weight=1)
        text_area.grid_rowconfigure(5, weight=0)
        text_area.grid_columnconfigure(0, weight=1)

        # Input label
        input_label = tk.Label(
            text_area, text="Input Text", font=("Arial", 10, "bold"),
            bg="#fff7ef", fg="#684f46"
        )
        input_label.grid(row=0, column=0, sticky="ew", pady=(2, 0), padx=8, columnspan=2)
        self.input_box = tk.Text(text_area, height=5, width=56, wrap="word", font=("Arial", 12))
        self.input_sb = tk.Scrollbar(text_area, command=self.input_box.yview)
        self.input_box.config(yscrollcommand=self.input_sb.set)
        self.input_box.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(2, 2))
        self.input_sb.grid(row=1, column=1, sticky="ns", padx=(0, 8), pady=(2, 2))

        btns_frame = tk.Frame(text_area, bg="#fff7ef")
        btns_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))
        tk.Button(btns_frame, text="Paste", command=self._paste_text, bg="#eed7aa",
                  font=("Arial", 10, "bold"), width=12).pack(side="left", padx=(0, 5))
        tk.Button(btns_frame, text="Upload File", command=self.upload_file, bg="#eed7aa",
                  font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)
        tk.Button(btns_frame, text="Preprocess", command=self.preprocess_text, bg="#eed7aa",
                  font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)

        output_label = tk.Label(
            text_area, text="Processed & Adapted Text", font=("Arial", 10, "bold"),
            bg="#fff7ef", fg="#684f46"
        )
        output_label.grid(row=3, column=0, sticky="ew", pady=(4, 0), padx=8, columnspan=2)
        self.output_box = tk.Text(text_area, height=5, width=56, wrap="word")
        self.output_sb = tk.Scrollbar(text_area, command=self.output_box.yview)
        self.output_box.config(yscrollcommand=self.output_sb.set)
        self.output_box.grid(row=4, column=0, sticky="nsew", padx=(8, 0), pady=(2, 4))
        self.output_sb.grid(row=4, column=1, sticky="ns", padx=(0, 8), pady=(2, 4))

        out_btns = tk.Frame(text_area, bg="#fff7ef")
        out_btns.grid(row=5, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 4))
        tk.Button(out_btns, text="Export Text", command=self.export_text, bg="#eed7aa",
                  font=("Arial", 10, "bold"), width=16).pack(side="left", padx=(0, 7))
        tk.Button(out_btns, text="Clear", command=self.clear_text, bg="#eed7aa",
                  font=("Arial", 10, "bold"), width=12).pack(side="left", padx=7)

        # RIGHT: Sidebars horizontally next to each other
        sidebar_container = tk.Frame(container, bg="#fae2b5")
        sidebar_container.grid(row=0, column=1, padx=(0, 0), pady=16, sticky="nsew")
        sidebar_container.grid_rowconfigure(0, weight=1)
        sidebar_container.grid_columnconfigure(0, weight=1)
        sidebar_container.grid_columnconfigure(1, weight=1)

        # Customization Sidebar (unchanged)
        custom_frame = tk.Frame(sidebar_container, bg="#f7ddb3", bd=2, relief="ridge", height=680, width=270)
        custom_frame.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=(0,0))
        custom_frame.grid_propagate(False)
        custom_frame.grid_columnconfigure(0, weight=1)
        custom_frame.grid_columnconfigure(1, weight=1)
        tk.Label(custom_frame, text="Customization", bg="#f7ddb3", font=("Arial", 15, "bold"), fg="#7d482e").grid(row=0, column=0, columnspan=2, pady=(10,2))
        tk.Label(custom_frame, text="Font:", bg="#f7ddb3").grid(row=1, column=0, sticky="w", padx=11)
        self.font_var = tk.StringVar(value=self.settings["font_family"])
        font_menu = tk.OptionMenu(custom_frame, self.font_var, *self.fonts, command=lambda evt: self._refresh_custom_style())
        font_menu.config(width=14, font=("Arial", 10))
        font_menu.grid(row=1, column=1, sticky="ew", padx=(0,9), pady=2)
        tk.Label(custom_frame, text="Font Size:", bg="#f7ddb3").grid(row=2, column=0, sticky="w", padx=11)
        self.size_var = tk.IntVar(value=self.settings["font_size"])
        tk.Scale(custom_frame, variable=self.size_var, from_=12, to=32, orient="horizontal", showvalue=True, bg="#f7ddb3",
                 command=lambda evt: self._refresh_custom_style(), length=140).grid(row=2, column=1, sticky="w", padx=(0,9), pady=(2,0))
        tk.Label(custom_frame, text="Word Spacing:", bg="#f7ddb3").grid(row=3, column=0, sticky="w", padx=11)
        self.ws_var = tk.IntVar(value=self.settings.get("word_spacing", 1))
        tk.Scale(custom_frame, variable=self.ws_var, from_=0, to=8, orient="horizontal", showvalue=True, bg="#f7ddb3",
                 command=lambda evt: self._refresh_custom_style(), length=140).grid(row=3, column=1, sticky="w", padx=(0,9))
        tk.Label(custom_frame, text="Letter Spacing:", bg="#f7ddb3").grid(row=4, column=0, sticky="w", padx=11)
        self.ls_var = tk.IntVar(value=self.settings.get("letter_spacing", 0))
        tk.Scale(custom_frame, variable=self.ls_var, from_=0, to=4, orient="horizontal", showvalue=True, bg="#f7ddb3",
                 command=lambda evt: self._refresh_custom_style(), length=140).grid(row=4, column=1, sticky="w", padx=(0,9))
        tk.Button(custom_frame, text="Background", command=self._choose_bg_color, bg="#ffefcb", width=16).grid(row=5, column=0, pady=(14,1), padx=11)
        tk.Button(custom_frame, text="Text Color", command=self._choose_fg_color, bg="#ffefcb", width=16).grid(row=5, column=1, pady=(14,1), padx=1)
        tk.Button(custom_frame, text="Highlight Color", command=self._choose_hl_color, bg="#ffefcb", width=16).grid(row=6, column=0, pady=(7,0), padx=11)
        tk.Label(custom_frame, text="Highlight Mode:", bg="#f7ddb3").grid(row=7, column=0, sticky="w", padx=11, pady=(13,0), columnspan=2)
        self.highlight_var = tk.StringVar(value=self.settings.get("highlight_mode", "word"))
        tk.Radiobutton(custom_frame, text="Word", variable=self.highlight_var, value="word", bg="#f7ddb3", command=self._refresh_highlight_mode).grid(row=8, column=0, sticky="w", padx=(19,0))
        tk.Radiobutton(custom_frame, text="Line", variable=self.highlight_var, value="line", bg="#f7ddb3", command=self._refresh_highlight_mode).grid(row=8, column=1, sticky="w", padx=(2,0))
        tk.Button(custom_frame, text="Save Prefs", command=self.save_settings,
                  bg="#f7ca97", font=("Arial", 10, "bold"), width=16).grid(row=9, column=0, pady=(16,2), padx=11)
        tk.Button(custom_frame, text="About", command=self.show_about_popup,
                  bg="#f7ca97", font=("Arial", 10, "bold"), width=16).grid(row=9, column=1, pady=(16,2), padx=1)

        # TTS Controls Sidebar (right of right pane)
        tts_frame = tk.Frame(sidebar_container, bg="#f5dab0", bd=2, relief="ridge", height=680, width=240)
        tts_frame.grid(row=0, column=1, sticky="nsew", padx=(0,0), pady=(0,0))
        tts_frame.grid_propagate(False)
        tts_frame.grid_columnconfigure(0, weight=1)
        tts_frame.grid_columnconfigure(1, weight=1)
        tk.Label(tts_frame, text="TTS Controls", bg="#f5dab0", font=("Arial", 15, "bold"), fg="#995c00")\
            .grid(row=0, column=0, columnspan=2, pady=(12,7))
        tk.Button(tts_frame, text="Play", command=self.play_tts, width=12, bg="#dec09c", font=("Arial", 11)).grid(row=1, column=0, padx=(18,5), pady=(7,5))
        tk.Button(tts_frame, text="Pause", command=self.pause_tts, width=12, bg="#dec09c", font=("Arial", 11)).grid(row=1, column=1, padx=(5,18), pady=(7,5))
        tk.Button(tts_frame, text="Resume", command=self.resume_tts, width=12, bg="#dec09c", font=("Arial", 11)).grid(row=2, column=0, padx=(18,5), pady=4)
        tk.Button(tts_frame, text="Stop", command=self.stop_tts, width=12, bg="#dec09c", font=("Arial", 11)).grid(row=2, column=1, padx=(5,18), pady=4)
        tk.Label(tts_frame, text="Reading Speed:", bg="#f5dab0").grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(26,2))
        self.speed_var = tk.IntVar(value=170)
        tk.Scale(tts_frame, variable=self.speed_var, from_=120, to=250, orient="horizontal",
                 showvalue=True, bg="#f5dab0", command=lambda e:self._refresh_speed(), length=180).grid(row=4, column=0, columnspan=2, padx=18, pady=(0,10))

    def _paste_text(self):
        try:
            text = self.root.clipboard_get()
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, text)
        except Exception:
            messagebox.showerror("Error", "No text in clipboard.")

    def upload_file(self):
        text = upload_text_file(self.input_box)
        if text:
            messagebox.showinfo("Upload", "File loaded successfully.")

    def export_text(self):
        export_text_file(self.output_box)

    def preprocess_text(self):
        raw = self.input_box.get("1.0", tk.END)
        if not raw.strip():
            messagebox.showwarning("Warning", "Please enter or upload text first.")
            return
        processed = preprocess_text(raw)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, processed)
        self._clear_highlight()

    def clear_text(self):
        self.input_box.delete("1.0", tk.END)
        self.output_box.delete("1.0", tk.END)
        self._clear_highlight()

    def _refresh_custom_style(self, live=True):
        self.settings["font_family"] = self.font_var.get()
        self.settings["font_size"] = self.size_var.get()
        self.settings["word_spacing"] = self.ws_var.get()
        self.settings["letter_spacing"] = self.ls_var.get()
        apply_custom_style(self.output_box, self.settings, live=live)
        self._clear_highlight()

    def _choose_bg_color(self):
        color = colorchooser.askcolor(title="Background Color")[1]
        if color:
            self.settings["bg_color"] = color
            apply_custom_style(self.output_box, self.settings)
            self._clear_highlight()

    def _choose_fg_color(self):
        color = colorchooser.askcolor(title="Text Color")[1]
        if color:
            self.settings["fg_color"] = color
            apply_custom_style(self.output_box, self.settings)
            self._clear_highlight()

    def _choose_hl_color(self):
        color = colorchooser.askcolor(title="Highlight Color")[1]
        if color:
            self.settings["highlight_color"] = color

    def save_settings(self):
        self.settings["highlight_mode"] = self.highlight_var.get()
        save_settings(self.settings)
        messagebox.showinfo("Saved", "Preferences saved successfully.")

    def show_about_popup(self):
        messagebox.showinfo(
            "About", (
                "Personalized Reading Aid for Dyslexics\n\n"
                "Paste or upload text, customize font/spacing/colors, and listen with TTS.\n\n"
                "Credits: Team DyslexiaAid"
            )
        )

    def _refresh_highlight_mode(self):
        mode = self.highlight_var.get()
        self.settings["highlight_mode"] = mode
        self.tts.set_highlight_mode(mode)
        self._clear_highlight()

    def _clear_highlight(self):
        for tag in ("highlight", "highlight_line"):
            self.output_box.tag_remove(tag, "1.0", tk.END)

    def _refresh_speed(self):
        self.tts.set_rate(self.speed_var.get())

    def _on_tts_highlight(self, word_idx, word, line_idx):
        self.output_box.tag_remove("highlight", "1.0", tk.END)
        self.output_box.tag_remove("highlight_line", "1.0", tk.END)
        text = self.output_box.get("1.0", tk.END)
        if self.settings["highlight_mode"] == "word" and word is not None:
            idx = 0
            curr = 0
            word_list = text.split()
            for i, w in enumerate(word_list):
                if i == word_idx:
                    break
                curr += len(w)+1
            start = f"1.0 + {curr}c"
            end = f"{start} + {len(word)}c"
            self.output_box.tag_add("highlight", start, end)
            self.output_box.tag_configure("highlight", background=self.settings.get("highlight_color", "#ffe599"))
        elif self.settings["highlight_mode"] == "line" and line_idx is not None:
            lines = text.split('\n')
            curr = 0
            for i, ln in enumerate(lines):
                if i == line_idx:
                    break
                curr += len(ln)+1
            start = f"1.0 + {curr}c"
            end = f"{start} + {len(lines[line_idx])}c"
            self.output_box.tag_add("highlight_line", start, end)
            self.output_box.tag_configure("highlight_line", background=self.settings.get("highlight_color", "#ffe599"))

    def play_tts(self):
        text = self.output_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to read.")
            return
        self._clear_highlight()
        self.tts.set_highlight_mode(self.highlight_var.get())
        self.tts.set_rate(self.speed_var.get())
        self.tts.speak(text)

    def pause_tts(self):
        self.tts.pause()
        self._clear_highlight()

    def resume_tts(self):
        self.tts.resume()

    def stop_tts(self):
        self.tts.stop()
        self._clear_highlight()

if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
