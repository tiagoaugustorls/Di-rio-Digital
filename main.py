import tkinter as tk
from tkinter import messagebox
import logging
import sys
import os
from pathlib import Path
from ui.main_ui import MainUI


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diary_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiaryApp:
    """Aplicação principal do Diário Digital"""
    
    def __init__(self, root):
        self.root = root
        self.current_user = None
        self.main_ui = None
        
        # Configurações da janela principal
        self._setup_window()
        
        # Inicializa gerenciadores
        self._initialize_managers()
        
        # Configurações adicionais
        self._setup_event_handlers()
        
        # Mostra a tela de login
        self._show_login()
        
        logger.info("Aplicação inicializada com sucesso")

    def _setup_window(self):
        """Configura a janela principal"""
        self.root.title("Diário Digital")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)
        
        # Centraliza a janela na tela
        self._center_window()
        
        # Configura ícone da aplicação (se existir)
        self._setup_icon()

    def _center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_icon(self):
        """Configura o ícone da aplicação"""
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except tk.TclError:
                logger.warning("Não foi possível carregar o ícone da aplicação")

    def _initialize_managers(self):
        """Inicializa todos os gerenciadores necessários"""
        try:
            from database import DatabaseManager
            from themes import ThemeManager
            from auth import AuthManager
            
            self.db = DatabaseManager()
            self.theme_manager = ThemeManager(self.root)
            
            # Aplica tema salvo ou padrão
            saved_theme = self._get_saved_theme()
            self.theme_manager.apply_theme(saved_theme)
            
            self.auth = AuthManager(
                db=self.db,
                theme_manager=self.theme_manager,
                on_login_success=self.show_main_ui,
                root=self.root
            )
            
        except ImportError as e:
            logger.error(f"Erro ao importar módulos: {e}")
            self._show_error("Erro de Inicialização", 
                           "Não foi possível carregar todos os módulos necessários.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciadores: {e}")
            self._show_error("Erro de Inicialização", 
                           f"Erro inesperado durante a inicialização: {str(e)}")
            sys.exit(1)

    def _get_saved_theme(self):
        """Recupera o tema salvo ou retorna o padrão"""
        try:
            # Aqui você pode implementar a lógica para recuperar o tema salvo
            # Por exemplo, de um arquivo de configuração ou banco de dados
            return "light"  # Tema padrão
        except Exception:
            return "light"

    def _setup_event_handlers(self):
        """Configura handlers para eventos da aplicação"""
        # Handler para fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Handler para redimensionamento (opcional)
        self.root.bind('<Configure>', self._on_window_configure)

    def _show_login(self):
        """Mostra a tela de login"""
        try:
            self.auth.show_login_screen()
        except Exception as e:
            logger.error(f"Erro ao mostrar tela de login: {e}")
            self._show_error("Erro", "Não foi possível carregar a tela de login.")

    def show_main_ui(self, user):
        """Mostra a interface principal após login bem-sucedido"""
        try:
            self.current_user = user
            logger.info(f"Login bem-sucedido para usuário: {user.get('username', 'Unknown')}")
            
            # Remove todos os widgets da tela de login
            self._clear_window()
            
            # Importa e inicializa a UI principal
            from ui.main_ui import MainUI
            self.main_ui = MainUI(
                root=self.root,
                db=self.db,
                user=user,
                theme_manager=self.theme_manager,
                logout_callback=self._logout
            )
            
        except ImportError as e:
            logger.error(f"Erro ao importar MainUI: {e}")
            self._show_error("Erro", "Não foi possível carregar a interface principal.")
        except Exception as e:
            logger.error(f"Erro ao mostrar interface principal: {e}")
            self._show_error("Erro", f"Erro inesperado: {str(e)}")

    def _logout(self):
        """Realiza logout e volta para tela de login"""
        try:
            logger.info(f"Logout do usuário: {self.current_user.get('username', 'Unknown')}")
            
            # Limpa referências
            self.current_user = None
            self.main_ui = None
            
            # Limpa a tela
            self._clear_window()
            
            # Volta para tela de login
            self.auth.show_login_screen()
            
        except Exception as e:
            logger.error(f"Erro durante logout: {e}")
            self._show_error("Erro", "Erro durante o logout.")

    def _clear_window(self):
        """Remove todos os widgets da janela"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _on_closing(self):
        """Handler para fechamento da aplicação"""
        try:
            if self.current_user:
                # Salva dados pendentes se necessário
                if hasattr(self.main_ui, 'save_pending_changes'):
                    self.main_ui.save_pending_changes()
            
            # Fecha conexões do banco de dados
            if hasattr(self.db, 'close'):
                self.db.close()
            
            logger.info("Aplicação fechada com sucesso")
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Erro ao fechar aplicação: {e}")
            self.root.destroy()

    def _on_window_configure(self, event):
        """Handler para eventos de configuração da janela"""
        # Implementar se necessário (ex: salvar posição/tamanho da janela)
        pass

    def _show_error(self, title, message):
        """Mostra mensagem de erro padronizada"""
        messagebox.showerror(title, message)

def main():
    """Função principal da aplicação"""
    try:
        # Verifica se todos os arquivos necessários existem
        required_files = ['auth.py', 'database.py', 'themes.py']
        missing_files = [f for f in required_files if not Path(f).exists()]
        
        if missing_files:
            messagebox.showerror(
                "Arquivos Ausentes", 
                f"Os seguintes arquivos são necessários:\n{', '.join(missing_files)}"
            )
            sys.exit(1)
        
        # Cria e executa a aplicação
        root = tk.Tk()
        app = DiaryApp(root)
        root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal na aplicação: {e}")
        messagebox.showerror(
            "Erro Fatal", 
            f"Ocorreu um erro inesperado:\n{str(e)}\n\nVerifique o arquivo de log para mais detalhes."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()