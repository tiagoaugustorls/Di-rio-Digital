import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
from datetime import datetime

class EntryUI:
    def __init__(self, parent, db, user, theme_manager):
        self.parent = parent
        self.db = db
        self.user = user
        self.theme = theme_manager
        self.current_theme = self.theme.current_theme
        self.editing_entry_id = None
        self.frame = None

    def show(self, entry_id=None):
        self.clear()
        self.editing_entry_id = entry_id

        self.frame = ttk.Frame(self.parent, style=f'{self.current_theme}.TFrame')
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(self.frame, text="Data:", style=f'{self.current_theme}.TLabel').pack(anchor='w')
        self.calendar = DateEntry(self.frame, date_pattern='dd/mm/yyyy', font=('Segoe UI', 10))
        self.calendar.pack(fill='x', pady=5)

        ttk.Label(self.frame, text="Título:", style=f'{self.current_theme}.TLabel').pack(anchor='w', pady=(10, 0))
        self.title_entry = ttk.Entry(self.frame, font=('Segoe UI', 11))
        self.title_entry.pack(fill='x', pady=5)

        ttk.Label(self.frame, text="Conteúdo:", style=f'{self.current_theme}.TLabel').pack(anchor='w', pady=(10, 0))
        self.content_text = scrolledtext.ScrolledText(self.frame, wrap='word',
                                                      height=15,
                                                      font=('Segoe UI', 11),
                                                      bg='#ffffff' if self.current_theme == 'light' else '#1e1e1e',
                                                      fg='black' if self.current_theme == 'light' else 'white',
                                                      insertbackground='black' if self.current_theme == 'light' else 'white')
        self.content_text.pack(fill='both', expand=True, pady=5)

        btn_frame = ttk.Frame(self.frame, style=f'{self.current_theme}.TFrame')
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Salvar", style=f'{self.current_theme}.TButton', command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", style=f'{self.current_theme}.TButton', command=self.cancel).pack(side='left', padx=5)

        if self.editing_entry_id:
            self.load_entry_data()

    def load_entry_data(self):
        entry = self.db.get_entry(self.editing_entry_id, self.user['id'])
        if entry:
            entry_id, title, content, created_at = entry
            self.title_entry.insert(0, title)
            self.content_text.insert('1.0', content)
            try:
                date_obj = datetime.strptime(created_at[:10], "%Y-%m-%d")
                self.calendar.set_date(date_obj)
            except ValueError:
                self.calendar.set_date(datetime.now())
        else:
            messagebox.showerror("Erro", "Entrada não encontrada.")

    def save(self):
        try:
            date_obj = self.calendar.get_date()
            title = self.title_entry.get().strip()
            content = self.content_text.get('1.0', 'end').strip()
            sql_date = date_obj.strftime('%Y-%m-%d')

            if not all([title, content, sql_date]):
                messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
                return

            if self.editing_entry_id:
                success = self.db.update_entry(self.editing_entry_id, self.user['id'], sql_date, title, content)
                action = "atualizada"
            else:
                success = self.db.create_entry(self.user['id'], title, content, sql_date)
                action = "criada"

            if success:
                messagebox.showinfo("Sucesso", f"Entrada {action} com sucesso!")
                self.cancel()
            else:
                messagebox.showerror("Erro", f"Falha ao {action} entrada.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar entrada:\n{str(e)}")

    def cancel(self):
        self.clear()
        from ui.list_ui import ListUI
        list_ui = ListUI(self.parent, self.db, self.user, self.theme)
        list_ui.show()

    def clear(self):
        if self.frame:
            self.frame.destroy()
    
    def update_theme(self, new_theme):
        """Atualiza o tema da interface e reaplica o estilo"""
        self.current_theme = new_theme
        if self.frame:
            self.show(self.editing_entry_id)
