import os
import shutil
import zipfile
import tarfile
import py7zr
import rarfile
import patoolib
from password_cracker import PasswordCracker

class ArchiveUtils:
    def __init__(self):
        self.cracker = PasswordCracker()
        self.supported_formats = {
            '.zip': 'ZIP Archive',
            '.rar': 'RAR Archive',
            '.7z': '7-Zip Archive',
            '.tar': 'TAR Archive',
            '.gz': 'GZIP Compressed File',
            '.tgz': 'GZIP Compressed TAR',
            '.bz2': 'BZIP2 Compressed File',
            '.tbz2': 'BZIP2 Compressed TAR',
            '.xz': 'XZ Compressed File',
            '.txz': 'XZ Compressed TAR',
            '.z': 'Z Compressed File',
            '.lz': 'LZMA Compressed File',
            '.lzma': 'LZMA Compressed File',
            '.lzo': 'LZO Compressed File',
            '.rz': 'RZ Compressed File',
            '.sz': 'Snappy Compressed File',
            '.ace': 'ACE Archive',
            '.arj': 'ARJ Archive',
            '.cab': 'CAB Archive',
            '.cpio': 'CPIO Archive',
            '.deb': 'Debian Package',
            '.dmg': 'Apple Disk Image',
            '.iso': 'ISO Image',
            '.lha': 'LHA Archive',
            '.lzh': 'LZH Archive',
            '.msi': 'Microsoft Installer',
            '.rpm': 'RPM Package',
            '.udf': 'UDF Image',
            '.wim': 'Windows Imaging Format',
            '.xar': 'XAR Archive',
            '.zst': 'Zstandard Archive'
        }
    
    def get_file_type(self, filename):
        filename = filename.lower()
        for ext in sorted(self.supported_formats.keys(), key=len, reverse=True):
            if filename.endswith(ext):
                return ext
        return None
    
    def extract_archive(self, input_path, output_dir, password=None):
        file_type = self.get_file_type(input_path)
        
        if file_type in ('.zip', '.rar', '.7z'):
            if file_type == '.zip':
                with zipfile.ZipFile(input_path, 'r') as archive:
                    if password:
                        archive.extractall(output_dir, pwd=password.encode())
                    else:
                        archive.extractall(output_dir)
            
            elif file_type == '.rar':
                with rarfile.RarFile(input_path, 'r') as archive:
                    if password:
                        archive.extractall(output_dir, pwd=password)
                    else:
                        archive.extractall(output_dir)
            
            elif file_type == '.7z':
                with py7zr.SevenZipFile(input_path, 'r', password=password) as archive:
                    archive.extractall(output_dir)
        
        else:
            # Используем patoolib для остальных форматов
            try:
                if password:
                    # Для форматов, поддерживающих пароли через patoolib
                    patoolib.extract_archive(input_path, outdir=output_dir, password=password)
                else:
                    patoolib.extract_archive(input_path, outdir=output_dir)
            except:
                # Fallback для форматов без поддержки паролей
                if file_type in ('.tar', '.tgz', '.tbz2', '.txz', '.gz', '.bz2', '.xz'):
                    mode = 'r'
                    if file_type in ('.tgz', '.gz'):
                        mode = 'r:gz'
                    elif file_type in ('.tbz2', '.bz2'):
                        mode = 'r:bz2'
                    elif file_type in ('.txz', '.xz'):
                        mode = 'r:xz'
                    
                    with tarfile.open(input_path, mode) as archive:
                        archive.extractall(output_dir)
    
    def create_archive(self, input_dir, output_path, file_type):
        if file_type in ('.zip', '.rar', '.7z'):
            if file_type == '.zip':
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for root, _, files in os.walk(input_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, input_dir)
                            archive.write(file_path, arcname)
            
            elif file_type == '.rar':
                # RAR создается через patoolib, так как rarfile не поддерживает создание RAR
                patoolib.create_archive(output_path, [input_dir], program='rar')
            
            elif file_type == '.7z':
                with py7zr.SevenZipFile(output_path, 'w') as archive:
                    archive.writeall(input_dir, os.path.basename(input_dir))
        
        else:
            # Используем patoolib для остальных форматов
            patoolib.create_archive(output_path, [input_dir])
    
    def remove_password(self, input_path, output_path, progress_callback, status_callback):
        file_type = self.get_file_type(input_path)
        
        if not file_type:
            return "Unsupported file format"
        
        temp_dir = "temp_unpack"
        os.makedirs(temp_dir, exist_ok=True)
        
        password = None
        try:
            # Шаг 1: Попытка открыть без пароля
            status_callback("Checking archive...")
            progress_callback(10)
            
            try:
                self.extract_archive(input_path, temp_dir)
            except (RuntimeError, rarfile.PasswordRequired, py7zr.exceptions.PasswordRequired, 
                    patoolib.util.PatoolError, Exception) as e:
                if "password" in str(e).lower() or "encrypted" in str(e).lower():
                    # Шаг 2: Подбор пароля
                    status_callback("Cracking password...")
                    progress_callback(20)
                    
                    def update_progress():
                        progress_callback(20 + 30 * len(os.listdir(temp_dir)) / 100)
                    
                    password = self.cracker.crack_archive(input_path, file_type, update_progress)
                    if password is None:
                        return "Failed to crack password"
                    
                    status_callback(f"Password found: {password}")
                    progress_callback(60)
                    
                    # Шаг 3: Извлечение с найденным паролем
                    status_callback("Extracting files...")
                    self.extract_archive(input_path, temp_dir, password)
                else:
                    return f"Error opening archive: {str(e)}"
            
            # Шаг 4: Перепаковка без пароля
            status_callback("Creating new archive...")
            progress_callback(70)
            self.create_archive(temp_dir, output_path, file_type)
            
            progress_callback(100)
            return True
        
        except Exception as e:
            return str(e)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)