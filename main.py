import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
from archive_utils import ArchiveUtils
import threading
import time

class ZipUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZipUnlocker v2")
        self.geometry("600x500")
        self.configure(bg="#2b2b2b")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20, troughcolor='#3c3f41', background='#4caf50')
        
        # Заголовок
        title_frame = tk.Frame(self, bg="#2b2b2b")
        title_frame.pack(pady=10, fill="x")
        
        title_label = tk.Label(
            title_frame,
            text="ZipUnlocker v2",
            font=("Arial", 20, "bold"),
            fg="#4caf50",
            bg="#2b2b2b"
        )
        title_label.pack()
        
        version_label = tk.Label(
            title_frame,
            text="Release",
            font=("Arial", 10),
            fg="#ff6b6b",
            bg="#2b2b2b"
        )
        version_label.pack()
        
        github_link = tk.Label(
            self,
            text="GitHub Repository",
            font=("Arial", 10, "underline"),
            fg="#64b5f6",
            cursor="hand2",
            bg="#2b2b2b"
        )
        github_link.pack(pady=5)
        github_link.bind("<Button-1>", lambda e: self.open_github())
        
  
        content_frame = tk.Frame(self, bg="#3c3f41", padx=10, pady=10)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)
        

        self.select_button = tk.Button(
            content_frame,
            text="Выбрать архив",
            font=("Arial", 12),
            bg="#4caf50",
            fg="white",
            relief="flat",
            command=self.select_file
        )
        self.select_button.pack(pady=10)
        
        # Информация о форматах
        formats_label = tk.Label(
            content_frame,
            text="Поддерживаемые форматы: .ZIP .RAR .7Z .TAR.GZ .TAR.BZ2 .TAR.XZ",
            font=("Arial", 10),
            fg="#bdbdbd",
            bg="#3c3f41"
        )
        formats_label.pack(pady=5)
        
        # Статус
        self.status = tk.Label(
            content_frame,
            text="Ожидание файла...",
            bg="#3c3f41",
            fg="#64b5f6",
            font=("Arial", 10)
        )
        self.status.pack(pady=5)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(pady=10, fill="x")
        
        # Лог
        log_label = tk.Label(
            content_frame,
            text="Лог операций:",
            font=("Arial", 10, "bold"),
            fg="#bdbdbd",
            bg="#3c3f41"
        )
        log_label.pack(anchor="w", pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            content_frame,
            height=8,
            bg="#2b2b2b",
            fg="#e0e0e0",
            font=("Consolas", 9)
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Предупреждение
        warning = tk.Label(
            self,
            text="Pre-Release: Возможны ошибки!",
            fg="#ff6b6b",
            bg="#2b2b2b",
            font=("Arial", 9, "italic")
        )
        warning.pack(side="bottom", pady=5)
        
        self.utils = ArchiveUtils()
    
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/windusik/ZipUnlocker")
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите архив",
            filetypes=[
                ("Архивы", "*.zip *.rar *.7z *.tar.gz *.tgz *.tar.bz2 *.tbz2 *.tar.xz *.txz"),
                ("Все файлы", "*.*")
            ]
        )
        if not file_path:
            return
        
        # Формирование выходного пути
        filename = file_path.lower()
        if filename.endswith(".tar.gz"):
            base_name = filename.replace(".tar.gz", "")
            output_path = f"{base_name}_unlocked.tar.gz"
        elif filename.endswith(".tgz"):
            base_name = filename.replace(".tgz", "")
            output_path = f"{base_name}_unlocked.tar.gz"
        elif filename.endswith(".tar.bz2"):
            base_name = filename.replace(".tar.bz2", "")
            output_path = f"{base_name}_unlocked.tar.bz2"
        elif filename.endswith(".tbz2"):
            base_name = filename.replace(".tbz2", "")
            output_path = f"{base_name}_unlocked.tar.bz2"
        elif filename.endswith(".tar.xz"):
            base_name = filename.replace(".tar.xz", "")
            output_path = f"{base_name}_unlocked.tar.xz"
        elif filename.endswith(".txz"):
            base_name = filename.replace(".txz", "")
            output_path = f"{base_name}_unlocked.tar.xz"
        else:
            base_name, ext = os.path.splitext(file_path)
            output_path = f"{base_name}_unlocked{ext}"
        
        self.log_message(f"Выбран файл: {os.path.basename(file_path)}")
        self.status.config(text="Обработка...")
        self.select_button.config(state=tk.DISABLED)
        
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
            self.update_status(f"Готово: {os.path.basename(output_path)}")
            messagebox.showinfo("Успех", "Пароль успешно снят!")
        else:
            self.update_status("Ошибка!")
            self.log_message(f"Ошибка: {result}")
            messagebox.showerror("Ошибка", f"Ошибка обработки: {result}")
        
        self.progress['value'] = 0
        self.select_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = ZipUnlockerApp()
    app.mainloop()