import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
from datetime import datetime
import os

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Файл для хранения истории
        self.history_file = "password_history.json"
        self.history = self.load_history()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных паролей", 
                                font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Длина пароля
        length_frame = ttk.Frame(main_frame)
        length_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(length_frame, text="Длина пароля:").pack(side=tk.LEFT)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(length_frame, from_=4, to=32, 
                                      variable=self.length_var, orient=tk.HORIZONTAL,
                                      length=200, command=self.update_length_label)
        self.length_scale.pack(side=tk.LEFT, padx=10)
        
        self.length_label = ttk.Label(length_frame, text="12", width=3)
        self.length_label.pack(side=tk.LEFT)
        
        # Чекбоксы для выбора символов
        check_frame = ttk.LabelFrame(main_frame, text="Типы символов", padding="10")
        check_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.use_letters = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(check_frame, text="Буквы (a-z, A-Z)", 
                       variable=self.use_letters).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="Специальные символы (!@#$%^&*)", 
                       variable=self.use_special).grid(row=2, column=0, sticky=tk.W)
        
        # Поле для отображения пароля
        ttk.Label(main_frame, text="Сгенерированный пароль:").grid(row=3, column=0, 
                                                                     sticky=tk.W, pady=(10, 0))
        
        password_frame = ttk.Frame(main_frame)
        password_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                        state='readonly', font=('Courier', 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(password_frame, text="📋", width=3, 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(5, 0))
        
        # Кнопка генерации
        ttk.Button(main_frame, text="Сгенерировать пароль", 
                  command=self.generate_password).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Таблица истории
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview для истории
        columns = ('date', 'password', 'length', 'types')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        self.history_tree.heading('date', text='Дата')
        self.history_tree.heading('password', text='Пароль')
        self.history_tree.heading('length', text='Длина')
        self.history_tree.heading('types', text='Типы')
        
        self.history_tree.column('date', width=120)
        self.history_tree.column('password', width=200)
        self.history_tree.column('length', width=60)
        self.history_tree.column('types', width=120)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления историей
        button_frame = ttk.Frame(history_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в JSON", 
                  command=self.export_history).pack(side=tk.LEFT, padx=5)
        
        # Настройка весов
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Загрузка истории в таблицу
        self.update_history_table()
        
        # Привязка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_length_label(self, value):
        self.length_label.config(text=str(int(float(value))))
    
    def generate_password(self):
        length = int(self.length_var.get())
        
        # Проверка минимальной и максимальной длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа")
            return
        
        # Проверка выбора хотя бы одного типа символов
        if not any([self.use_letters.get(), self.use_digits.get(), self.use_special.get()]):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return
        
        # Формирование строки доступных символов
        chars = ""
        types_used = []
        
        if self.use_letters.get():
            chars += string.ascii_letters
            types_used.append("Буквы")
        if self.use_digits.get():
            chars += string.digits
            types_used.append("Цифры")
        if self.use_special.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            types_used.append("Спец.")
        
        # Генерация пароля с гарантией включения всех выбранных типов
        password = []
        
        # Добавляем по одному символу каждого выбранного типа
        if self.use_letters.get():
            password.append(random.choice(string.ascii_letters))
        if self.use_digits.get():
            password.append(random.choice(string.digits))
        if self.use_special.get():
            password.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # Заполняем остальную длину случайными символами
        for _ in range(length - len(password)):
            password.append(random.choice(chars))
        
        # Перемешиваем пароль
        random.shuffle(password)
        final_password = ''.join(password)
        
        # Отображаем пароль
        self.password_var.set(final_password)
        
        # Сохраняем в историю
        self.add_to_history(final_password, length, types_used)
    
    def add_to_history(self, password, length, types_used):
        entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'password': password,
            'length': length,'types': ', '.join(types_used)
        }
        
        self.history.append(entry)
        self.save_history()
        self.update_history_table()
    
    def update_history_table(self):
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей (последние сверху)
        for entry in reversed(self.history[-50:]):  # Показываем последние 50 записей
            self.history_tree.insert('', 0, values=(
                entry['date'],
                entry['password'],
                entry['length'],
                entry['types']
            ))
    
    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
    
    def export_history(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "История пуста")
            return
        
        try:
            with open('exported_passwords.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"История экспортирована в файл 'exported_passwords.json'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {str(e)}")
    
    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
    
    def on_closing(self):
        self.save_history()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
