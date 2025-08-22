import os
import zipfile
import rarfile
import py7zr
from tqdm import tqdm
import threading
import queue
import time

class PasswordCracker:
    def __init__(self):
        self.common_passwords = self.load_password_list("common_passwords.txt")
        self.russian_passwords = self.load_password_list("russian_passwords.txt")
        self.advanced_passwords = self.load_password_list("advanced_passwords.txt")
        self.all_passwords = self.common_passwords + self.russian_passwords + self.advanced_passwords
        self.password_queue = queue.Queue()
        self.found_password = None
        self.stop_event = threading.Event()
        
        for pwd in self.all_passwords:
            self.password_queue.put(pwd)
    
    def load_password_list(self, filename):
        wordlist_path = os.path.join(os.path.dirname(__file__), "wordlists", filename)
        passwords = []
        if os.path.exists(wordlist_path):
            try:
                with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
            except:
                with open(wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
        return passwords
    
    def crack_worker(self, file_path, file_type, progress_callback):
        while not self.password_queue.empty() and not self.stop_event.is_set():
            try:
                password = self.password_queue.get_nowait()
                
                if progress_callback:
                    progress_callback()
                
                try:
                    if file_type == 'zip':
                        with zipfile.ZipFile(file_path) as archive:
                            for file_info in archive.filelist:
                                try:
                                    archive.open(file_info, pwd=password.encode())
                                    self.found_password = password
                                    self.stop_event.set()
                                    return
                                except:
                                    continue
                    
                    elif file_type == 'rar':
                        with rarfile.RarFile(file_path) as archive:
                            archive.testrarity(pwd=password)
                            self.found_password = password
                            self.stop_event.set()
                            return
                    
                    elif file_type == '7z':
                        with py7zr.SevenZipFile(file_path, 'r', password=password) as archive:
                            archive.getnames()
                            self.found_password = password
                            self.stop_event.set()
                            return
                
                except (RuntimeError, zipfile.BadZipFile, rarfile.BadRarFile, 
                        rarfile.PasswordRequired, py7zr.exceptions.PasswordRequired, 
                        py7zr.exceptions.Bad7zFile, Exception):
                    continue
                    
            except queue.Empty:
                break
    
    def crack_archive(self, file_path, file_type, progress_callback=None):
        self.found_password = None
        self.stop_event.clear()
        
        threads = []
        for _ in range(8):
            thread = threading.Thread(
                target=self.crack_worker, 
                args=(file_path, file_type, progress_callback),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        return self.found_password