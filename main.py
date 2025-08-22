import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import time
from archive_utils import ArchiveUtils
from themes.dark_theme import THEME, FONTS
import threading
from PIL import Image, ImageTk
import sys
from localization import LANGUAGES, get_system_language

class ZipUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Устанавливаем язык по умолчанию
        self.current_language = get_system_language()
        self.lang = LANGUAGES[self.current_language]
        
        self.title(self.lang["title"])
        self.geometry("700x550")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        
        # Иконка приложения
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "assets", "icon.png")
            if os.path.exists(icon_path):
                self.iconphoto(True, tk.PhotoImage(file=icon_path))
        except:
            pass
        
        # Стили
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20, troughcolor=THEME["secondary"], background=THEME["progress"])
        self.style.configure("TButton", background=THEME["button"], foreground=THEME["fg"])
        self.style.map("TButton", background=[("active", THEME["button_hover"])])
        
        # Заголовок
        title_frame = tk.Frame(self, bg=THEME["bg"])
        title_frame.pack(pady=10, fill="x")
        
        self.title_label = tk.Label(
            title_frame,
            text=self.lang["title"],
            font=FONTS["title"],
            fg=THEME["accent"],
            bg=THEME["bg"]
        )
        self.title_label.pack()
        
        self.subtitle_label = tk.Label(
            title_frame,
            text=self.lang["final_release"],
            font=FONTS["subtitle"],
            fg=THEME["text_highlight"],
            bg=THEME["bg"]
        )
        self.subtitle_label.pack()
        
        # Выбор языка
        lang_frame = tk.Frame(title_frame, bg=THEME["bg"])
        lang_frame.pack(pady=5)
        
        tk.Label(
            lang_frame,
            text=self.lang["choose_language"],
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["bg"]
        ).pack(side=tk.LEFT)
        
        self.lang_var = tk.StringVar(value=self.current_language)
        lang_combo = ttk.Combobox(
            lang_frame, 
            textvariable=self.lang_var,
            values=list(LANGUAGES.keys()),
            state="readonly",
            width=5
        )
        lang_combo.pack(side=tk.LEFT, padx=5)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Основной контент
        content_frame = tk.Frame(self, bg=THEME["secondary"], padx=15, pady=15)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Кнопка выбора файла
        self.select_button = ttk.Button(
            content_frame,
            text=self.lang["select_archive"],
            command=self.select_file
        )
        self.select_button.pack(pady=10)
        
        # Информация о выбранном файле
        self.file_info = tk.Label(
            content_frame,
            text=self.lang["no_file_selected"],
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["secondary"],
            wraplength=500
        )
        self.file_info.pack(pady=5)
        
        # Статус
        self.status = tk.Label(
            content_frame,
            text=self.lang["waiting"],
            bg=THEME["secondary"],
            fg=THEME["text_highlight"],
            font=FONTS["normal"]
        )
        self.status.pack(pady=5)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.progress.pack(pady=10, fill="x")
        
        # Лог
        log_frame = tk.Frame(content_frame, bg=THEME["secondary"])
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.log_label = tk.Label(
            log_frame,
            text="Журнал операций:",
            font=FONTS["subtitle"],
            fg=THEME["fg"],
            bg=THEME["secondary"]
        )
        self.log_label.pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            bg=THEME["bg"],
            fg=THEME["fg"],
            font=("Consolas", 9),
            relief="flat",
            borderwidth=1
        )
        self.log_text.pack(fill="both", expand=True, pady=(5, 0))
        self.log_text.config(state=tk.DISABLED)
        
        # Статистика
        stats_frame = tk.Frame(content_frame, bg=THEME["secondary"])
        stats_frame.pack(fill="x", pady=(10, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text=self.lang["stats"].format(0, 0, 0),
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["secondary"]
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Копирайт
        self.copyright_label = tk.Label(
            self,
            text=self.lang["copyright"],
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["bg"]
        )
        self.copyright_label.pack(side="bottom", pady=5)
        
        self.utils = ArchiveUtils()
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        self.log_message(self.lang["log_init"])
        self.log_message(self.lang["log_formats"].format(len(self.utils.supported_formats)))
    
    def change_language(self, event):
        new_lang = self.lang_var.get()
        if new_lang in LANGUAGES:
            self.current_language = new_lang
            self.lang = LANGUAGES[self.current_language]
            self.update_ui_text()
    
    def update_ui_text(self):
        """Обновляем все тексты в интерфейсе при смене языка"""
        self.title(self.lang["title"])
        self.title_label.config(text=self.lang["title"])
        self.subtitle_label.config(text=self.lang["final_release"])
        self.select_button.config(text=self.lang["select_archive"])
        self.file_info.config(text=self.lang["no_file_selected"])
        self.status.config(text=self.lang["waiting"])
        self.log_label.config(text="Журнал операций:")
        self.stats_label.config(text=self.lang["stats"].format(
            self.processed_count, self.success_count, self.error_count
        ))
        self.copyright_label.config(text=self.lang["copyright"])
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_stats(self):
        self.stats_label.config(
            text=self.lang["stats"].format(self.processed_count, self.success_count, self.error_count)
        )
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title=self.lang["select_archive"],
            filetypes=[(self.lang["select_archive"], 
                       "*.zip *.rar *.7z *.tar *.gz *.tgz *.bz2 *.tbz2 *.xz *.txz "
                       "*.z *.lz *.lzma *.lzo *.rz *.sz *.ace *.arj *.cab *.cpio "
                       "*.deb *.dmg *.iso *.lha *.lzh *.msi *.rpm *.udf *.wim *.xar *.zst")]
        )
        if not file_path:
            return
        
        file_type = self.utils.get_file_type(file_path)
        if not file_type:
            messagebox.showerror(self.lang["error"], self.lang["unsupported_format"])
            return
        
        # Формирование выходного пути
        base_name, ext = os.path.splitext(file_path)
        if file_type in ('.tgz', '.tbz2', '.txz'):
            # Для составных расширений
            base_name = base_name.replace(ext, '')
            output_path = f"{base_name}_unlocked{file_type}"
        else:
            output_path = f"{base_name}_unlocked{file_type}"
        
        self.file_info.config(text=f"{self.lang['select_archive']}: {os.path.basename(file_path)}")
        self.log_message(self.lang["log_start"].format(os.path.basename(file_path)))
        self.log_message(self.lang["log_archive_type"].format(self.utils.supported_formats[file_type]))
        self.status.config(text=self.lang["processing"])
        self.select_button.config(state=tk.DISABLED)
        
        self.processed_count += 1
        self.update_stats()
        
        thread = threading.Thread(
            target=self.process_archive,
            args=(file_path, output_path),
            daemon=True
        )
        thread.start()
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.update_idletasks()
    
    def update_status(self, message):
        self.status.config(text=message)
        self.log_message(message)
        self.update_idletasks()
    
    def process_archive(self, input_path, output_path):
        def progress_callback(value):
            self.after(10, lambda: self.update_progress(value))
        
        def status_callback(message):
            self.after(10, lambda: self.update_status(message))
        
        result = self.utils.remove_password(input_path, output_path, progress_callback, status_callback)
        
        if result is True:
            self.update_status(self.lang["done"])
            self.log_message(self.lang["log_success"].format(os.path.basename(output_path)))
            self.success_count += 1
            messagebox.showinfo(self.lang["success_message"], self.lang["success_message"])
        else:
            self.update_status(self.lang["error"])
            self.log_message(self.lang["log_error"].format(result))
            self.error_count += 1
            messagebox.showerror(self.lang["error"], f"{self.lang['error']}: {result}")
        
        self.progress['value'] = 0
        self.select_button.config(state=tk.NORMAL)
        self.update_stats()

if __name__ == "__main__":
    app = ZipUnlockerApp()
    app.mainloop()