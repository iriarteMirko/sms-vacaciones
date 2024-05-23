from clase_sms_ccd import Clase_SMS
from datetime import datetime, timedelta
from tkinter import messagebox
from customtkinter import *
from resource_path import *
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
        self.boton2.configure(state="disabled")
        self.checkbox_hoja.configure(state="disabled")
        self.checkbox_fichero.configure(state="disabled")
        self.boton3.configure(state="disabled")
        self.boton4.configure(state="disabled")
        self.boton_salir.configure(state="disabled")
    
    def habilitar_botones(self):
        self.boton1.configure(state="normal")
        self.boton2.configure(state="normal")
        self.checkbox_hoja.configure(state="normal")
        self.checkbox_fichero.configure(state="normal")
        self.boton3.configure(state="normal")
        self.boton4.configure(state="normal")
        self.boton_salir.configure(state="normal")
    
    def verificar_thread(self, thread):
        if thread.is_alive():
            self.app.after(1000, self.verificar_thread, thread)
        else:
            self.habilitar_botones()
    
    def iniciar_proceso(self, accion):
        self.deshabilitar_botones()
        if accion == 1:
            thread = threading.Thread(target=self.accion_boton1)
        elif accion == 2:
            thread = threading.Thread(target=self.accion_boton2)
        elif accion == 3:
            thread = threading.Thread(target=self.accion_boton3)
        elif accion == 4:
            thread = threading.Thread(target=self.accion_boton4)
        else:
            return
        thread.start()
        self.app.after(1000, self.verificar_thread, thread)
    
    def accion_boton1(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            self.reporte.actualizar_base_celulares()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            fin = time.time()
            self.proceso1 = fin - inicio
            self.progressbar.stop()
    
    def accion_boton2(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            self.reporte.exportar_deudores()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            fin = time.time()
            self.proceso2 = fin - inicio
            self.progressbar.stop()
            self.inicio_sap = time.time()
    
    def accion_boton3(self):
        self.fin_sap = time.time()
        self.progressbar.start()
        try:
            inicio = time.time()
            if self.var_hoja_calculo.get() == True:
                self.reporte.preparar_fbl5n_hoja_calculo()
            else:
                self.reporte.preparar_fbl5n_fichero_local()
            self.reporte.preparar_recaudacion()
            self.reporte.preparar_modelo()
            self.reporte.preparar_zfir60()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            fin = time.time()
            self.proceso3 = fin - inicio
            self.progressbar.stop()
    
    def accion_boton4(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            lista_nivel_1, lista_ld = self.reporte.exportar_archivos_txt()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            fin = time.time()
            proceso4 = fin - inicio
            self.progressbar.stop()
            self.tiempo_proceso = round((self.proceso1 + self.proceso2 + self.proceso3 + proceso4),2)
            tiempo_sap = round((self.fin_sap - self.inicio_sap),2)
            self.tiempo_total = round((self.tiempo_proceso + tiempo_sap),2)
            
            self.entry_nivel1.configure(state="normal")
            self.entry_nivel1.delete(0, "end")
            self.entry_nivel1.insert(0, lista_nivel_1)
            self.entry_nivel1.configure(state="readonly")
            self.entry_ld.configure(state="normal")
            self.entry_ld.delete(0, "end")
            self.entry_ld.insert(0, lista_ld)
            self.entry_ld.configure(state="readonly")
            
            self.entry_proceso.configure(state="normal")
            self.entry_proceso.delete(0, "end")
            self.entry_proceso.insert(0, str(self.tiempo_proceso) + " s")
            self.entry_proceso.configure(state="readonly")
            self.entry_total.configure(state="normal")
            self.entry_total.delete(0, "end")
            self.entry_total.insert(0, str(self.tiempo_total) + " s")
            self.entry_total.configure(state="readonly")
            # Mensajes listos
            messagebox.showinfo("SMS C&CD", "MENSAJES LISTOS:"
                                + "\n- LD: " + lista_ld + " destinatarios." 
                                + "\n- Nivel 1: " + lista_nivel_1 + " destinatarios."
                                + "\n\nTIEMPOS DE EJECUCIÓN:"
                                + "\n- Proceso: " + str(self.tiempo_proceso) + " segundos."
                                + "\n- SAP: " + str(tiempo_sap) + " segundos."
                                + "\n- Total: " + str(self.tiempo_total) + " segundos.")
            os.startfile(resource_path("./CARGAS/"))
    
    def generar_reporte(self):
        try:
            excel_rutas = resource_path("./RUTAS.xlsx")
            df_rutas = pd.read_excel(excel_rutas)
            fecha_hoy = datetime.today()
            fecha_ayer = fecha_hoy - timedelta(days=1)
            fecha_ayer = fecha_ayer.strftime("%Y%m%d")
            fecha_hoy = datetime.today().strftime("%Y%m%d")
            fecha_hoy_txt = datetime.today().strftime("%d.%m.%Y")
            ruta_zfir60 = df_rutas["RUTA"][0]
            ruta_modelo = df_rutas["RUTA"][1]
            ruta_dacxanalista = df_rutas["RUTA"][2]
            self.reporte = Clase_SMS(fecha_hoy, fecha_ayer, fecha_hoy_txt, ruta_zfir60, ruta_modelo, ruta_dacxanalista)
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e)
                                + "\n\nAsegúrese de tener el archivo 'RUTAS.xlsx' en la misma carpeta que el ejecutable.")
            self.app.destroy()
    
    def crear_app(self):        
        self.app = CTk()
        self.app.title("SMS C&CD")
        icon_path = resource_path("./images/icono.ico")
        if os.path.isfile(icon_path):
            self.app.iconbitmap(icon_path)
        else:
            messagebox.showwarning("ADVERTENCIA", "No se encontró el archivo 'icono.ico' en la ruta: " + icon_path)
        self.app.resizable(False, False)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(self.app)
        main_frame.pack_propagate("True")
        main_frame.pack(fill="both", expand=True)
        
        frame_title = CTkFrame(main_frame)
        frame_title.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        titulo = CTkLabel(frame_title, text="SMS C&CD", font=("Calibri",15,"bold"))
        titulo.pack(fill="both", expand=True, ipady=5, padx=10)
        
        frame_botones = CTkFrame(main_frame)
        frame_botones.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.boton1 = CTkButton(frame_botones, text="Actualizar Números", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=200, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton1.pack(fill="both", expand=True, ipady=5, padx=10, pady=(10, 0))
        
        self.boton2 = CTkButton(frame_botones, text="Exportar Deudores", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=200, corner_radius=5, command=lambda: self.iniciar_proceso(2))
        self.boton2.pack(fill="both", expand=True, ipady=5, padx=10, pady=(10, 0))
        
        frame_checkbox = CTkFrame(frame_botones, border_width=2, border_color="black")
        frame_checkbox.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        label_exportar = CTkLabel(frame_checkbox, text="Seleccionar formato SAP:", font=("Calibri",12,"bold"))
        label_exportar.pack(padx=10, pady=5)
        
        self.var_hoja_calculo = BooleanVar()
        self.var_hoja_calculo.set(True)
        self.var_hoja_calculo.trace("w", lambda *args: self.var_fichero_local.set(not self.var_hoja_calculo.get()))
        self.checkbox_hoja = CTkCheckBox(frame_checkbox, text="Hoja", font=("Calibri",12), width=5,
                                        border_color="#d11515", border_width=2, fg_color="#d11515", 
                                        hover_color="#d11515", variable=self.var_hoja_calculo)
        self.checkbox_hoja.pack(side="left", padx=(30,10), pady=(0, 10))
        
        self.var_fichero_local = BooleanVar()
        self.var_fichero_local.set(False)
        self.var_fichero_local.trace("w", lambda *args: self.var_hoja_calculo.set(not self.var_fichero_local.get()))
        self.checkbox_fichero = CTkCheckBox(frame_checkbox, text="Fichero", font=("Calibri",12), width=5,
                                            border_color="#d11515", border_width=2, fg_color="#d11515", 
                                            hover_color="#d11515", variable=self.var_fichero_local)
        self.checkbox_fichero.pack(side="left", padx=(10,30), pady=(0, 10))
        
        self.boton3 = CTkButton(frame_botones, text="Preparar Bases", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=200, corner_radius=5, command=lambda: self.iniciar_proceso(3))
        self.boton3.pack(fill="both", expand=True, ipady=5, padx=10, pady=(10, 0))
        
        self.boton4 = CTkButton(frame_botones, text="Exportar TXT", font=("Calibri",12), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                width=200, corner_radius=5, command=lambda: self.iniciar_proceso(4))
        self.boton4.pack(fill="both", expand=True, ipady=5, padx=10, pady=10)
        
        frame_output = CTkFrame(main_frame)
        frame_output.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        frame_detalles = CTkFrame(frame_output, bg_color="transparent", fg_color="transparent")
        frame_detalles.pack(side="left", fill="both", expand=True, padx=(25,5))
        
        label_detalles = CTkLabel(frame_detalles, text=" - Detalles - ", font=("Calibri",12,"bold"))
        label_detalles.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")
        
        label_nivel1 = CTkLabel(frame_detalles, text="Nivel 1: ", font=("Calibri",12))
        label_nivel1.grid(row=1, column=0, padx=0, pady=0, sticky="e")
        self.entry_nivel1 = CTkEntry(frame_detalles, font=("Calibri",12), width=30, height=5, border_width=0, state="readonly")
        self.entry_nivel1.grid(row=1, column=1, padx=0, pady=0, sticky="w")
        
        label_ld = CTkLabel(frame_detalles, text="LD: ", font=("Calibri",12))
        label_ld.grid(row=2, column=0, padx=0, pady=(0,5), sticky="e")
        self.entry_ld = CTkEntry(frame_detalles, font=("Calibri",12), width=30, height=5, border_width=0, state="readonly")
        self.entry_ld.grid(row=2, column=1, padx=0, pady=(0,5), sticky="w")
        
        frame_tiempos = CTkFrame(frame_output, bg_color="transparent", fg_color="transparent")
        frame_tiempos.pack(side="right", fill="both", expand=True, padx=(5,25))
        
        label_tiempos = CTkLabel(frame_tiempos, text=" - Tiempos - ", font=("Calibri",12,"bold"))
        label_tiempos.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")
        
        label_proceso = CTkLabel(frame_tiempos, text="Proceso: ", font=("Calibri",12))
        label_proceso.grid(row=1, column=0, padx=0, pady=0, sticky="e")
        self.entry_proceso = CTkEntry(frame_tiempos, font=("Calibri",12), width=43, height=5, border_width=0, state="readonly")
        self.entry_proceso.grid(row=1, column=1, padx=0, pady=0, sticky="w")
        
        label_total = CTkLabel(frame_tiempos, text="Total: ", font=("Calibri",12))
        label_total.grid(row=2, column=0, padx=0, pady=(0,5), sticky="e")
        self.entry_total = CTkEntry(frame_tiempos, font=("Calibri",12), width=43, height=5, border_width=0, state="readonly")
        self.entry_total.grid(row=2, column=1, padx=0, pady=(0,5), sticky="w")
        
        frame_salir = CTkFrame(main_frame)
        frame_salir.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.boton_salir = CTkButton(frame_salir, text="Salir", font=("Calibri",12), text_color="black", 
                                    fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
                                    width=50, height=10, corner_radius=5, command=self.salir)
        self.boton_salir.pack(padx=50, pady=5)
        
        self.progressbar = CTkProgressBar(main_frame, mode="indeterminate", orientation="horizontal", 
                                            progress_color="#d11515", height=7, border_width=0)
        self.progressbar.pack(fill="x", expand=True, padx=10, pady=10)
        
        self.app.mainloop()

def main():
    app = App()
    app.generar_reporte()
    app.crear_app()

if __name__ == "__main__":
    main()