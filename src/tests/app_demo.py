from datetime import datetime, timedelta
from tkinter import messagebox
from customtkinter import *
import pandas as pd
import warnings
import threading
import time

warnings.filterwarnings("ignore")

class App():
    def salir(self):
        self.app.destroy()
    
    def deshabilitar_botones(self):
        self.boton1.configure(state="disabled")
    
    def habilitar_botones(self):
        self.boton1.configure(state="normal")
    
    def verificar_thread(self, thread):
        if thread.is_alive():
            self.app.after(1000, self.verificar_thread, thread)
        else:
            self.habilitar_botones()
    
    def iniciar_proceso(self, accion):
        self.deshabilitar_botones()
        if accion == 1:
            thread = threading.Thread(target=self.accion_boton1)
        else:
            return
        thread.start()
        self.app.after(1000, self.verificar_thread, thread)
    
    def accion_boton1(self):
        self.progressbar.start()
        try:
            print("Iniciando proceso 1...")
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def crear_app(self):        
        self.app = CTk()
        self.app.title("C&CD")
        self.app.resizable(True, True)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(self.app)
        main_frame.pack_propagate("True")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        frame_title = CTkFrame(main_frame)
        frame_title.pack(fill="both", expand=True, padx=10, pady=(10,0))
        titulo = CTkLabel(frame_title, text="Cartera General CCD", font=("Calibri",12,"bold"))
        titulo.pack(fill="both", expand=True, padx=10)
        
        # Analista
        frame_buscar = CTkFrame(main_frame)
        frame_buscar.pack(fill="both", expand=True, padx=10, pady=(10,0))
        
        analista = CTkLabel(frame_buscar, text="Analista:", font=("Calibri",12))
        analista.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        
        combo_analista = CTkComboBox(frame_buscar, font=("Calibri",12), width=50)
        combo_analista.pack(side="left", fill="both", expand=True, padx=(0,10), pady=10)
        
        deudor = CTkLabel(frame_buscar, text="Deudor:", font=("Calibri",12))
        deudor.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        
        entry_deudor = CTkEntry(frame_buscar, font=("Calibri",12), width=30)
        entry_deudor.pack(side="left", fill="both", expand=True, padx=(0,10), pady=10)
        
        self.boton1 = CTkButton(frame_buscar, text="Buscar", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=100, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton1.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Inputs
        frame_inputs = CTkFrame(main_frame)
        frame_inputs.pack(fill="both", expand=True, padx=10, pady=(10,0))
        
        entry_deudor = CTkEntry(frame_inputs, font=("Calibri",12), width=100)
        entry_deudor.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        entry_dac = CTkEntry(frame_inputs, font=("Calibri",12), width=150)
        entry_dac.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        combo_estado = CTkComboBox(frame_inputs, font=("Calibri",12), width=100)
        combo_estado.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        
        combo_responsable = CTkComboBox(frame_inputs, font=("Calibri",12), width=100)
        combo_responsable.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        combo_apoyo1 = CTkComboBox(frame_inputs, font=("Calibri",12), width=100)
        combo_apoyo1.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        combo_apoyo2 = CTkComboBox(frame_inputs, font=("Calibri",12), width=100)
        combo_apoyo2.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        
        combo_apoyo3 = CTkComboBox(frame_inputs, font=("Calibri",12), width=100)
        combo_apoyo3.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        
        
        # Botones
        frame_botones = CTkFrame(main_frame)
        frame_botones.pack(fill="both", expand=True, padx=10, pady=(10,0))
        
        self.boton2 = CTkButton(frame_botones, text="Agregar", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=50, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton2.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.boton3 = CTkButton(frame_botones, text="Modificar", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=50, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton3.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.boton4 = CTkButton(frame_botones, text="Eliminar", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=50, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton4.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Tabla
        frame_tabla = CTkFrame(main_frame)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=(10,0))
        
        
        # Progressbar
        self.progressbar = CTkProgressBar(main_frame, mode="indeterminate", orientation="horizontal", progress_color="#d11515", height=7, border_width=0)
        self.progressbar.pack(fill="x", expand=True, padx=10, pady=10)
        
        self.app.mainloop()

def main():
    app = App()
    app.crear_app()

if __name__ == "__main__":
    main()