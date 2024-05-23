from resource_path import *
from tkinter import messagebox
import pandas as pd

class Clase_SMS:
    def __init__(self, fecha_hoy, fecha_ayer, fecha_hoy_txt, ruta_zfir60, ruta_modelo, ruta_dacxanalista):
        self.fecha_hoy = fecha_hoy
        self.fecha_ayer = fecha_ayer
        self.fecha_hoy_txt = fecha_hoy_txt
        
        self.ruta_dacxanalista = ruta_dacxanalista + "/Nuevo_DACxANALISTA.xlsx"
        self.ruta_zfir60 = ruta_zfir60 + "/ZFIR60_" + self.fecha_hoy + ".xlsx"
        self.ruta_modelo = ruta_modelo + "/Modelo de Evaluación de Pedidos de Equipos_" + self.fecha_hoy + ".xlsx"
        
        self.ruta_base_celulares = "./BASES/Base_Celulares_CCD.xlsx"
        self.fbl5n_hoja = "./BASES/FBL5N_HOJA.xlsx"
        self.fbl5n_fichero = "./BASES/FBL5N_FICHERO.xlsx"
        self.reporte_recaudacion = "./BASES/Reporte_Recaudacion_" + self.fecha_hoy + ".csv"
        self.deudores = "./BASES/Deudores.xlsx"
        
        self.ld_txt = "./CARGAS/LD " + self.fecha_hoy_txt + ".txt"
        self.nivel_1_txt = "./CARGAS/Nivel 1 " + self.fecha_hoy_txt + ".txt"
        
        self.contador = 0
    
    def abrir_archivo(self, path):
        os.startfile(resource_path(path))
    
    def actualizar_base_celulares(self):
        df_base_celulares = pd.read_excel(self.ruta_base_celulares)
        df_dacxanalista = pd.read_excel(self.ruta_dacxanalista, sheet_name="Base_NUEVA")
        columnas_requeridas = ["DEUDOR", "NOMBRE", "REGION", "ANALISTA_ACT", "TIPO_DAC", "ESTADO"]
        lista_tipo_dac_no_validos = ["PVA", "TARJETERO", "RED", "RECARGA FFVV", "PROVEEDOR", "CROSSBORDER", "CDR", "CACE", "AGENTE TELMEX", "AGENTE TELMEX  / RED", "DAC RURAL"]
        df_dacxanalista = df_dacxanalista[columnas_requeridas]
        df_dacxanalista = df_dacxanalista[~df_dacxanalista["TIPO_DAC"].isin(lista_tipo_dac_no_validos)]
        df_dacxanalista = df_dacxanalista[df_dacxanalista["ESTADO"].isin(["OPERATIVO CON MOVIMIENTO", "OPERATIVO SIN MOVIMIENTO"])]
        df_dacxanalista = df_dacxanalista.merge(df_base_celulares, on="DEUDOR", how="right")
        df_dacxanalista = df_dacxanalista.rename(columns={
            "NOMBRE_x": "NOMBRE",
            "REGION_x": "REGION",
            "ANALISTA_ACT_x": "ANALISTA_ACT",
            "TIPO_DAC_x": "TIPO_DAC",
            "ESTADO_x": "ESTADO"
        })
        df_dacxanalista = df_dacxanalista[columnas_requeridas + ["CELULAR"]]
        df_dacxanalista["CELULAR"] = df_dacxanalista["CELULAR"].astype("Int64")
        df_dacxanalista.dropna(subset=["NOMBRE"], inplace=True)
        df_dacxanalista["CELULAR"] = df_dacxanalista["CELULAR"].fillna(0)
        df_dacxanalista.reset_index(drop=True, inplace=True)
        df_dacxanalista.to_excel(self.ruta_base_celulares, index=False)
        # Preparar base celulares
        df_celulares = df_dacxanalista[["DEUDOR", "NOMBRE", "CELULAR"]]
        total_deudores = df_celulares.shape[0]
        df_celulares = df_celulares[df_celulares["CELULAR"]!=0]
        df_celulares.reset_index(drop=True, inplace=True)
        total_celulares = df_celulares.shape[0]
        # Limpiar nombres
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("á", "a")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("é", "e")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("í", "i")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ó", "o")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ú", "u")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ñ", "n")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Á", "A")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("É", "E")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Í", "I")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ó", "O")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ú", "U")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ñ", "N")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("  ", " ")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("  ", " ")
        if total_deudores == total_celulares:
            messagebox.showinfo("INFO", "Todos los socios["+str(total_deudores)+"] cuentan con celulares.")
        else:
            messagebox.showinfo("INFO", "BASE DE CELULARES ACTUALIZADA!\n"
                                + "\n- CON CELULAR: " + str(total_celulares) 
                                + "\n- SIN CELULAR: " + str(total_deudores-total_celulares)
                                + "\n- TOTAL: " + str(total_deudores))
        self.df_celulares = df_celulares
    
    def generar_texto(self, row):
        if self.contador == 0:
            if row["TIPO"] == "DISPONIBLE":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que su Linea Disponible en RECAUDACION es S/{row["TOTAL"]}, puede realizar su pedido hasta este importe. Creditos y Cobranzas le desea un excelente dia."'
            elif row["TIPO"] == "SOBREGIRO":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que el dia de hoy cuenta con sobregiro en RECAUDACION de S/{row["TOTAL"]}. Para mayor informacion contacte a su analista de C&CD."'
            elif row["TIPO"] == "SIN_LINEA":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que el día de hoy no cuenta con Linea Disponible en RECAUDACION. Para mayor informacion contacte a su analista de C&CD."'
        elif self.contador == 1:
            if row["TIPO"] == "DISPONIBLE":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que su Linea Disponible de Equipos de hoy es S/{row["TOTAL"]}, puede realizar pedidos de equipos valorizados a precio prepago hasta este importe, sujeto a evaluacion crediticia. Creditos y Cobranzas le desea un excelente dia."'
            elif row["TIPO"] == "SOBREGIRO":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que el dia de hoy cuenta con sobregiro en Linea Disponible para compra de Equipos de S/{row["TOTAL"]}. Para mas informacion contacte a su analista. Creditos y Cobranzas le desea un excelente dia."'
            elif row["TIPO"] == "SIN_LINEA":
                return f'51{row["CELULAR"]},Text,"Estimado Socio {row["NOMBRE"]}, le informamos que el dia de hoy no cuenta con Linea Disponible para compra de Equipos. Para mas informacion contacte a su analista. Creditos y Cobranzas le desea un excelente dia."'
        else:
            return f'51{row["CELULAR"]},Text,"Estimado Socio: Le informamos que tiene una deuda vencida de S/{row["Total Vencida"]}, puede pagarla desde la Web y App de bancos principales. Mayor informacion en el Portal de Canales: https://portaldistribuidores.claro.com.pe. Creditos y Cobranzas Distribuidores."'
    
    def exportar_deudores(self):
        df_recaudacion = pd.read_csv(self.reporte_recaudacion, encoding="latin1")
        df_recaudacion = df_recaudacion.drop("USER_ID", axis=1)
        df_recaudacion = df_recaudacion[df_recaudacion["FECHA_RECAUDACION"] == int(self.fecha_ayer)]
        df_recaudacion[["SAP"]].to_excel(self.deudores, index=False)
        df_recaudacion.reset_index(drop=True, inplace=True)
        self.df_recaudacion = df_recaudacion
        self.abrir_archivo(self.deudores)
    
    def preparar_fbl5n_hoja_calculo(self):
        df_fbl5n = pd.read_excel(self.fbl5n_hoja)
        df_fbl5n = df_fbl5n[df_fbl5n["Cuenta"].notna()]
        df_fbl5n = df_fbl5n[df_fbl5n["ACC"] == "PE07"]
        df_fbl5n = df_fbl5n[["Cuenta","Importe en ML"]]
        df_fbl5n["Importe en ML"] = df_fbl5n["Importe en ML"] * -1
        df_fbl5n = df_fbl5n.groupby("Cuenta")["Importe en ML"].sum().reset_index()
        df_fbl5n.set_index("Cuenta", inplace=True)
        self.df_fbl5n = df_fbl5n
    
    def preparar_fbl5n_fichero_local(self):
        df_fbl5n = pd.read_excel(self.fbl5n_fichero)
        df_fbl5n = df_fbl5n.iloc[:, 3:] # Elimina las 3 primeras columnas
        df_fbl5n = df_fbl5n.iloc[7:, :] # Elimina las 7 primeras filas
        df_fbl5n = df_fbl5n.drop(df_fbl5n.index[1]) # Elimina la segunda fila (después de eliminar las 7 primeras)
        df_fbl5n = df_fbl5n.iloc[:-3, :] # Elimina las 3 últimas filas
        df_fbl5n.columns = df_fbl5n.iloc[0] # Nuevo encabezado
        df_fbl5n = df_fbl5n[1:]
        df_fbl5n = df_fbl5n[df_fbl5n["Cuenta"].notna()]
        df_fbl5n = df_fbl5n[df_fbl5n["ACC"] == "PE07"]
        df_fbl5n = df_fbl5n.rename(columns={"     Importe en ML":"Importe en ML"})
        df_fbl5n = df_fbl5n[["Cuenta","Importe en ML"]]
        df_fbl5n["Importe en ML"] = df_fbl5n["Importe en ML"] * -1
        df_fbl5n = df_fbl5n.groupby("Cuenta")["Importe en ML"].sum().reset_index()
        df_fbl5n.set_index("Cuenta", inplace=True)
        self.df_fbl5n = df_fbl5n
    
    def preparar_recaudacion(self):
        self.df_recaudacion["FALTA"] = self.df_recaudacion["SAP"].map(self.df_fbl5n["Importe en ML"])
        self.df_recaudacion["FALTA"].fillna(0, inplace=True)
        self.df_recaudacion["RESTA"] = self.df_recaudacion["LIMITE_CREDITICIO"] - self.df_recaudacion["SALDO_ACTUAL"]
        self.df_recaudacion["TOTAL"] = self.df_recaudacion["FALTA"] + self.df_recaudacion["RESTA"]
        
        df_cruce_recaudacion = self.df_celulares.merge(self.df_recaudacion, left_on="DEUDOR", right_on="SAP", how="left")
        df_cruce_recaudacion = df_cruce_recaudacion[["CELULAR", "NOMBRE", "TOTAL"]]
        df_cruce_recaudacion["TOTAL"].fillna(0, inplace=True)
        df_cruce_recaudacion = df_cruce_recaudacion.sort_values(by="TOTAL", ascending=True)
        df_cruce_recaudacion["TIPO"] = df_cruce_recaudacion["TOTAL"].apply(
            lambda x: "DISPONIBLE" if x > 0 else ("SIN_LINEA" if x == 0 else "SOBREGIRO"))
        df_cruce_recaudacion["TOTAL"] = df_cruce_recaudacion["TOTAL"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_recaudacion.reset_index(drop=True, inplace=True)
        
        df_cruce_recaudacion["TEXTO"] = df_cruce_recaudacion.apply(self.generar_texto, axis=1)
        self.df_cruce_recaudacion = df_cruce_recaudacion
        self.contador += 1
    
    def preparar_modelo(self):
        df_modelo = pd.read_excel(self.ruta_modelo, sheet_name="Base")
        columnas_modelo = ["DEUDOR", "NOMBRE", "LINEA DISPONIBLE EQUIPOS RESTANTE"]
        df_modelo = df_modelo[columnas_modelo]
        
        df_cruce_modelo = self.df_celulares.merge(df_modelo, left_on="DEUDOR", right_on="DEUDOR", how="inner")
        df_cruce_modelo = df_cruce_modelo[["CELULAR", "NOMBRE_x", "LINEA DISPONIBLE EQUIPOS RESTANTE"]]
        df_cruce_modelo = df_cruce_modelo.rename(columns={"NOMBRE_x": "NOMBRE", "LINEA DISPONIBLE EQUIPOS RESTANTE": "TOTAL"})
        df_cruce_modelo = df_cruce_modelo.sort_values(by="TOTAL", ascending=True)
        df_cruce_modelo["TIPO"] = df_cruce_modelo["TOTAL"].apply(
            lambda x: "DISPONIBLE" if x > 0 else ("SIN_LINEA" if x == 0 else "SOBREGIRO"))
        df_cruce_modelo["TOTAL"] = df_cruce_modelo["TOTAL"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_modelo.reset_index(drop=True, inplace=True)
        
        df_cruce_modelo["TEXTO"] = df_cruce_modelo.apply(self.generar_texto, axis=1)
        self.df_cruce_modelo = df_cruce_modelo
        self.contador += 1
    
    def preparar_zfir60(self):
        df_zfir60 = pd.read_excel(self.ruta_zfir60, sheet_name="Sheet1")
        df_zfir60 = df_zfir60[["Cliente Pa", "Total Vencida"]]
        df_zfir60["Total Vencida"] = df_zfir60["Total Vencida"].clip(lower=0)
        df_zfir60 = df_zfir60.groupby("Cliente Pa")["Total Vencida"].sum().reset_index()
        
        df_cruce_zfir60 = self.df_celulares.merge(df_zfir60, left_on="DEUDOR", right_on="Cliente Pa", how="left")
        df_cruce_zfir60 = df_cruce_zfir60[["CELULAR", "Total Vencida"]]
        df_cruce_zfir60 = df_cruce_zfir60[df_cruce_zfir60["Total Vencida"] != 0]
        df_cruce_zfir60 = df_cruce_zfir60.sort_values(by="Total Vencida", ascending=False)
        df_cruce_zfir60["Total Vencida"] = df_cruce_zfir60["Total Vencida"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_zfir60.reset_index(drop=True, inplace=True)
        
        df_cruce_zfir60["TEXTO"] = df_cruce_zfir60.apply(self.generar_texto, axis=1)
        self.df_cruce_zfir60 = df_cruce_zfir60
        self.contador = 0
        
        messagebox.showinfo("INFO", "REGISTROS VALIDADOS:\n" 
                            + "\n- En LD de EQUIPOS: " + str(self.df_cruce_modelo.shape[0])
                            + "\n- En LD de RECAUDACION: " + str(self.df_cruce_recaudacion.shape[0])
                            + "\n- Con Deuda Vencida (ZFIR60): " + str(df_cruce_zfir60.shape[0]))
    
    def exportar_archivos_txt(self):
        # Nivel 1
        lista_nivel_1 = self.df_cruce_zfir60["TEXTO"].to_list()
        with open(self.nivel_1_txt, "w") as f:
            for item in lista_nivel_1:
                f.write("%s\n" % item)
        # LD
        df_ld = pd.concat([self.df_cruce_modelo, self.df_cruce_recaudacion], ignore_index=True)
        lista_ld = df_ld["TEXTO"].to_list()
        with open(self.ld_txt, "w") as f:
            for item in lista_ld:
                f.write("%s\n" % item)
        # Resultados
        return str(len(lista_nivel_1)), str(len(lista_ld))