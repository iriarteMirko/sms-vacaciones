from .sms_vacaciones import SMS_Vacaciones
from .rutas import *
from ..utils.resource_path import *
from tkinter import messagebox, Entry
from customtkinter import *
import threading
import time


class App_Vacaciones():
    def deshabilitar_botones(self):
        self.boton1.configure(state="disabled")
        self.boton2.configure(state="disabled")
        self.checkbox_hoja.configure(state="disabled")
        self.checkbox_fichero.configure(state="disabled")
        self.boton3.configure(state="disabled")
        self.boton4.configure(state="disabled")
        self.boton_salir.configure(state="disabled")
        self.boton_rutas.configure(state="disabled")
        self.boton_regla.configure(state="disabled")
    
    def habilitar_botones(self):
        self.boton1.configure(state="normal")
        self.boton2.configure(state="normal")
        self.checkbox_hoja.configure(state="normal")
        self.checkbox_fichero.configure(state="normal")
        self.boton3.configure(state="normal")
        self.boton4.configure(state="normal")
        self.boton_salir.configure(state="normal")
        self.boton_rutas.configure(state="normal")
        self.boton_regla.configure(state="normal")
    
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
        self.rutas = verificar_rutas()
        self.reporte = SMS_Vacaciones(self.rutas)
        try:
            inicio = time.time()
            resultados = self.reporte.actualizar_base_celulares()
            fin = time.time()
            self.proceso1 = fin - inicio
            total_deudores = resultados[0]
            total_celulares = resultados[1]
            if total_deudores == total_celulares:
                messagebox.showinfo("INFO", "Todos los socios["+str(total_deudores)+"] cuentan con celulares.")
            else:
                messagebox.showinfo(
                    "INFO", "BASE DE CELULARES ACTUALIZADA!\n"
                    + "\n- CON CELULAR: " + str(total_celulares) 
                    + "\n- SIN CELULAR: " + str(total_deudores-total_celulares)
                    + "\n- TOTAL: " + str(total_deudores))
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton2(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            self.reporte.exportar_deudores()
            fin = time.time()
            self.proceso2 = fin - inicio
            self.inicio_sap = time.time()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
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
            resultados = self.reporte.return_resultados()
            fin = time.time()
            self.proceso3 = fin - inicio
            ld_equipos = resultados[0]
            ld_recaudacion = resultados[1]
            zfir60 = resultados[2]
            messagebox.showinfo(
                "INFO", "REGISTROS VALIDADOS:\n" 
                + "\n- En LD de EQUIPOS: " + str(ld_equipos)
                + "\n- En LD de RECAUDACION: " + str(ld_recaudacion)
                + "\n- Con Deuda Vencida (ZFIR60): " + str(zfir60))
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton4(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            lista_nivel_1, lista_ld = self.reporte.exportar_archivos_txt()
            fin = time.time()
            proceso4 = fin - inicio
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
            
            # Mensajes listos
            messagebox.showinfo(
                "SMS C&CD", "MENSAJES LISTOS:"
                + "\n- LD: " + lista_ld + " destinatarios." 
                + "\n- Nivel 1: " + lista_nivel_1 + " destinatarios."
                + "\n\nTIEMPOS DE EJECUCIÓN:"
                + "\n- Proceso: " + str(self.tiempo_proceso) + " segundos."
                + "\n- SAP: " + str(tiempo_sap) + " segundos."
                + "\n- Total: " + str(self.tiempo_total) + " segundos.")
            os.startfile(self.rutas[5])
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def confirmar_configuracion(self):
        self.rutas = verificar_rutas()
        self.ventana_config.destroy()
    
    def ventana_rutas(self):
        self.ventana_config =CTkToplevel(self.app)
        self.ventana_config.title("Rutas")
        self.ventana_config.resizable(False, False)
        self.ventana_config.grab_set()
        self.ventana_config.focus_set()
        
        titulo1 = CTkLabel(self.ventana_config, text="Seleccionar Archivos", font=("Calibri",12,"bold"))
        titulo1.pack(fill="both", expand=True, padx=10, pady=0)
        
        frame_botones1 = CTkFrame(self.ventana_config)
        frame_botones1.pack_propagate("True")
        frame_botones1.pack(fill="both", expand=True, padx=10, pady=0)
        
        file_dacxanalista = CTkButton(
            frame_botones1, text="DACxANALISTA", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, corner_radius=5, command=lambda: seleccionar_archivo("DACXANALISTA"))
        file_dacxanalista.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        file_celulares = CTkButton(
            frame_botones1, text="Base Celulares", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, corner_radius=5, command=lambda: seleccionar_archivo("CELULARES"))
        file_celulares.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")
        
        titulo2 = CTkLabel(self.ventana_config, text="Seleccionar Carpetas", font=("Calibri",12,"bold"))
        titulo2.pack(fill="both", expand=True, padx=10, pady=0)
        
        frame_botones2 = CTkFrame(self.ventana_config)
        frame_botones2.pack_propagate("True")
        frame_botones2.pack(fill="both", expand=True, padx=10, pady=(0,10))
        
        folder_modelo = CTkButton(
            frame_botones2, text="Carpeta MODELO", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=100, corner_radius=5, command=lambda: seleccionar_carpeta("MODELO"))
        folder_modelo.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        folder_zfir = CTkButton(
            frame_botones2, text="Carpeta ZFIR60", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, corner_radius=5, command=lambda: seleccionar_carpeta("ZFIR"))
        folder_zfir.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")
        
        folder_bases = CTkButton(
            frame_botones2, text="Carpeta BASES", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, corner_radius=5, command=lambda: seleccionar_carpeta("BASES"))
        folder_bases.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        folder_cargas = CTkButton(
            frame_botones2, text="Carpeta CARGAS", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, corner_radius=5, command=lambda: seleccionar_carpeta("CARGAS"))
        folder_cargas.grid(row=1, column=1, padx=(0,10), pady=10, sticky="nsew")
        
        boton_confirmar = CTkButton(
            self.ventana_config, text="Confirmar", font=("Calibri",12), text_color="black",
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515",
            width=100, height=10, corner_radius=5, command=self.confirmar_configuracion)
        boton_confirmar.pack(ipady=2, padx=10, pady=(0,10))
    
    def abrir_regla(self):
        os.startfile(resource_path("src/utils/REGLA.xlsx"))
    
    def crear_app(self):
        self.app = CTk()
        self.app.title("SMS C&CD")
        self.icon_path = resource_path("src/images/icono.ico")
        if os.path.isfile(self.icon_path):
            self.app.iconbitmap(self.icon_path)
        else:
            messagebox.showwarning("ADVERTENCIA", "No se encontró el archivo 'icono.ico' en la ruta: " + self.icon_path)
        self.app.resizable(False, False)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(self.app)
        main_frame.pack_propagate("True")
        main_frame.pack(fill="both", expand=True)
        
        frame_botones = CTkFrame(main_frame)
        frame_botones.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.boton1 = CTkButton(
            frame_botones, text="1: Actualizar Números", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton1.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton2 = CTkButton(
            frame_botones, text="2: Exportar Deudores", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(2))
        self.boton2.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        frame_checkbox = CTkFrame(frame_botones, border_width=2, border_color="black")
        frame_checkbox.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        label_exportar = CTkLabel(frame_checkbox, text="Seleccionar formato SAP:", font=("Calibri",12,"bold"))
        label_exportar.pack(padx=10, pady=5)
        
        self.var_hoja_calculo = BooleanVar()
        self.var_hoja_calculo.set(True)
        self.var_hoja_calculo.trace("w", lambda *args: self.var_fichero_local.set(not self.var_hoja_calculo.get()))
        self.checkbox_hoja = CTkCheckBox(
            frame_checkbox, text="Hoja", font=("Calibri",12), width=5, 
            border_color="#d11515", border_width=2, fg_color="#d11515", 
            hover_color="#d11515", variable=self.var_hoja_calculo)
        self.checkbox_hoja.pack(side="left", padx=(30,10), pady=(0, 10))
        
        self.var_fichero_local = BooleanVar()
        self.var_fichero_local.set(False)
        self.var_fichero_local.trace("w", lambda *args: self.var_hoja_calculo.set(not self.var_fichero_local.get()))
        self.checkbox_fichero = CTkCheckBox(
            frame_checkbox, text="Fichero", font=("Calibri",12), width=5, 
            border_color="#d11515", border_width=2, fg_color="#d11515", 
            hover_color="#d11515", variable=self.var_fichero_local)
        self.checkbox_fichero.pack(side="left", padx=(10,30), pady=(0, 10))
        
        self.boton3 = CTkButton(
            frame_botones, text="3: Preparar Bases", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(3))
        self.boton3.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton4 = CTkButton(
            frame_botones, text="4: Exportar TXT", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(4))
        self.boton4.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton_salir = CTkButton(
            frame_botones, text="Salir", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=100, height=10, corner_radius=5, command=self.app.destroy)
        self.boton_salir.pack(ipady=2, padx=50, pady=10)
        
        frame_output = CTkFrame(main_frame)
        frame_output.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        label_nivel1 = CTkLabel(frame_output, text="Nivel 1: ", font=("Calibri",12))
        label_nivel1.pack(side="left", padx=(25,0), pady=5)
        self.entry_nivel1 = Entry(frame_output, font=("Calibri",12), width=5, state="readonly")
        self.entry_nivel1.pack(side="left", fill="x", expand=True, padx=(0,10), pady=5)
        
        label_ld = CTkLabel(frame_output, text="LD: ", font=("Calibri",12))
        label_ld.pack(side="left", padx=(10,0), pady=5)
        self.entry_ld = Entry(frame_output, font=("Calibri",12), width=5, state="readonly")
        self.entry_ld.pack(side="left", fill="x", expand=True, padx=(0,25), pady=5)
        
        frame_config = CTkFrame(main_frame)
        frame_config.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.boton_rutas = CTkButton(
            frame_config, text="Configurar Rutas", font=("Calibri", 12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=50, height=10, corner_radius=5, command=self.ventana_rutas)
        self.boton_rutas.pack(side="left", fill="both", expand=True, ipady=2, padx=(10,5), pady=10)
        
        self.boton_regla = CTkButton(
            frame_config, text="Abrir Regla", font=("Calibri", 12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=50, height=10, corner_radius=5, command=self.abrir_regla)
        self.boton_regla.pack(side="left", fill="both", expand=True, ipady=2, padx=(5,10), pady=10)
        
        self.progressbar = CTkProgressBar(
            main_frame, mode="indeterminate", orientation="horizontal", 
            progress_color="#d11515", height=7, border_width=0)
        self.progressbar.pack(fill="x", expand=True, padx=10, pady=(10,0))
        
        label_copyrigth = CTkLabel(main_frame, text="© Creado por Mirko Iriarte (C26823)", font=("Calibri",10), text_color="black")
        label_copyrigth.pack(fill="both", expand=True, padx=10, pady=0)
        
        self.app.mainloop()