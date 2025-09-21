from tkinter import ttk, Menu, simpledialog, messagebox

from ui.entry_ui import EntryUI
from ui.list_ui import ListUI
from export.export import ExportManager

from datetime import datetime

class MainUI:
    def __init__(self, root, db, user, theme_manager, logout_callback):
        self.root = root
        self.db = db
        self.user = user
        self.theme = theme_manager
        self.logout_callback = logout_callback

        self.frame = ttk.Frame(root, style=f'{self.theme.current_theme}.TFrame')
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Barra de menu
        menu_bar = ttk.Frame(self.frame, style=f'{self.theme.current_theme}.TFrame')
        menu_bar.pack(fill='x', padx=5, pady=5)

        ttk.Button(menu_bar, text='Nova Entrada', command=self.show_new_entry).pack(side='left', padx=5)
        ttk.Button(menu_bar, text='Minhas Entradas', command=self.show_entries).pack(side='left', padx=5)
        ttk.Button(menu_bar, text='Alternar Tema', command=self.toggle_theme).pack(side='left', padx=5)

        # Botão com menu de exportação
        export_btn = ttk.Menubutton(menu_bar, text='Exportar')
        export_menu = Menu(export_btn, tearoff=0)
        export_menu.add_command(label='Exportar tudo (PDF)', command=self.export_all_pdf)
        export_menu.add_command(label='Exportar tudo (TXT)', command=self.export_all_txt)
        export_menu.add_separator()
        export_menu.add_command(label='Por data (PDF)', command=self.export_by_date_pdf)
        export_menu.add_command(label='Por data (TXT)', command=self.export_by_date_txt)
        export_menu.add_separator()
        export_menu.add_command(label='Favoritos (PDF)', command=self.export_favorites_pdf)
        export_menu.add_command(label='Favoritos (TXT)', command=self.export_favorites_txt)
        export_btn["menu"] = export_menu
        export_btn.pack(side='left', padx=5)

        ttk.Button(menu_bar, text='Sair', command=self.logout_callback).pack(side='right', padx=5)

        # Frame de conteúdo
        self.content_frame = ttk.Frame(self.frame, style=f'{self.theme.current_theme}.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Inicializa sub-interfaces
        self.entry_ui = EntryUI(self.content_frame, self.db, self.user, self.theme)
        self.list_ui = ListUI(self.content_frame, self.db, self.user, self.theme)

        self.show_entries()

    def show_new_entry(self):
        self.clear_content()
        self.entry_ui.show()

    def show_entries(self):
        self.clear_content()
        self.list_ui.show()

    def toggle_theme(self):
        new_theme = self.theme.toggle()
        self.frame.configure(style=f'{new_theme}.TFrame')
        self.entry_ui.update_theme(new_theme)
        self.list_ui.update_theme(new_theme)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def get_entries_all(self):
        return self.db.get_entries_by_user_id(self.user['id'])

    def get_entries_by_date(self):
        start = simpledialog.askstring("Data inicial", "Formato: YYYY-MM-DD")
        end = simpledialog.askstring("Data final", "Formato: YYYY-MM-DD")
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Erro", "Formato de data inválido.")
            return []
        return self.db.get_entries_by_date_range(self.user['id'], start, end)

    def get_entries_favorites(self):
        return self.db.get_favorite_entries(self.user['id'])

    def export_entries(self, entries, format):
        if not entries:
            messagebox.showinfo("Sem dados", "Nenhuma entrada encontrada para exportar.")
            return
        manager = ExportManager(entries, self.user['username'])
        if format == "pdf":
            manager.to_pdf()
        else:
            manager.to_txt()

    def export_all_pdf(self):
        self.export_entries(self.get_entries_all(), "pdf")

    def export_all_txt(self):
        self.export_entries(self.get_entries_all(), "txt")

    def export_by_date_pdf(self):
        self.export_entries(self.get_entries_by_date(), "pdf")

    def export_by_date_txt(self):
        self.export_entries(self.get_entries_by_date(), "txt")

    def export_favorites_pdf(self):
        self.export_entries(self.get_entries_favorites(), "pdf")

    def export_favorites_txt(self):
        self.export_entries(self.get_entries_favorites(), "txt")
