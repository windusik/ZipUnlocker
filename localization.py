LANGUAGES = {
    "en": {
        "title": "ZipUnlocker v3",
        "final_release": "Final Release",
        "select_archive": "Select archive to unlock",
        "no_file_selected": "No file selected",
        "waiting": "Waiting...",
        "processing": "Processing...",
        "cracking_password": "Cracking password...",
        "password_found": "Password found: {}",
        "extracting": "Extracting files...",
        "creating_archive": "Creating new archive...",
        "done": "Done!",
        "error": "Error!",
        "unsupported_format": "Unsupported file format",
        "failed_to_crack": "Failed to crack password",
        "success_message": "Password successfully removed!",
        "stats": "Processed: {} | Success: {} | Errors: {}",
        "log_init": "ZipUnlocker v3 initialized and ready",
        "log_formats": "Supported formats: {}",
        "log_start": "Started processing: {}",
        "log_archive_type": "Archive type: {}",
        "log_success": "File successfully processed: {}",
        "log_error": "Processing error: {}",
        "copyright": "© 2025 Platon U. All rights reserved.",
        "choose_language": "Choose language"
    },
    "zh": {
        "title": "ZipUnlocker v3",
        "final_release": "最终版本",
        "select_archive": "选择要解锁的存档",
        "no_file_selected": "未选择文件",
        "waiting": "等待中...",
        "processing": "处理中...",
        "cracking_password": "破解密码...",
        "password_found": "找到密码: {}",
        "extracting": "提取文件中...",
        "creating_archive": "创建新存档...",
        "done": "完成！",
        "error": "错误！",
        "unsupported_format": "不支持的文件格式",
        "failed_to_crack": "无法破解密码",
        "success_message": "密码已成功移除！",
        "stats": "已处理: {} | 成功: {} | 错误: {}",
        "log_init": "ZipUnlocker v3 已初始化并准备就绪",
        "log_formats": "支持的格式: {}",
        "log_start": "开始处理: {}",
        "log_archive_type": "存档类型: {}",
        "log_success": "文件处理成功: {}",
        "log_error": "处理错误: {}",
        "copyright": "© 2025 Platon U. 保留所有权利。",
        "choose_language": "选择语言"
    },
    "ru": {
        "title": "ZipUnlocker v3",
        "final_release": "Финальный релиз",
        "select_archive": "Выбрать архив для разблокировки",
        "no_file_selected": "Файл не выбран",
        "waiting": "Ожидание...",
        "processing": "Обработка...",
        "cracking_password": "Подбор пароля...",
        "password_found": "Найден пароль: {}",
        "extracting": "Извлечение файлов...",
        "creating_archive": "Создание нового архива...",
        "done": "Готово!",
        "error": "Ошибка!",
        "unsupported_format": "Неподдерживаемый формат файла",
        "failed_to_crack": "Не удалось подобрать пароль",
        "success_message": "Пароль успешно снят!",
        "stats": "Обработано: {} | Успешно: {} | Ошибки: {}",
        "log_init": "ZipUnlocker v3 инициализирован и готов к работе",
        "log_formats": "Поддерживаемых форматов: {}",
        "log_start": "Начата обработка: {}",
        "log_archive_type": "Тип архива: {}",
        "log_success": "Файл успешно обработан: {}",
        "log_error": "Ошибка обработки: {}",
        "copyright": "© 2025 Platon U. Все права защищены.",
        "choose_language": "Выберите язык"
    }
}

def get_system_language():
    """Определяем язык системы по умолчанию"""
    import locale
    try:
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang:
            if 'zh' in sys_lang:
                return 'zh'
            elif 'ru' in sys_lang:
                return 'ru'
    except:
        pass
    return 'en'