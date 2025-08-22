import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import time
from archive_utils import ArchiveUtils
from themes.dark_theme import THEME, FONTS
import threading
from PIL import Image, ImageTk
import sys

class ZipUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZipUnlocker v3")
        self.geometry("700x550")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        
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
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20, troughcolor=THEME["secondary"], background=THEME["progress"])
        self.style.configure("TButton", background=THEME["button"], foreground=THEME["fg"])
        self.style.map("TButton", background=[("active", THEME["button_hover"])])
        
        title_frame = tk.Frame(self, bg=THEME["bg"])
        title_frame.pack(pady=10, fill="x")
        
        title_label = tk.Label(
            title_frame,
            text="ZipUnlocker v3",
            font=FONTS["title"],
            fg=THEME["accent"],
            bg=THEME["bg"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Final Release",
            font=FONTS["subtitle"],
            fg=THEME["text_highlight"],
            bg=THEME["bg"]
        )
        subtitle_label.pack()
        
        content_frame = tk.Frame(self, bg=THEME["secondary"], padx=15, pady=15)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.select_button = ttk.Button(
            content_frame,
            text="Выбрать архив для разблокировки",
            command=self.select_file
        )
        self.select_button.pack(pady=10)
        
        self.file_info = tk.Label(
            content_frame,
            text="Файл не выбран",
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["secondary"],
            wraplength=500
        )
        self.file_info.pack(pady=5)
        
        self.status = tk.Label(
            content_frame,
            text="Ожидание файла...",
            bg=THEME["secondary"],
            fg=THEME["text_highlight"],
            font=FONTS["normal"]
        )
        self.status.pack(pady=5)
        
        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.progress.pack(pady=10, fill="x")
        
        log_frame = tk.Frame(content_frame, bg=THEME["secondary"])
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        log_label = tk.Label(
            log_frame,
            text="Журнал операций:",
            font=FONTS["subtitle"],
            fg=THEME["fg"],
            bg=THEME["secondary"]
        )
        log_label.pack(anchor="w")
        
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
        
        stats_frame = tk.Frame(content_frame, bg=THEME["secondary"])
        stats_frame.pack(fill="x", pady=(10, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Обработано архивов: 0 | Успешно: 0 | С ошибками: 0",
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["secondary"]
        )
        self.stats_label.pack(side="left")
        
        copyright_label = tk.Label(
            self,
            text="© 2025 Platon U. All rights reserved.",
            font=FONTS["small"],
            fg=THEME["fg"],
            bg=THEME["bg"]
        )
        copyright_label.pack(side="bottom", pady=5)
        
        self.utils = ArchiveUtils()
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        self.log_message("ZipUnlocker v3 инициализирован и готов к работе")
        self.log_message(f"Поддерживаемых форматов: {len(self.utils.supported_formats)}")
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_stats(self):
        self.stats_label.config(
            text=f"Обработано архивов: {self.processed_count} | Успешно: {self.success_count} | С ошибками: {self.error_count}"
        )
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите архив для разблокировки",
            filetypes=[("Все поддерживаемые архивы", 
                       "*.zip *.rar *.7z *.tar *.gz *.tgz *.bz2 *.tbz2 *.xz *.txz "
                       "*.z *.lz *.lzma *.lzo *.rz *.sz *.ace *.arj *.cab *.cpio "
                       "*.deb *.dmg *.iso *.lha *.lzh *.msi *.rpm *.udf *.wim *.xar *.zst")]
        )
        if not file_path:
            return
        
        file_type = self.utils.get_file_type(file_path)
        if not file_type:
            messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
            return
        
        base_name, ext = os.path.splitext(file_path)
        if file_type in ('.tgz', '.tbz2', '.txz'):
            base_name = base_name.replace(ext, '')
            output_path = f"{base_name}_unlocked{file_type}"
        else:
            output_path = f"{base_name}_unlocked{file_type}"
        
        self.file_info.config(text=f"Выбран файл: {os.path.basename(file_path)}")
        self.log_message(f"Начата обработка: {os.path.basename(file_path)}")
        self.log_message(f"Тип архива: {self.utils.supported_formats[file_type]}")
        self.status.config(text="Обработка...")
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
            self.update_status("Готово!")
            self.log_message(f"Файл успешно обработан: {os.path.basename(output_path)}")
            self.success_count += 1
            messagebox.showinfo("Успех", "Пароль успешно снят!")
        else:
            self.update_status("Ошибка!")
            self.log_message(f"Ошибка обработки: {result}")
            self.error_count += 1
            messagebox.showerror("Ошибка", f"Ошибка обработки: {result}")
        
        self.progress['value'] = 0
        self.select_button.config(state=tk.NORMAL)
        self.update_stats()

if __name__ == "__main__":
    app = ZipUnlockerApp()
    app.mainloop()