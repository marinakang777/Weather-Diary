import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")

        self.records = []
        self.filename = "weather_data.json"

        self.load_from_file()
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # Frame для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=25)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=2)

        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=0, column=6, padx=5, pady=2)

        add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        add_btn.grid(row=0, column=7, padx=10, pady=2)

        # Frame для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        filter_btn = ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters)
        filter_btn.grid(row=0, column=4, padx=5)

        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.grid(row=0, column=5, padx=5)

        # Таблица для отображения записей
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=250)
        self.tree.column("precipitation", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        save_btn = ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file)
        save_btn.pack(side="left", padx=5)

        load_btn = ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file)
        load_btn.pack(side="left", padx=5)

        exit_btn = ttk.Button(btn_frame, text="Выход", command=self.root.quit)
        exit_btn.pack(side="right", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        try:
            temp_value = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return

        record = {
            "date": date,
            "temperature": temp_value,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }

        self.records.append(record)
        self.update_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def update_table(self, filtered_records=None):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        records_to_show = filtered_records if filtered_records is not None else self.records

        for record in records_to_show:
            self.tree.insert("", tk.END, values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))

    def apply_filters(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records.copy()

        if filter_date:
            if self.validate_date(filter_date):
                filtered = [r for r in filtered if r["date"] == filter_date]
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
                return

        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом")
                return

        self.update_table(filtered)
        messagebox.showinfo("Фильтр", f"Найдено записей: {len(filtered)}")

    def reset_filters(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
        messagebox.showinfo("Фильтр", "Фильтры сброшены")

    def save_to_file(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
                self.update_table()
                messagebox.showinfo("Загрузка", f"Данные загружены из {self.filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
        else:
            messagebox.showwarning("Загрузка", "Файл не найден. Начинаем с пустого дневника")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
