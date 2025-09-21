from tkinter import ttk
from tkinter import messagebox

class LoginUI:
    def __init__(self, root, login_callback, register_callback, theme_manager):
        self.root = root
        self.login_callback = login_callback
        self.register_callback = register_callback
        self.theme = theme_manager
        self.current_theme = theme_manager.current_theme

        # Frame principal que ocupa toda a janela
        self.frame = ttk.Frame(root, style=f'{self.current_theme}.TFrame')
        self.frame.pack(fill='both', expand=True)

        # Permite que a frame cresça com a janela
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.create_widgets()

    def destroy(self):
        self.frame.destroy()

    def create_widgets(self):
        # Container central que se ajusta
        container = ttk.Frame(self.frame, style=f'{self.current_theme}.TFrame', padding=20)
        container.grid(row=0, column=0, sticky='nsew')
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Título
        title = ttk.Label(container, text="Diário Pessoal", style=f'{self.current_theme}.Title.TLabel', font=('Helvetica', 18, 'bold'))
        title.grid(row=0, column=0, pady=(10, 20))

        # Notebook com abas de login e cadastro
        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky='nsew')

        # Login Tab
        login_tab = ttk.Frame(notebook, style=f'{self.current_theme}.TFrame', padding=20)
        notebook.add(login_tab, text='Login')

        login_tab.columnconfigure(0, weight=1)

        ttk.Label(login_tab, text='Usuário:', style=f'{self.current_theme}.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.user_entry = ttk.Entry(login_tab, style=f'{self.current_theme}.TEntry')
        self.user_entry.grid(row=1, column=0, sticky='ew', pady=5)

        ttk.Label(login_tab, text='Senha:', style=f'{self.current_theme}.TLabel').grid(row=2, column=0, sticky='w', pady=(10, 5))
        self.pass_entry = ttk.Entry(login_tab, show='*', style=f'{self.current_theme}.TEntry')
        self.pass_entry.grid(row=3, column=0, sticky='ew', pady=5)

        ttk.Button(login_tab, text='Entrar', style=f'{self.current_theme}.TButton', command=self.on_login)\
            .grid(row=4, column=0, sticky='ew', pady=(20, 0))

        # Register Tab
        register_tab = ttk.Frame(notebook, style=f'{self.current_theme}.TFrame', padding=20)
        notebook.add(register_tab, text='Cadastro')

        register_tab.columnconfigure(0, weight=1)

        ttk.Label(register_tab, text='Novo Usuário:', style=f'{self.current_theme}.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.new_user_entry = ttk.Entry(register_tab, style=f'{self.current_theme}.TEntry')
        self.new_user_entry.grid(row=1, column=0, sticky='ew', pady=5)

        ttk.Label(register_tab, text='Senha:', style=f'{self.current_theme}.TLabel').grid(row=2, column=0, sticky='w', pady=(10, 5))
        self.new_pass_entry = ttk.Entry(register_tab, show='*', style=f'{self.current_theme}.TEntry')
        self.new_pass_entry.grid(row=3, column=0, sticky='ew', pady=5)

        ttk.Label(register_tab, text='Confirmar Senha:', style=f'{self.current_theme}.TLabel').grid(row=4, column=0, sticky='w', pady=(10, 5))
        self.confirm_pass_entry = ttk.Entry(register_tab, show='*', style=f'{self.current_theme}.TEntry')
        self.confirm_pass_entry.grid(row=5, column=0, sticky='ew', pady=5)

        ttk.Button(register_tab, text='Cadastrar', style=f'{self.current_theme}.TButton', command=self.on_register)\
            .grid(row=6, column=0, sticky='ew', pady=(20, 0))

    def on_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if username and password:
            self.login_callback(username, password)
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos de login.")

    def on_register(self):
        username = self.new_user_entry.get().strip()
        password = self.new_pass_entry.get().strip()
        confirm = self.confirm_pass_entry.get().strip()
        if username and password and confirm:
            self.register_callback(username, password, confirm)
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos de cadastro.")
