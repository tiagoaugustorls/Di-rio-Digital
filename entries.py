from datetime import datetime

class EntryManager:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
    
    def create(self, date, title, content):
        try:
            sql_date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            return self.db.create_entry(self.user_id, sql_date, title, content)
        except ValueError:
            return False
    
    def get_all(self, search_term=None):
        return self.db.get_entries(self.user_id, search_term)
    
    def update(self, entry_id, date, title, content):
        try:
            sql_date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            return self.db.update_entry(entry_id, self.user_id, sql_date, title, content)
        except ValueError:
            return False
    
    def delete(self, entry_id):
        return self.db.delete_entry(entry_id, self.user_id)