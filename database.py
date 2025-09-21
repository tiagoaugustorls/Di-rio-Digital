import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_name="diario.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()
        logger.info("DatabaseManager inicializado")

    def create_tables(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    theme TEXT
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

    # Autenticação
    def user_exists(self, username: str) -> bool:
        result = self.connection.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        return result is not None

    def create_user(self, username: str, password_hash: str, salt: str) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, password_hash, salt)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str):
        return self.connection.execute(
            "SELECT id, username, password_hash, salt, theme FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    def update_user_password(self, user_id: int, new_hash: str, new_salt: str) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                    (new_hash, new_salt, user_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar senha: {e}")
            return False

    # CRUD de Entradas
    def get_entries(self, user_id: int, search_term: str = ""):
        query = '''
            SELECT id, title, content, created_at, updated_at, favorite
            FROM entries
            WHERE user_id = ?
        '''
        params = [user_id]

        if search_term:
            query += " AND (title LIKE ? OR content LIKE ?)"
            term = f"%{search_term}%"
            params.extend([term, term])

        query += " ORDER BY created_at DESC"

        return self.connection.execute(query, params).fetchall()


    def create_entry(self, user_id: int, title: str, content: str, date: str = None) -> bool:
        try:
            # Valida o formato da data se fornecido
            if date:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Data inválida fornecida: {date}, usando data atual.")
                    date = None

            with self.connection:
                if date:
                    self.connection.execute(
                        "INSERT INTO entries (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
                        (user_id, title, content, date)
                    )
                else:
                    self.connection.execute(
                        "INSERT INTO entries (user_id, title, content) VALUES (?, ?, ?)",
                        (user_id, title, content)
                    )
            return True
        except Exception as e:
            logger.error(f"Erro ao criar entrada: {e}")
            return False
        
    def get_entry(self, entry_id: int, user_id: int):
         return self.connection.execute(
             "SELECT id, title, content, created_at FROM entries WHERE id = ? AND user_id = ?",
             (entry_id, user_id)
        ).fetchone()   
        
    def update_entry(self, entry_id: int, user_id: int, date: str, title: str, content: str) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    """
                    UPDATE entries
                    SET title = ?, content = ?, created_at = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                    """,
                    (title, content, date, entry_id, user_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar entrada: {e}")
            return False


    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    "DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir entrada: {e}")
            return False
        
    def update_username(self, user_id: int, new_username: str) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    "UPDATE users SET username = ? WHERE id = ?",
                    (new_username, user_id)
                )
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Nome de usuário já existe: {new_username}")
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar nome de usuário: {e}")
            return False
        
    def delete_user(self, user_id: int) -> bool:
        try:
            with self.connection:
                self.connection.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
                self.connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir usuário: {e}")
            return False
        
    def get_entries_by_user_id(self, user_id: int):
        return self.connection.execute(
            "SELECT id, created_at, title, content FROM entries WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,)
        ).fetchall()

    def get_entries_by_date_range(self, user_id: int, start_date: str, end_date: str):
        return self.connection.execute(
            """
            SELECT id, created_at, title, content
            FROM entries
            WHERE user_id = ? AND date(created_at) BETWEEN date(?) AND date(?)
            ORDER BY created_at ASC
            """,
            (user_id, start_date, end_date)
        ).fetchall()

    def get_favorite_entries(self, user_id: int):
        return self.connection.execute(
            "SELECT id, created_at, title, content FROM entries WHERE user_id = ? AND favorite = 1 ORDER BY created_at ASC",
            (user_id,)
        ).fetchall()

    def set_entry_favorite(self, entry_id: int, user_id: int, is_favorite: bool):
        try:
            with self.connection:
                self.connection.execute(
                    "UPDATE entries SET favorite = ? WHERE id = ? AND user_id = ?",
                    (1 if is_favorite else 0, entry_id, user_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar favorito: {e}")
            return False
    def set_favorite(self, entry_id: int, is_favorite: bool) -> bool:
        try:
            with self.connection:
                self.connection.execute(
                    "UPDATE entries SET favorite = ? WHERE id = ?",
                    (1 if is_favorite else 0, entry_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar favorito: {e}")
            return False
