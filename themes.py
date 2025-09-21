from tkinter import ttk
import tkinter as tk

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.current_theme = 'light'
        self.theme_configs = {}
        self.widgets_to_update = []  # Lista para rastrear widgets que precisam ser atualizados
        self.setup_themes()
    
    def setup_themes(self):
        self.style.theme_use('clam')  # Base do tema, compatível com personalização

        # Configurações dos temas
        self.theme_configs = {
            'light': {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'button_bg': '#e1e1e1',
                'button_fg': '#000000',
                'button_active': '#d5d5d5',
                'button_pressed': '#cccccc',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                # Listbox
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'listbox_select_bg': '#0078d4',
                'listbox_select_fg': '#ffffff',
                # Treeview (Tabelas)
                'treeview_bg': '#ffffff',
                'treeview_fg': '#000000',
                'treeview_select_bg': '#0078d4',
                'treeview_select_fg': '#ffffff',
                'treeview_heading_bg': '#e1e1e1',
                'treeview_heading_fg': '#000000',
                'treeview_odd_bg': '#f8f8f8',
                'treeview_even_bg': '#ffffff'
            },
            'dark': {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'button_bg': '#3d3d3d',
                'button_fg': '#ffffff',
                'button_active': '#4d4d4d',
                'button_pressed': '#5a5a5a',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'text_bg': '#404040',
                'text_fg': '#ffffff',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                # Listbox
                'listbox_bg': '#404040',
                'listbox_fg': '#ffffff',
                'listbox_select_bg': '#0078d4',
                'listbox_select_fg': '#ffffff',
                # Treeview (Tabelas)
                'treeview_bg': '#404040',
                'treeview_fg': '#ffffff',
                'treeview_select_bg': '#0078d4',
                'treeview_select_fg': '#ffffff',
                'treeview_heading_bg': '#3d3d3d',
                'treeview_heading_fg': '#ffffff',
                'treeview_odd_bg': '#454545',
                'treeview_even_bg': '#404040'
            }
        }

        # Configurar estilos para ambos os temas
        for theme_name, config in self.theme_configs.items():
            # Frame
            self.style.configure(f'{theme_name}.TFrame', 
                               background=config['bg'])
            
            # Label
            self.style.configure(f'{theme_name}.TLabel', 
                               background=config['bg'], 
                               foreground=config['fg'])
            
            # Button
            self.style.configure(f'{theme_name}.TButton', 
                               background=config['button_bg'], 
                               foreground=config['button_fg'],
                               borderwidth=1,
                               focuscolor='none')
            
            # Entry
            self.style.configure(f'{theme_name}.TEntry',
                               fieldbackground=config['entry_bg'],
                               foreground=config['entry_fg'],
                               borderwidth=1)
            
            # Scrollbar
            self.style.configure(f'{theme_name}.Vertical.TScrollbar',
                               background=config['button_bg'],
                               troughcolor=config['bg'],
                               borderwidth=1)
            
            # Notebook (abas)
            self.style.configure(f'{theme_name}.TNotebook',
                               background=config['bg'])
            self.style.configure(f'{theme_name}.TNotebook.Tab',
                               background=config['button_bg'],
                               foreground=config['fg'])
            
            # Treeview (Tabelas)
            self.style.configure(f'{theme_name}.Treeview',
                               background=config['treeview_bg'],
                               foreground=config['treeview_fg'],
                               fieldbackground=config['treeview_bg'],
                               borderwidth=1)
            
            self.style.configure(f'{theme_name}.Treeview.Heading',
                               background=config['treeview_heading_bg'],
                               foreground=config['treeview_heading_fg'],
                               borderwidth=1)

            # Mapeamento para hover/focus
            self.style.map(f'{theme_name}.TButton',
                background=[('active', config['button_active']), 
                          ('pressed', config['button_pressed'])])
            
            self.style.map(f'{theme_name}.TNotebook.Tab',
                background=[('selected', config['select_bg']),
                          ('active', config['button_active'])])
            
            self.style.map(f'{theme_name}.Treeview',
                background=[('selected', config['treeview_select_bg'])],
                foreground=[('selected', config['treeview_select_fg'])])
            
            self.style.map(f'{theme_name}.Treeview.Heading',
                background=[('active', config['button_active'])])

    def register_widget(self, widget, widget_type='default'):
        """Registra um widget para ser atualizado quando o tema mudar"""
        self.widgets_to_update.append((widget, widget_type))

    def apply_theme(self, theme):
        """Aplica o tema ao root e atualiza todos os widgets registrados"""
        if theme not in self.theme_configs:
            print(f"Tema '{theme}' não encontrado. Usando tema padrão 'light'.")
            theme = 'light'
            
        self.current_theme = theme
        config = self.theme_configs[theme]
        
        # Atualizar background do root
        self.root.configure(background=config['bg'])
        
        # Atualizar widgets registrados
        for widget, widget_type in self.widgets_to_update:
            try:
                if isinstance(widget, tk.Text):
                    widget.configure(
                        bg=config['text_bg'],
                        fg=config['text_fg'],
                        insertbackground=config['fg'],
                        selectbackground=config['select_bg'],
                        selectforeground=config['select_fg']
                    )
                elif isinstance(widget, tk.Entry):
                    widget.configure(
                        bg=config['entry_bg'],
                        fg=config['entry_fg'],
                        insertbackground=config['fg']
                    )
                elif isinstance(widget, tk.Listbox):
                    widget.configure(
                        bg=config['listbox_bg'],
                        fg=config['listbox_fg'],
                        selectbackground=config['listbox_select_bg'],
                        selectforeground=config['listbox_select_fg'],
                        highlightbackground=config['bg'],
                        highlightcolor=config['select_bg']
                    )
                elif isinstance(widget, ttk.Treeview):
                    # Aplicar estilo específico do tema
                    widget.configure(style=f'{theme}.Treeview')
                    # Configurar tags para linhas alternadas
                    widget.tag_configure('oddrow', background=config['treeview_odd_bg'])
                    widget.tag_configure('evenrow', background=config['treeview_even_bg'])
                elif isinstance(widget, (tk.Label, tk.Button, tk.Frame)):
                    if hasattr(widget, 'configure'):
                        if isinstance(widget, tk.Button):
                            widget.configure(
                                bg=config['button_bg'],
                                fg=config['button_fg'],
                                activebackground=config['button_active'],
                                activeforeground=config['button_fg']
                            )
                        else:
                            widget.configure(
                                bg=config['bg'],
                                fg=config['fg']
                            )
                # Para widgets TTK genéricos
                elif hasattr(widget, 'configure') and hasattr(widget, 'winfo_class'):
                    widget_class = widget.winfo_class()
                    if widget_class in ['TButton', 'TLabel', 'TFrame', 'TEntry']:
                        widget.configure(style=f'{theme}.{widget_class}')
            except tk.TclError:
                # Widget foi destruído, remover da lista
                self.widgets_to_update.remove((widget, widget_type))

    def set_theme(self, theme):
        """Alias para apply_theme, mantendo compatibilidade com código existente"""
        self.apply_theme(theme)

    def toggle(self):
        """Alterna entre tema claro e escuro"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        return new_theme

    def get_current_theme(self):
        """Retorna o tema atual"""
        return self.current_theme

    def get_theme_config(self, key=None):
        """Retorna a configuração do tema atual ou uma chave específica"""
        config = self.theme_configs[self.current_theme]
        if key:
            return config.get(key, None)
        return config

    def update_treeview_rows(self, treeview):
        """Atualiza as cores das linhas alternadas de uma Treeview"""
        config = self.theme_configs[self.current_theme]
        
        # Aplicar tags alternadas às linhas existentes
        for i, item in enumerate(treeview.get_children()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            treeview.item(item, tags=(tag,))
        
        # Configurar as tags com as cores do tema atual
        treeview.tag_configure('oddrow', 
                              background=config['treeview_odd_bg'],
                              foreground=config['treeview_fg'])
        treeview.tag_configure('evenrow', 
                              background=config['treeview_even_bg'],
                              foreground=config['treeview_fg'])

    def create_themed_treeview(self, parent, **kwargs):
        """Cria uma Treeview já configurada com o tema atual"""
        treeview = ttk.Treeview(parent, style=f'{self.current_theme}.Treeview', **kwargs)
        self.register_widget(treeview)
        return treeview

    def create_themed_listbox(self, parent, **kwargs):
        """Cria uma Listbox já configurada com o tema atual"""
        config = self.theme_configs[self.current_theme]
        listbox = tk.Listbox(parent,
                            bg=config['listbox_bg'],
                            fg=config['listbox_fg'],
                            selectbackground=config['listbox_select_bg'],
                            selectforeground=config['listbox_select_fg'],
                            **kwargs)
        self.register_widget(listbox)
        return listbox

    def create_themed_button(self, parent, use_ttk=True, **kwargs):
        """Cria um botão já configurado com o tema atual"""
        if use_ttk:
            button = ttk.Button(parent, style=f'{self.current_theme}.TButton', **kwargs)
        else:
            config = self.theme_configs[self.current_theme]
            button = tk.Button(parent,
                              bg=config['button_bg'],
                              fg=config['button_fg'],
                              activebackground=config['button_active'],
                              activeforeground=config['button_fg'],
                              **kwargs)
        self.register_widget(button)
        return button

    def add_custom_theme(self, theme_name, config):
        """Adiciona um tema personalizado"""
        self.theme_configs[theme_name] = config
        # Reconfigurar estilos para incluir o novo tema
        self.setup_themes()

# Exemplo de uso completo:
"""
# No seu código principal:
root = tk.Tk()
theme_manager = ThemeManager(root)

# Método 1: Criar widgets já tematizados
button = theme_manager.create_themed_button(root, text="Botão Tematizado")
listbox = theme_manager.create_themed_listbox(root)
treeview = theme_manager.create_themed_treeview(root, columns=('col1', 'col2'))

# Método 2: Registrar widgets existentes
existing_button = tk.Button(root, text="Botão Existente")
theme_manager.register_widget(existing_button)

existing_listbox = tk.Listbox(root)
theme_manager.register_widget(existing_listbox)

existing_treeview = ttk.Treeview(root)
theme_manager.register_widget(existing_treeview)

# Para Treeview, adicionar linhas alternadas
for i in range(10):
    item_id = existing_treeview.insert('', 'end', values=(f'Item {i}', f'Valor {i}'))

# Atualizar cores das linhas
theme_manager.update_treeview_rows(existing_treeview)

# Alternar tema (todos os widgets serão atualizados automaticamente)
theme_manager.toggle()

# Ou aplicar tema específico
theme_manager.apply_theme('dark')
"""