import customtkinter as ctk
import database.db_manager as db_manager
from datetime import datetime

# Configuración visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Gaming PC Manager")
        self.geometry("400x300")
        
        # Nos aseguramos de que la base de datos exista al abrir la app
        db_manager.crear_tablas()
        
        # Etiqueta de título
        self.label = ctk.CTkLabel(self, text="Gestor de Hardware", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        # Botón de prueba
        self.btn_prueba = ctk.CTkButton(self, text="Agregar Componente de Prueba", command=self.guardar_prueba)
        self.btn_prueba.pack(pady=20)

    def guardar_prueba(self):
        # Datos simulados de un componente
        hoy = datetime.now().strftime("%Y-%m-%d")
        db_manager.agregar_componente("AMD Ryzen 5", "CPU", hoy, 24)

if __name__ == "__main__":
    app = App()
    app.mainloop()