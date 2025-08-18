import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from archive_utils import ArchiveUtils
import threading

class ZipUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZipUnlockeк v1")
        self.geometry("500x400")
        self.configure(bg="#f0f0f0")
        
        title_label = tk.Label(
            self,
            text="ZipUnlocker",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=10)
        
        github_link = tk.Label(
            self,
            text="GitHub Repository",
            font=("Arial", 10, "underline"),
            fg="blue",
            cursor="hand2",
            bg="#f0f0f0"
        )
        github_link.pack(pady=5)
        github_link.bind("<Button-1>", lambda e: self.open_github())
        
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        self.select_button = tk.Button(
            button_frame,
            text="Выбрать архив",
            font=("Arial", 14),
            command=self.select_file
        )
        self.select_button.pack()
        
        # Информация о форматах
        formats_label = tk.Label(
            button_frame,
            text="Поддерживаемые форматы: .ZIP .RAR .TAR.GZ .7Z",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        formats_label.pack(pady=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress.pack(pady=10)
        
        # Статус
        self.status = tk.Label(
            self,
            text="Ожидание файла...",
            bg="#f0f0f0",
            font=("Arial", 10)
        )
        self.status.pack(pady=5)
        
        warning = tk.Label(
            self,
            text="Возможны ошибки снятия пароля",
            fg="red",
            bg="#f0f0f0",
            font=("Arial", 9, "italic")
        )
        warning.pack(side="bottom", pady=5)
    
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/windusik/ZipUnlocker")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите архив",
            filetypes=[
                ("Архивы", "*.zip *.rar *.7z *.tar.gz *.tgz"),
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
        else:
            base_name, ext = os.path.splitext(file_path)
            output_path = f"{base_name}_unlocked{ext}"
        
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
    
    def process_archive(self, input_path, output_path):
        def progress_callback(value):
            self.after(10, lambda: self.update_progress(value))
        
        result = ArchiveUtils.remove_password(input_path, output_path, progress_callback)
        
        if result is True:
            self.status.config(text=f"Готово: {os.path.basename(output_path)}")
            messagebox.showinfo("Успех", "Пароль успешно снят!")
        else:
            self.status.config(text="Ошибка!")
            messagebox.showerror("Ошибка", f"Ошибка обработки: {result}")
        
        self.progress['value'] = 0
        self.select_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = ZipUnlockerApp()
    app.mainloop()