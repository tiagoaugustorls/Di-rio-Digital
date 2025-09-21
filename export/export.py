import os
from fpdf import FPDF
from datetime import datetime
from tkinter import filedialog, messagebox
import webbrowser

class ExportManager:
    def __init__(self, entries, username):
        self.entries = entries
        self.username = username

    def format_date(self, date_str):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
            except ValueError:
                continue
        return date_str

    def save_file(self, default_name, extension, filetypes):
        return filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=filetypes,
            initialfile=default_name
        )

    def handle_post_save(self, file_path):
        messagebox.showinfo("Sucesso", f"Arquivo exportado para:\n{file_path}")
        if messagebox.askyesno("Abrir", "Deseja abrir o arquivo?"):
            webbrowser.open(file_path)

    def to_pdf(self):
        if not self.entries:
            messagebox.showwarning("Aviso", "Nenhuma entrada para exportar.")
            return False

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Cabeçalho
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Diário Digital - {self.username}", 0, 1, 'C')
        pdf.ln(10)

        # Conteúdo das entradas
        pdf.set_font("Arial", size=12)
        
        for i, entry in enumerate(self.entries):
            _, date, title, content = entry
            formatted_date = self.format_date(date)
            
            # Verificar se precisa quebrar página
            if pdf.get_y() > 250:
                pdf.add_page()
            
            # Data
            pdf.cell(0, 8, f"Data: {formatted_date}", 0, 1)
            
            # Título
            pdf.cell(0, 8, f"Título: {title}", 0, 1)
            
            # Conteúdo
            pdf.cell(0, 8, f"Conteúdo: {content}", 0, 1)
            
            # Linha separadora (apenas se não for a última entrada)
            if i < len(self.entries) - 1:
                pdf.ln(3)  # Pequeno espaço antes da linha
                pdf.cell(0, 5, "---------------------------", 0, 1)
                pdf.ln(5)  # Espaço após a linha
            else:
                pdf.ln(8)  # Espaço final se for a última entrada

        file_path = self.save_file(f"diario_{self.username}.pdf", ".pdf", [("PDF Files", "*.pdf")])
        if file_path:
            try:
                pdf.output(file_path)
                self.handle_post_save(file_path)
                return True
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar PDF: {str(e)}")
                return False
        return False

    def to_txt(self):
        if not self.entries:
            messagebox.showwarning("Aviso", "Nenhuma entrada para exportar.")
            return False

        content = f"Diário Digital - {self.username}\n{'='*50}\n\n"
        for entry in self.entries:
            _, date, title, text = entry
            formatted_date = self.format_date(date)
            content += f"Data: {formatted_date}\nTítulo: {title}\nConteúdo: {text}\n\n{'-'*50}\n\n"

        file_path = self.save_file(f"diario_{self.username}.txt", ".txt", [("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.handle_post_save(file_path)
            return True
        return False
