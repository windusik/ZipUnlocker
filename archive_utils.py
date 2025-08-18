import os
import shutil
import zipfile
import tarfile
import py7zr
import rarfile
import threading
import time

class ArchiveUtils:
    COMMON_PASSWORDS = [
        '', '123', '1234', '12345', 'password', 'qwerty', 'abc123', 
        '111111', 'admin', 'passw0rd', '123456', '12345678'
    ]

    @staticmethod
    def try_extract(archive, password, temp_dir, file_type):
        try:
            if file_type == 'zip':
                archive.extractall(temp_dir, pwd=password.encode())
                return True
            elif file_type == 'rar':
                archive.extractall(temp_dir, pwd=password)
                return True
            elif file_type == '7z':
                with py7zr.SevenZipFile(archive.filename, 'r', password=password) as sz:
                    sz.extractall(temp_dir)
                return True
            return False
        except:
            return False

    @staticmethod
    def crack_archive(file_path, file_type, progress_callback):
        try:
            if file_type == 'zip':
                archive = zipfile.ZipFile(file_path)
            elif file_type == 'rar':
                archive = rarfile.RarFile(file_path)
            elif file_type == '7z':
                archive = py7zr.SevenZipFile(file_path)
            else:
                return None
        except:
            return None

        total = len(ArchiveUtils.COMMON_PASSWORDS)
        for i, password in enumerate(ArchiveUtils.COMMON_PASSWORDS):
            progress_callback(int((i + 1) / total * 50))
            if ArchiveUtils.try_extract(archive, password, "temp_crack", file_type):
                return password
            time.sleep(0.01)  # Для плавного обновления прогресса
        return None

    @staticmethod
    def remove_password(input_path, output_path, progress_callback):
        filename = input_path.lower()
        
        if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
            file_type = 'tar.gz'
        elif filename.endswith(".zip"):
            file_type = 'zip'
        elif filename.endswith(".rar"):
            file_type = 'rar'
        elif filename.endswith(".7z"):
            file_type = '7z'
        else:
            return "Неподдерживаемый формат файла"
        
        temp_dir = "temp_unpack"
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs("temp_crack", exist_ok=True)
        
        password = None
        try:
            # Шаг 1: Попытка открыть без пароля
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
            except (RuntimeError, rarfile.PasswordRequired, py7zr.exceptions.PasswordRequired):
                # Шаг 2: Подбор пароля
                progress_callback(20)
                password = ArchiveUtils.crack_archive(input_path, file_type, progress_callback)
                if password is None:
                    return "Не удалось подобрать пароль"
                
                # Шаг 3: Извлечение с найденным паролем
                progress_callback(60)
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
            progress_callback(70)
            if file_type in ('zip', 'rar'):
                with zipfile.ZipFile(output_path, 'w') as zip_out:
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
            
            progress_callback(100)
            return True
        
        except Exception as e:
            return str(e)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree("temp_crack", ignore_errors=True)