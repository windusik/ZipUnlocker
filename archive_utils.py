import os
import shutil
import zipfile
import tarfile
import py7zr
import rarfile
from password_cracker import PasswordCracker

class ArchiveUtils:
    def __init__(self):
        self.cracker = PasswordCracker()
    
    def remove_password(self, input_path, output_path, progress_callback, status_callback):
        filename = input_path.lower()
        
        if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
            file_type = 'tar.gz'
        elif filename.endswith(".zip"):
            file_type = 'zip'
        elif filename.endswith(".rar"):
            file_type = 'rar'
        elif filename.endswith(".7z"):
            file_type = '7z'
        elif filename.endswith(".tar.bz2") or filename.endswith(".tbz2"):
            file_type = 'tar.bz2'
        elif filename.endswith(".tar.xz") or filename.endswith(".txz"):
            file_type = 'tar.xz'
        else:
            return "Неподдерживаемый формат файла"
        
        temp_dir = "temp_unpack"
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs("temp_test", exist_ok=True)
        
        password = None
        try:
            # Шаг 1: Попытка открыть без пароля
            status_callback("Проверка архива...")
            progress_callback(10)
            try:
                if file_type == 'zip':
                    with zipfile.ZipFile(input_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif file_type == 'rar':
                    with rarfile.RarFile(input_path, 'r') as rar_ref:
                        rar_ref.extractall(temp_dir)
                elif file_type == '7z':
                    with py7zr.SevenZipFile(input_path, 'r') as sz_ref:
                        sz_ref.extractall(temp_dir)
                elif file_type == 'tar.gz':
                    with tarfile.open(input_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(temp_dir)
                elif file_type == 'tar.bz2':
                    with tarfile.open(input_path, 'r:bz2') as tar_ref:
                        tar_ref.extractall(temp_dir)
                elif file_type == 'tar.xz':
                    with tarfile.open(input_path, 'r:xz') as tar_ref:
                        tar_ref.extractall(temp_dir)
            except (RuntimeError, rarfile.PasswordRequired, py7zr.exceptions.PasswordRequired):
                # Шаг 2: Подбор пароля
                status_callback("Подбор пароля...")
                progress_callback(20)
                
                def update_progress():
                    progress_callback(20 + 30 * len(os.listdir("temp_test")) / 100)
                
                password = self.cracker.crack_archive(input_path, file_type, update_progress)
                if password is None:
                    return "Не удалось подобрать пароль"
                
                status_callback(f"Найден пароль: {password}")
                progress_callback(60)
                
                # Шаг 3: Извлечение с найденным паролем
                status_callback("Извлечение файлов...")
                if file_type == 'zip':
                    with zipfile.ZipFile(input_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir, pwd=password.encode())
                elif file_type == 'rar':
                    with rarfile.RarFile(input_path, 'r') as rar_ref:
                        rar_ref.extractall(temp_dir, pwd=password)
                elif file_type == '7z':
                    with py7zr.SevenZipFile(input_path, 'r', password=password) as sz_ref:
                        sz_ref.extractall(temp_dir)
            
            # Шаг 4: Перепаковка без пароля
            status_callback("Создание нового архива...")
            progress_callback(70)
            if file_type in ('zip', 'rar'):
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_out.write(file_path, arcname)
            elif file_type == '7z':
                with py7zr.SevenZipFile(output_path, 'w') as sz_out:
                    sz_out.writeall(temp_dir, os.path.basename(output_path))
            elif file_type == 'tar.gz':
                with tarfile.open(output_path, 'w:gz') as tar_out:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            tar_out.add(file_path, arcname)
            elif file_type == 'tar.bz2':
                with tarfile.open(output_path, 'w:bz2') as tar_out:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            tar_out.add(file_path, arcname)
            elif file_type == 'tar.xz':
                with tarfile.open(output_path, 'w:xz') as tar_out:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            tar_out.add(file_path, arcname)
            
            progress_callback(100)
            return True
        
        except Exception as e:
            return str(e)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree("temp_test", ignore_errors=True)