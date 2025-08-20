import os
import zipfile
import rarfile
import py7zr
from tqdm import tqdm

class PasswordCracker:
    def __init__(self):
        self.common_passwords = self.load_common_passwords()
    
    def load_common_passwords(self):
        wordlist_path = os.path.join(os.path.dirname(__file__), "wordlists", "common_passwords.txt")
        if os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        else:
            # Fallback to built-in common passwords
            return [
                '', '123', '1234', '12345', 'password', 'qwerty', 'abc123', 
                '111111', 'admin', 'passw0rd', '123456', '12345678',
                '123456789', 'letmein', 'welcome', 'monkey', 'sunshine',
                'password1', '123qwe', 'football', 'baseball', 'master'
            ]
    
    def crack_archive(self, file_path, file_type, progress_callback=None):
        passwords = self.common_passwords
        
        if file_type == 'zip':
            archive = zipfile.ZipFile(file_path)
            test_file = archive.namelist()[0] if archive.namelist() else None
            
            for password in tqdm(passwords, desc="Checking passwords"):
                if progress_callback:
                    progress_callback()
                
                try:
                    if test_file:
                        archive.open(test_file, pwd=password.encode())
                    return password
                except (RuntimeError, zipfile.BadZipFile):
                    continue
                except Exception:
                    try:
                        archive.extractall(path="temp_test", pwd=password.encode())
                        return password
                    except:
                        continue
            
        elif file_type == 'rar':
            archive = rarfile.RarFile(file_path)
            
            for password in tqdm(passwords, desc="Checking passwords"):
                if progress_callback:
                    progress_callback()
                
                try:
                    archive.extractall(path="temp_test", pwd=password)
                    return password
                except (rarfile.BadRarFile, rarfile.PasswordRequired):
                    continue
                except Exception as e:
                    if "password" in str(e).lower():
                        continue
                    else:
                        raise e
            
        elif file_type == '7z':
            for password in tqdm(passwords, desc="Checking passwords"):
                if progress_callback:
                    progress_callback()
                
                try:
                    with py7zr.SevenZipFile(file_path, 'r', password=password) as archive:
                        archive.extractall(path="temp_test")
                    return password
                except py7zr.exceptions.PasswordRequired:
                    continue
        
        return None