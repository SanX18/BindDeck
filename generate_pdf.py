from fpdf import FPDF
import markdown

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 14)
        self.cell(0, 10, "Manual de Usuario: BindDeck ESP32", align="C", ln=True)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generate_pdf():
    with open('manual_completo.md', 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # HTML simple conversion for fpdf2
    html_content = markdown.markdown(md_text)
    
    # In FPDF2, write_html can be used directly
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    try:
        pdf.write_html(html_content)
    except Exception as e:
        print(f"Error parseando HTML: {e}")
        # Fallback to pure text if html fails
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 5, md_text.encode('latin-1', 'replace').decode('latin-1'))
        
    pdf.output("Manual_Usuario_BindDeck.pdf")
    print("PDF generado con éxito: Manual_Usuario_BindDeck.pdf")

if __name__ == '__main__':
    generate_pdf()
