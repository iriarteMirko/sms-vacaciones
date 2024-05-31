import pandas as pd
import os


class SMS_APOYO():
    def __init__(self, fecha_hoy, ruta_dacx, ruta_celulares, ruta_apoyos, ruta_vacaciones, apoyos_txt):
        self.fecha_hoy = fecha_hoy
        self.ruta_dacx = ruta_dacx
        self.ruta_celulares = ruta_celulares
        self.ruta_apoyos = ruta_apoyos
        self.ruta_vacaciones = ruta_vacaciones
        self.apoyos_txt = apoyos_txt
    
    def depurar_dacx(self,):
        columnas = ['DEUDOR', 'NOMBRE', 'RUC', 'ANALISTA_ACT', 'TIPO_DAC', 'ESTADO']
        no_analistas = ['REGION NORTE', 'REGION SUR', 'WALTER LOPEZ', 'SIN INFORMACION']
        no_estados = ['LIQUIDADO', 'PROCESO DE LIQUIDACIÓN']
        
        df_dacx = pd.read_excel(self.ruta_dacx, sheet_name='Base_NUEVA', usecols=columnas)
        df_dacx = df_dacx.rename(columns={'ANALISTA_ACT': 'ANALISTA', 'TIPO_DAC': 'TIPO'})
        df_dacx = df_dacx[~df_dacx['ANALISTA'].isin(no_analistas)]
        df_dacx = df_dacx[~df_dacx['ESTADO'].isin(no_estados)]
        df_dacx['DEUDOR'] = df_dacx['DEUDOR'].astype('Int64').astype(str)
        df_dacx['RUC'] = df_dacx['RUC'].astype('Int64').astype(str)
        df_dacx.dropna(subset=['DEUDOR'], inplace=True)
        df_dacx.drop_duplicates(subset=['DEUDOR'], inplace=True)
        df_dacx.reset_index(drop=True, inplace=True)
        self.df_dacx = df_dacx
        self.list_analistas = df_dacx['ANALISTA'].unique()
    
    def actualizar_apoyos(self,):
        df_apoyos = pd.read_excel(self.ruta_apoyos, sheet_name='GENERAL', usecols=['DEUDOR', 'APOYO1', 'APOYO2', 'APOYO3'])
        df_apoyos['DEUDOR'] = df_apoyos['DEUDOR'].astype('Int64').astype(str)
        df_apoyos = pd.merge(df_apoyos, self.df_dacx, on='DEUDOR', how='right')
        df_apoyos = df_apoyos[['DEUDOR', 'NOMBRE', 'ANALISTA', 'APOYO1', 'APOYO2', 'APOYO3', 'ESTADO', 'TIPO']]
        df_apoyos.dropna(subset=['DEUDOR'], inplace=True)
        df_apoyos.drop_duplicates(subset=['DEUDOR'], inplace=True)
        df_apoyos.sort_values(by='DEUDOR', inplace=True, ignore_index=True)
        df_apoyos.reset_index(drop=True, inplace=True)
        df_apoyos.to_excel(self.ruta_apoyos, sheet_name='GENERAL', index=False)
        
        with pd.ExcelWriter(self.ruta_apoyos) as writer:
            df_temp = df_apoyos.copy()
            df_apoyos.to_excel(writer, sheet_name='GENERAL', index=False)
            for analista in self.list_analistas:
                df_apoyos = df_temp[df_temp['ANALISTA'] == analista]
                df_apoyos.sort_values(by='DEUDOR', inplace=True, ignore_index=True)
                df_apoyos.reset_index(drop=True, inplace=True)
                df_apoyos.to_excel(writer, sheet_name=analista, index=False)
                print(f'HOJA: {analista} [{df_apoyos.shape[0]} registros]')
    
    def depurar_celulares(self,):
        df_celulares = pd.read_excel(self.ruta_celulares)
        df_celulares['DEUDOR'] = df_celulares['DEUDOR'].astype('Int64').astype(str)
        df_celulares['CELULAR'] = df_celulares['CELULAR'].astype('Int64').astype(str)
        df_celulares = df_celulares[['DEUDOR', 'CELULAR']]
        df_celulares['CELULAR'] = df_celulares[df_celulares['CELULAR'].str.len() == 9]['CELULAR']
        df_celulares.dropna(subset=['CELULAR'], inplace=True)
        df_celulares['CELULAR'] = '51' + df_celulares['CELULAR']
        df_celulares.reset_index(drop=True, inplace=True)
        self.df_celulares = df_celulares
    
    def cruzar_data(self,):
        df_apoyos = pd.read_excel(self.ruta_apoyos, sheet_name='GENERAL', usecols=['DEUDOR', 'ANALISTA', 'APOYO1', 'APOYO2', 'APOYO3'])
        df_apoyos['DEUDOR'] = df_apoyos['DEUDOR'].astype('Int64').astype(str)
        df_cruce = pd.merge(self.df_celulares, df_apoyos, on='DEUDOR', how='left')
        df_cruce.dropna(subset=['ANALISTA'], inplace=True)
        df_cruce.dropna(subset=['CELULAR'], inplace=True)
        df_cruce.reset_index(drop=True, inplace=True)
        self.df_cruce = df_cruce
    
    def obtener_regla(self,):
        df_regla = pd.read_excel(self.ruta_vacaciones, sheet_name='TEXTO')
        self.texto1 = df_regla['TEXTO'][0]
        self.texto2 = df_regla['TEXTO'][1]
        self.texto3 = df_regla['TEXTO'][2]
        self.texto4 = df_regla['TEXTO'][3]
    
    def formato_fecha(self, fecha):
        from datetime import datetime
        return datetime.strptime(fecha, '%d.%m.%Y')
    
    def generar_sms(self,):
        df_vacaciones = pd.read_excel(self.ruta_vacaciones, sheet_name='VACACIONES')
        df_vacaciones.dropna(inplace=True)
        
        dict_analistas = dict(zip(df_vacaciones['ANALISTA'], zip(df_vacaciones['FECHA_SALIDA'], df_vacaciones['FECHA_RETORNO'])))
        
        vacaciones = {}
        
        for analista, fechas in dict_analistas.items():
            if self.formato_fecha(fechas[0]) <= self.formato_fecha(self.fecha_hoy) <= self.formato_fecha(fechas[1]):
                print(f'{analista} de vacaciones desde {fechas[0]} hasta {fechas[1]}')
                vacaciones.update({analista: fechas[1]})
        
        if vacaciones == {}:
            print('NO HAY ANALISTAS DE VACACIONES')
        else:
            analistas = list(vacaciones.keys())
            self.generar_texto(analistas, vacaciones)
            self.exportar_txt()
    
    def generar_texto(self, analistas, vacaciones):
        self.df_cruce = self.df_cruce[self.df_cruce['ANALISTA'].isin(analistas)]
        self.df_cruce['FECHA_RETORNO'] = self.df_cruce['ANALISTA'].map(vacaciones)
        self.df_cruce['APOYO'] = self.df_cruce[['APOYO1', 'APOYO2', 'APOYO3']].apply(
            lambda x: x[0] if x[0] not in (analistas) 
            else (x[1] if x[1] not in (analistas) else x[2]), axis=1)
        self.df_cruce['FECHA_RETORNO'] = self.df_cruce['FECHA_RETORNO'].str.replace('.', '/')
        self.df_cruce.reset_index(drop=True, inplace=True)
        self.df_cruce = self.df_cruce[['CELULAR', 'ANALISTA', 'FECHA_RETORNO','APOYO']]
        self.df_cruce['TEXTO'] = self.df_cruce.apply(lambda row: f'{row["CELULAR"]}{self.texto1}{row["ANALISTA"]}{self.texto2}{row["FECHA_RETORNO"]}{self.texto3}{row["APOYO"]}{self.texto4}', axis=1)
        self.lista_apoyos = self.df_cruce["TEXTO"].to_list()
    
    def exportar_txt(self,):
        with open(self.apoyos_txt, "w") as f:
            for item in self.lista_apoyos:
                f.write("%s\n" % item)
        print(f'Registros validados: [{len(self.lista_apoyos)}]')
        os.startfile(self.apoyos_txt)