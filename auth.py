import hashlib
import secrets
import logging
import re
from typing import Dict, Optional, Callable
from tkinter import messagebox
from ui.login_ui import LoginUI

logger = logging.getLogger(__name__)

class AuthManager:
    """Gerenciador de autenticação com segurança aprimorada"""
    
    # Configurações de segurança
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_TIME = 300  # 5 minutos em segundos
    
    def __init__(self, db, theme_manager, on_login_success: Callable, root):
        self.db = db
        self.theme_manager = theme_manager
        self.on_login_success = on_login_success
        self.root = root
        self.current_user = None
        self.login_ui = None
        
        # Controle de tentativas de login
        self.login_attempts = {}  # {username: {'count': int, 'last_attempt': timestamp}}
        
        logger.info("AuthManager inicializado")
    
    def _generate_salt(self) -> str:
        """Gera um salt aleatório para hash da senha"""
        return secrets.token_hex(32)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Gera hash seguro da senha com salt
        Retorna (hash, salt)
        """
        if salt is None:
            salt = self._generate_salt()
        
        # Combina senha com salt e faz múltiplas iterações
        combined = f"{password}{salt}"
        hashed = combined.encode()
        
        # Aplica hash múltiplas vezes para maior segurança
        for _ in range(100000):  # PBKDF2-like approach
            hashed = hashlib.sha256(hashed).digest()
        
        return hashed.hex(), salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        try:
            computed_hash, _ = self._hash_password(password, salt)
            return secrets.compare_digest(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False
    
    def _validate_password_strength(self, password: str) -> tuple:
        """
        Valida a força da senha
        Retorna (is_valid, error_message)
        """
        if len(password) < self.MIN_PASSWORD_LENGTH:
            return False, f"A senha deve ter pelo menos {self.MIN_PASSWORD_LENGTH} caracteres"
        
        # Verifica se tem pelo menos uma letra maiúscula
        if not re.search(r'[A-Z]', password):
            return False, "A senha deve conter pelo menos uma letra maiúscula"
        
        # Verifica se tem pelo menos uma letra minúscula
        if not re.search(r'[a-z]', password):
            return False, "A senha deve conter pelo menos uma letra minúscula"
        
        # Verifica se tem pelo menos um número
        if not re.search(r'\d', password):
            return False, "A senha deve conter pelo menos um número"
        
        # Verifica se tem pelo menos um caractere especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "A senha deve conter pelo menos um caractere especial (!@#$%^&*(),.?\":{}|<>)"
        
        return True, ""
    
    def _validate_username(self, username: str) -> tuple:
        """
        Valida o nome de usuário
        Retorna (is_valid, error_message)
        """
        if not username or len(username.strip()) == 0:
            return False, "Nome de usuário não pode estar vazio"
        
        if len(username) < 3:
            return False, "Nome de usuário deve ter pelo menos 3 caracteres"
        
        if len(username) > 50:
            return False, "Nome de usuário deve ter no máximo 50 caracteres"
        
        # Apenas letras, números e alguns caracteres especiais
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            return False, "Nome de usuário pode conter apenas letras, números, pontos, hífens e underscores"
        
        return True, ""
    
    def _is_user_locked(self, username: str) -> bool:
        """Verifica se o usuário está bloqueado por tentativas excessivas"""
        import time
        
        if username not in self.login_attempts:
            return False
        
        attempts_data = self.login_attempts[username]
        
        # Se não atingiu o limite, não está bloqueado
        if attempts_data['count'] < self.MAX_LOGIN_ATTEMPTS:
            return False
        
        # Verifica se o tempo de bloqueio já passou
        time_passed = time.time() - attempts_data['last_attempt']
        if time_passed > self.LOCKOUT_TIME:
            # Reset das tentativas após o tempo de bloqueio
            del self.login_attempts[username]
            return False
        
        return True
    
    def _record_login_attempt(self, username: str, success: bool):
        """Registra tentativa de login"""
        import time
        
        if success:
            # Remove registro de tentativas em caso de sucesso
            if username in self.login_attempts:
                del self.login_attempts[username]
        else:
            # Incrementa contador de tentativas falhadas
            if username not in self.login_attempts:
                self.login_attempts[username] = {'count': 0, 'last_attempt': 0}
            
            self.login_attempts[username]['count'] += 1
            self.login_attempts[username]['last_attempt'] = time.time()
    
    def login(self, username: str, password: str) -> bool:
        """Autentica um usuário com segurança aprimorada"""
        try:
            # Validação básica
            if not username or not password:
                messagebox.showerror("Erro", "Usuário e senha são obrigatórios")
                return False
            
            username = username.strip()
            
            # Verifica se usuário está bloqueado
            if self._is_user_locked(username):
                remaining_time = self.LOCKOUT_TIME - (
                    __import__('time').time() - self.login_attempts[username]['last_attempt']
                )
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                messagebox.showerror(
                    "Conta Bloqueada", 
                    f"Muitas tentativas de login. Tente novamente em {minutes}m {seconds}s"
                )
                return False
            
            # Busca usuário no banco de dados
            user_data = self.db.get_user_by_username(username)
            
            if not user_data:
                self._record_login_attempt(username, False)
                messagebox.showerror("Erro", "Usuário ou senha incorretos")
                logger.warning(f"Tentativa de login com usuário inexistente: {username}")
                return False
            
            # Extrai dados do usuário
            user_id, stored_username, password_hash, salt, theme_preference = user_data
            
            # Verifica senha
            if not self._verify_password(password, password_hash, salt):
                self._record_login_attempt(username, False)
                attempts_left = self.MAX_LOGIN_ATTEMPTS - self.login_attempts.get(username, {}).get('count', 0)
                messagebox.showerror(
                    "Erro", 
                    f"Usuário ou senha incorretos\nTentativas restantes: {attempts_left}"
                )
                logger.warning(f"Tentativa de login falhada para usuário: {username}")
                return False
            
            # Login bem-sucedido
            self._record_login_attempt(username, True)
            
            self.current_user = {
                'id': user_id,
                'username': stored_username,
                'theme': theme_preference or 'light'
            }
            
            # Aplica tema do usuário
            self.theme_manager.set_theme(self.current_user['theme'])
            
            # Remove UI de login
            if self.login_ui and hasattr(self.login_ui, 'frame'):
                self.login_ui.frame.destroy()
            
            # Chama callback de sucesso
            self.on_login_success(self.current_user)
            
            logger.info(f"Login bem-sucedido para usuário: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            messagebox.showerror("Erro", "Erro interno durante o login")
            return False
    
    def register(self, username: str, password: str, confirm_password: str) -> bool:
        """Registra um novo usuário com validações aprimoradas"""
        try:
            # Validação de nome de usuário
            is_valid, error_msg = self._validate_username(username)
            if not is_valid:
                messagebox.showerror("Erro", error_msg)
                return False
            
            # Validação de confirmação de senha
            if password != confirm_password:
                messagebox.showerror("Erro", "As senhas não coincidem")
                return False
            
            # Validação de força da senha
            is_valid, error_msg = self._validate_password_strength(password)
            if not is_valid:
                messagebox.showerror("Erro", error_msg)
                return False
            
            # Verifica se usuário já existe
            if self.db.user_exists(username.strip()):
                messagebox.showerror("Erro", "Nome de usuário já existe")
                return False
            
            # Gera hash seguro da senha
            password_hash, salt = self._hash_password(password)
            
            # Cria usuário no banco de dados
            success = self.db.create_user(username.strip(), password_hash, salt)
            
            if success:
                messagebox.showinfo(
                    "Sucesso", 
                    "Cadastro realizado com sucesso!\nVocê já pode fazer login."
                )
                logger.info(f"Novo usuário registrado: {username}")
                return True
            else:
                messagebox.showerror("Erro", "Erro ao criar usuário")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante registro: {e}")
            messagebox.showerror("Erro", "Erro interno durante o cadastro")
            return False
    
    def logout(self):
        """Desconecta o usuário atual de forma segura"""
        try:
            if self.current_user:
                username = self.current_user.get('username', 'Unknown')
                logger.info(f"Logout do usuário: {username}")
            
            # Limpa dados do usuário atual
            self.current_user = None
            
            # Remove todos os widgets da tela
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Mostra tela de login
            self.show_login_screen()
            
        except Exception as e:
            logger.error(f"Erro durante logout: {e}")
            # Em caso de erro, força limpeza da tela
            try:
                for widget in self.root.winfo_children():
                    widget.destroy()
                self.show_login_screen()
            except:
                pass
    
    def show_login_screen(self):
        """Mostra a tela de login"""
        try:
            self.login_ui = LoginUI(
                root=self.root,
                login_callback=self.login,
                register_callback=self.register,
                theme_manager=self.theme_manager
            )
            logger.info("Tela de login carregada")
            
        except Exception as e:
            logger.error(f"Erro ao carregar tela de login: {e}")
            messagebox.showerror("Erro", "Não foi possível carregar a tela de login")
    
    def get_current_user(self) -> Optional[Dict]:
        """Retorna o usuário atual logado"""
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """Verifica se há um usuário logado"""
        return self.current_user is not None
    
    def change_password(self, old_password: str, new_password: str, confirm_password: str) -> bool:
        """Permite que o usuário altere sua senha"""
        try:
            if not self.current_user:
                messagebox.showerror("Erro", "Nenhum usuário logado")
                return False
            
            # Verifica senha atual
            user_data = self.db.get_user_by_username(self.current_user['username'])
            if not user_data:
                messagebox.showerror("Erro", "Usuário não encontrado")
                return False
            
            _, _, stored_hash, salt, _ = user_data
            
            if not self._verify_password(old_password, stored_hash, salt):
                messagebox.showerror("Erro", "Senha atual incorreta")
                return False
            
            # Valida nova senha
            if new_password != confirm_password:
                messagebox.showerror("Erro", "As senhas não coincidem")
                return False
            
            is_valid, error_msg = self._validate_password_strength(new_password)
            if not is_valid:
                messagebox.showerror("Erro", error_msg)
                return False
            
            # Gera novo hash
            new_hash, new_salt = self._hash_password(new_password)
            
            # Atualiza no banco de dados
            if self.db.update_user_password(self.current_user['id'], new_hash, new_salt):
                messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
                logger.info(f"Senha alterada para usuário: {self.current_user['username']}")
                return True
            else:
                messagebox.showerror("Erro", "Erro ao alterar senha")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            messagebox.showerror("Erro", "Erro interno ao alterar senha")
            return False
        
    def change_username(self, new_username: str) -> bool:
        if not self.current_user:
            messagebox.showerror("Erro", "Nenhum usuário logado")
            return False

        is_valid, error_msg = self._validate_username(new_username)
        if not is_valid:
            messagebox.showerror("Erro", error_msg)
            return False

        if self.db.user_exists(new_username):
            messagebox.showerror("Erro", "Nome de usuário já está em uso")
            return False

        if self.db.update_username(self.current_user['id'], new_username):
            self.current_user['username'] = new_username
            messagebox.showinfo("Sucesso", "Nome de usuário alterado com sucesso")
            logger.info(f"Nome de usuário alterado para: {new_username}")
            return True
        else:
            messagebox.showerror("Erro", "Não foi possível alterar o nome de usuário")
            return False
    def delete_account(self, password: str) -> bool:
        if not self.current_user:
            messagebox.showerror("Erro", "Nenhum usuário logado")
            return False

        user_data = self.db.get_user_by_username(self.current_user['username'])
        if not user_data:
            messagebox.showerror("Erro", "Usuário não encontrado")
            return False

        _, _, password_hash, salt, _ = user_data

        if not self._verify_password(password, password_hash, salt):
            messagebox.showerror("Erro", "Senha incorreta")
            return False

        if self.db.delete_user(self.current_user['id']):
            messagebox.showinfo("Sucesso", "Conta excluída com sucesso")
            logger.info(f"Conta excluída: {self.current_user['username']}")
            self.logout()
            return True
        else:
            messagebox.showerror("Erro", "Erro ao excluir a conta")
            return False
