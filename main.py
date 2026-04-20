import database
from gui import App

if __name__ == "__main__":
    # Aseguramos que la tabla exista antes de abrir la ventana
    database.iniciar_db()
    
    # Arrancamos la aplicación
    app = App()
    app.mainloop()
