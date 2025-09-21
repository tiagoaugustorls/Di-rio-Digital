import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class ListUI:
    def __init__(self, parent, db, user, theme_manager):
        self.favorite_button = None
        self.parent = parent
        self.db = db
        self.user = user
        self.theme = theme_manager
        self.current_theme = theme_manager.current_theme
        self.tree = None
        self.search_entry = None
        self.frame = None

    def show(self):
        self.clear()
        self.frame = ttk.Frame(self.parent, style=f'{self.current_theme}.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Expansão dinâmica
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Frame de pesquisa
        search_frame = ttk.Frame(self.frame, style=f'{self.current_theme}.TFrame')
        search_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=0)

        ttk.Label(search_frame, text='🔍 Pesquisar:', style=f'{self.current_theme}.TLabel').grid(row=0, column=0, padx=(0, 5), sticky='w')

        self.search_entry = ttk.Entry(search_frame, font=('Segoe UI', 10))
        self.search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        self.search_entry.bind('<KeyRelease>', self.filter)

        ttk.Button(search_frame, text='Limpar', style=f'{self.current_theme}.TButton', command=self.clear_search).grid(row=0, column=2, padx=5)

        # ✅ Botão Favoritar reposicionado corretamente
        self.favorite_button = ttk.Button(search_frame,
                                        text="★ Favoritar / Desfavoritar",
                                        style=f'{self.current_theme}.TButton',
                                        command=self.toggle_favorite)
        self.favorite_button.grid(row=0, column=3, padx=5)

        # Estilo da Treeview
        style = ttk.Style()
        style.theme_use('clam')
        tree_style = f"{self.current_theme}.Treeview"
        style.configure(tree_style,
                        background='#ffffff' if self.current_theme == 'light' else '#2b2b2b',
                        foreground='black' if self.current_theme == 'light' else 'white',
                        rowheight=28,
                        fieldbackground='#f5f5f5' if self.current_theme == 'light' else '#1e1e1e')
        style.map(tree_style,
                background=[('selected', '#cce5ff' if self.current_theme == 'light' else '#444')],
                foreground=[('selected', 'black' if self.current_theme == 'light' else 'white')])

        # Treeview + Scrollbar em um frame
        tree_container = ttk.Frame(self.frame)
        tree_container.grid(row=1, column=0, sticky='nsew')
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_container,
                                columns=('id', 'date', 'title', 'preview', 'favorito'),
                                show='headings',
                                style=tree_style)
        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Criado em')
        self.tree.heading('title', text='Título')
        self.tree.heading('preview', text='Prévia')
        self.tree.heading("favorito", text="★")

        self.tree.column('id', width=50, stretch=False)
        self.tree.column('date', width=100, stretch=False)
        self.tree.column('title', width=200, stretch=False)
        self.tree.column('preview', width=400, stretch=True)
        self.tree.column('favorito', width=50, anchor='center', stretch=False)

        # Botões no rodapé
        btn_frame = ttk.Frame(self.frame, style=f'{self.current_theme}.TFrame')
        btn_frame.grid(row=2, column=0, pady=10, sticky='ew')
        btn_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(btn_frame, text='Visualizar', style=f'{self.current_theme}.TButton', command=self.view).grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(btn_frame, text='Editar', style=f'{self.current_theme}.TButton', command=self.edit).grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Button(btn_frame, text='Excluir', style=f'{self.current_theme}.TButton', command=self.delete).grid(row=0, column=2, padx=5, sticky='ew')

        self.load_data()



    def load_data(self, search_term=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        entries = self.db.get_entries(self.user['id'], search_term)
        for i, entry in enumerate(entries):
            entry_id, title, content, created_at, updated_at, favorite = entry
            preview = content[:100] + '...' if len(content) > 100 else content
            formatted_date = datetime.strptime(created_at[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
            star = '★' if favorite else ''
            tag = 'odd' if i % 2 == 0 else 'even'
            self.tree.insert('', 'end', values=(entry_id, formatted_date, title, preview, star), tags=(tag,))

        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f7f7f7')

    def filter(self, event=None):
        self.load_data(self.search_entry.get())

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.load_data()

    def view(self):
        selected = self.get_selected()
        if not selected:
            return
        entry_id, formatted_date, title, content = selected

        view_window = tk.Toplevel(self.parent)
        view_window.title(f"Entrada - {title}")
        view_window.geometry("700x500")

        main_frame = ttk.Frame(view_window, style=f'{self.current_theme}.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(main_frame, style=f'{self.current_theme}.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(header_frame,
                  text=f"{formatted_date} - {title}",
                  font=('Segoe UI', 12, 'bold'),
                  style=f'{self.current_theme}.TLabel').pack(side='left')

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True)

        text = scrolledtext.ScrolledText(text_frame,
                                         wrap='word',
                                         font=('Segoe UI', 11),
                                         padx=10, pady=10,
                                         bg='#ffffff' if self.current_theme == 'light' else '#1e1e1e',
                                         fg='black' if self.current_theme == 'light' else 'white',
                                         insertbackground='black' if self.current_theme == 'light' else 'white')
        text.insert('1.0', content)
        text.config(state='disabled')
        text.pack(fill='both', expand=True)

        ttk.Button(main_frame, text="Fechar", style=f'{self.current_theme}.TButton', command=view_window.destroy).pack(pady=(10, 0))

    def edit(self):
        selected = self.get_selected()
        if not selected:
            return
        entry_id = selected[0]
        self.clear()
        from ui.entry_ui import EntryUI
        entry_ui = EntryUI(parent=self.parent, db=self.db, user=self.user, theme_manager=self.theme)
        entry_ui.show(entry_id=entry_id)

    def delete(self):
        selected = self.get_selected()
        if not selected:
            return
        if messagebox.askyesno("Confirmar", "Deseja excluir esta entrada?"):
            entry_id = selected[0]
            success = self.db.delete_entry(entry_id, self.user['id'])
            if success:
                messagebox.showinfo("Sucesso", "Entrada excluída com sucesso!")
                self.load_data()
            else:
                messagebox.showerror("Erro", "Falha ao excluir entrada")

    def get_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma entrada")
            return None
        item = self.tree.item(selection[0])
        entry_id = item['values'][0]
        entry = self.db.get_entry(entry_id, self.user['id'])
        if not entry:
            messagebox.showerror("Erro", "Entrada não encontrada")
            return None
        entry_id, title, content, date = entry
        try:
            formatted_date = datetime.fromisoformat(date).strftime('%d/%m/%Y')
        except ValueError:
            formatted_date = date
        return (entry_id, formatted_date, title, content)

    def clear(self):
        if self.frame:
            self.frame.destroy()

    def update_theme(self, new_theme):
        self.current_theme = new_theme
        if self.frame:
            self.show()

    def toggle_favorite(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Aviso", "Selecione uma entrada.")
            return
        item = self.tree.item(selected)
        entry_id = item["values"][0]
        current_star = item["values"][-1]
        new_fav = 0 if current_star == '★' else 1
        if self.db.set_favorite(entry_id, new_fav):
            messagebox.showinfo("Sucesso", "Entrada atualizada.")
            self.show()
