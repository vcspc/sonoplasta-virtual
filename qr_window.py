import tkinter as tk
from tkinter import ttk
import qrcode
from PIL import Image, ImageTk
import socket

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class QRWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sonoplasta Virtual - QR Code")
        self.window.geometry("400x500")
        
        # Centraliza a janela
        window_width = 400
        window_height = 500
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configura o estilo
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 10))
        
        # Cria e mostra o QR Code
        self.create_widgets()
        
    def create_widgets(self):
        # Obtém o IP e cria a URL
        ip = get_local_ip()
        url = f"https://{ip}:5000"
        
        # Cria o QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Converte para PhotoImage
        self.qr_photo = ImageTk.PhotoImage(qr_image)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sonoplasta Virtual",
            font=("Arial", 16, "bold"),
            style="TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # Instruções
        ttk.Label(
            main_frame,
            text="Escaneie o QR Code para acessar:",
            style="TLabel"
        ).pack(pady=(0, 10))
        
        # QR Code
        ttk.Label(main_frame, image=self.qr_photo).pack(pady=10)
        
        # URL
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(
            url_frame,
            text="URL:",
            style="TLabel"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        url_label = ttk.Label(
            url_frame,
            text=url,
            style="TLabel",
            foreground="blue"
        )
        url_label.pack(side=tk.LEFT)
        
        # Aviso SSL
        ttk.Label(
            main_frame,
            text="Importante:",
            style="TLabel",
            font=("Arial", 12, "bold")
        ).pack(pady=(20, 5))
        
        ttk.Label(
            main_frame,
            text="Aceite o certificado SSL\nquando solicitado pelo navegador",
            style="TLabel"
        ).pack()
        
        # Botão de fechar
        ttk.Button(
            main_frame,
            text="Fechar",
            command=self.window.destroy,
            style="TButton",
            padding="10 5"
        ).pack(pady=20)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    qr_window = QRWindow()
    qr_window.run() 