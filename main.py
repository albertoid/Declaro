#Manejo web
from flask import Flask
from flask import render_template
from flask import request
from flask import Markup

# default inicial
user=''
password=''
captcha1=''
captcha2=''


# flask app
app=Flask(__name__)

# main app
@app.route("/", methods=['POST', 'GET'])
def main():
#-----------------------------------Librerias---------------------------------------------------------
    if request.method=='POST':
        user=request.form['s_user']
        password=request.form['s_password']
        captcha1=request.form['s_captcha1']

        #Scraping
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import Select
        import selenium.webdriver.support.ui as ui
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support import expected_conditions as EC

        #Manejo de Archivos
        import io
        import os
        from os import listdir, remove
        from os.path import isfile, join
        import pathlib
        from datetime import datetime


        # Bases de datos
        from pymongo import MongoClient
        import pandas as pd
        import pymongo
        import xmltodict

        #Despliegue Gráfico
        #%pylab inline
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        from PIL import Image 

        #Varios
        import time
        import base64
        from datetime import datetime
        import warnings
        warnings.filterwarnings("ignore")
        from tqdm import tqdm_notebook as tqdm

        max_attempts=7


        #------------------------------------ FUNCIONES -----------------------------------------------------------

        #-------------------------------------------lookuptag--------------------------------------------------------

        #Descripción General: Funcion para buscar un texto específico en etiquetas similares
        #Recibe: Lista de elementos (list_elements) que puede venir de un driver.find_elements...
        #Recibe: Texto para comparar (selected_string) que debe ser igual al texto que se esta buscando
        #Recibe: Despligue (verbose) para ver todos los elementos de la lista. False por default
        #Regresa: Elemento seleccionado o en caso de no encontrar nada None

        def lookuptag(list_elements,selected_string,verbose=False):
            if verbose == True:
                for i,e in enumerate(list_elements):
                    print(i,":", e.text)
            else:
                pass

            for i,e in enumerate(list_elements):
                if e.text == selected_string:
                    return e
                else:
                    pass
            return None

        #-------------------------------------------loadok-----------------------------------------------------------

        #Descripcion General: Funcion para asegurar la carga de una página despues de una secuencia
        #Recibe: elemento de Selenium
        #Recibe: tiempo en segundos de cada refrescado (refresh)
        #Recibe: Maximo número de intentos para varificar que el elemento se cargo (max_tries)
        #Recibe: Una etiqueta para identificar el elemento de prueba (stage) por default ""
        #Recibe: Despliegue (verbose) para verificar el estado de la validación
        #Regresa: None

        def loadok(element, refresh=1, max_tries=3, stage="",verbose=False):
            loaded=False
            tries=0

            while 1:
                try:
                    element
                    loaded=True
                    if verbose == True:
                        return print(stage+"loaded [ok]")
                    else:
                        return None
                except:
                    tries = tries + 1
                    loaded=False
                    time.sleep(refresh*tries)

                    if tries >= max_tries:
                        if verbose == True:
                            return print("Número de intentos superado. La página no ha cargado correctamente")
                        else:
                            return None

        #-------------------------------------------focus------------------------------------------------------------
        def focus(driver):
            loaded=False
            wait=1
            while loaded==False:
                try:
                    driver.switch_to_window(driver.window_handles[0])
                    loaded=True
                except:
                    time.sleep(wait)
                    wait+=1
                    if wait==max_attempts:
                        print("Error en carga de pagina")

        #-------------------------------------------clean_folder----------------------------------------------------

        #Descripción General: Funcion para borrar archivos de la carpeta temporal
        #Recibe: ruta (path) por default una carpeta temp dentro de la ruta actual
        #Recibe: lista de archivos (fl)
        #Regresa: None

        def clean_folder(fl, path='./temp/'):
            for i in fl:
                remove(path+i)

            return None

        #-------------------------------------------predict_encoding--------------------------------------------------

        #Descrición general: Predice la codificación de un archivo dado
        #Recibe: Ruta del Archivo (file_path)
        #Recibe: Numero de de lineas para la predicción (n_lines) por default 20. Entre mas líneas se mejora la probabilidad de una mejor preduccion
        #Entrega: Predicción de codificación en un str

        def predict_encoding(file_path, n_lines=20):
            '''Predict a file's encoding using chardet'''
            import chardet

            # Open the file as binary data
            with open(file_path, 'rb') as f:
                # Join binary lines for specified number of lines
                rawdata = b''.join([f.readline() for _ in range(n_lines)])

            return chardet.detect(rawdata)['encoding']

        #---------------------------------------------error_captcha----------------------------------------------------

        #Descripcion General: Verifica si no se lanza la ventana de error de captcha
        #Recibe: Nada
        #Regresa: Verdader si la ventana de error se muestra, Falso si no hay error
        def error_captcha():
            try:
                list_error_captcha=driver.find_elements_by_tag_name('div')
                error_captcha=lookuptag(list_error_captcha,' Captcha no válido')
                return True
            except:
                 return False

        #----------------------------------------ventana_emergente_conexion------------------------------------------

        #En caso de problemas de conexion sale un menu emergente que se puede buscar entre cada cambio de pagina
        def ventana_emergente_conexion():
            try:
                button_elements=driver.find_elements_by_tag_name('button')
                btn_problemas=lookuptag(button_elements,'Cerrar')
                btn_problemas.click()
            except:
                pass

        #-----------------------------------ventana_emergente_nueva_forma----------------------------------------------

        def ventana_emergente_nueva_forma():
            try:
                btn_iniciar_nueva_forma=driver.find_element_by_id('MainContent_wucDeclaracionesTemporales_Btn_NuevaDeclaTemporal')
                btn_iniciar_nueva_forma.click()
            except:
                try:
                    btn_iniciar_nueva_forma=driver.find_element_by_id('MainContent_wucDeclaracionesTemporales_Btn_ReemplazarDeclaTemporal')
                    btn_iniciar_nueva_forma.click()
                except:
                    pass
        #--------------------------------------fechas_ini_fin-----------------------------------------------------------
        def fechas_ini_fin():
            mes= 12 if time.localtime().tm_mon == 1 else time.localtime().tm_mon - 1
            mes_str = '0'+str(mes) if mes<10 else str(mes)

            anno = time.localtime().tm_year
            if mes in [1,3,5,7,8,10,12]:
                diafin=31
            elif mes in [4,6,9,11]:
                diafin=30
            else:
                if anno%4==0:
                    diafin=29
                else:
                    diafin=28
            fecha_ini="'01/"+mes_str+"/"+str(int(anno))+"'"
            fecha_fin="'"+str(diafin)+"/"+mes_str+"/"+str(int(anno))+"'"
            return [fecha_ini,fecha_fin,anno,mes,diafin]

        #------------------------------------Inicializacion de Variables ------------------------------------

        #Enviar Captcha y solicitar rfc, pwd y cap
        #str_rfc=input("Ingresa tu RFC:")
        #str_pwd=input("Ingresa tu contraseña:")
        #str_rfc='IADA810218HG5'
        #str_pwd='DaSa0520'
        #rfc_usuario = str_rfc
        #id_usuario = 'albertoid'

        #Inicialización de valores para la declaracion, que seran calculados por el módulo de calculo

        #Variables para la declaracion ISR
        ingresos='0'
        gastos='0'
        anterior='0'
        retenido='0'

        #Ingreso de valores IVA
        actividades_gravadas_16='0'
        actividades_gravadas_0='0'
        actividades_excentas='0'
        iva_acreditable_del_periodo='0'
        iva_retenido='0'


        #------------------------- Conexion a la base de datos de usuarios --------------------------------------
        pwd=open('pw.txt','r')
        pw=pwd.read()
        cliente=MongoClient('mongodb+srv://api:'+pw.split('\n')[0]+'@clusterdeclaro-tya5c.mongodb.net/test?retryWrites=true&w=majority')
        db_api=cliente.api
        coleccion_usuarios=db_api.usuarios
        #-------------------------------------## Login y registro de usuarios ##--------------------------------------

        ok=0
        while ok == False:
            opcion=input('Ingresa 1 para Login, 2 para Nuevo Usuario: ')

            if opcion == '1':
                ok2=False
                tries=0
                while ok2 == False:
                    id_usuario=input('Ingresa tu usuario: ')
                    check=list(coleccion_usuarios.find({'usuario':{'$eq': id_usuario}}))

                    if len(check)== 1:
                        password=input('Ingresa tu contaseña: ')
                        if check[0]['password']==password:
                            print('Bienvenido ',id_usuario)
                            str_rfc=check[0]['rfc']
                            str_pwd=check[0]['contraseña_sat']
                            usr= check[0]['usuario']
                            ok2=True
                        else:
                            print('Contraseña Incorrecta')
                            tries = tries + 1
                            if tries >3:
                                print('Demasiados intentos incorrectos')
                                break    
                    else:
                        print('Nombre de usuario incorrecto, intente otra vez')
                        tries = tries + 1
                        if tries >3:
                            print('Demasiados intentos incorrectos')
                            break 
                ok=True
            elif opcion == '2':
                nuevo_usuario=input('Escribe tu nuevo nombre de usuario')
                #Revisar si el usuario existe
                nueva_contraseña=input('Escribe tu nueva contraseña')
                nuevo_rfc=input('Escribe tu rfc')
                nueva_contraseña_sat=input('Escribe tu contraseña del SAT')

                nuevo_registro={'usuario': nuevo_usuario, 'password': nueva_contraseña,
                                'rfc':nuevo_rfc, 'contraseña_sat':nueva_contraseña_sat}

                coleccion_usuarios.insert_one(nuevo_registro);
                ok=True
            else:
                print('Opción no valida, intenta otra vez')


        #-----------------------------------------## API - Facturas  ##------------------------------------------#
        loaded =False
        while loaded==False:
            if str_rfc=='':
                print('Credenciales inexistentes')
                break
            else:
                pass
            try:
                #Deteccion de la raiz de los archivos
                directorio=pathlib.Path().absolute()
                filespath=str(directorio)+'/temp'

                #Seleccion de carpeta temporal para descarga de archivow
                chrome_options = webdriver.ChromeOptions()
                prefs = {'download.default_directory' : filespath}
                chrome_options.add_experimental_option('prefs', prefs)
                options = webdriver.ChromeOptions() 
                options.add_argument("download.default_directory="+filespath)

                #Inicializacion de driver de Selenium
                driver = webdriver.Chrome(chrome_options=chrome_options)

                #Inicializar Navegador y entrar a pagina web
                driver.get("https://portalcfdi.facturaelectronica.sat.gob.mx/")

                time.sleep(2)

                #Espera dináminca de la carga del captcha
                loadok(driver.find_elements_by_tag_name("img"))

                #Obtener Captcha
                images=driver.find_elements_by_tag_name("img")
                captcha = images[1].get_attribute('src')[23:]

                #Integrar Captcha
                image_decoded = base64.b64decode(str(captcha))       
                image = Image.open(io.BytesIO(image_decoded))

                #Mostrar captcha en jupiter notebook
                imgplot = plt.imshow(image)
                plt.show()

                #Guardar Captcha

                #fileName = 'captcha.jpeg'
                #imagePath = ("captcha.jpeg")
                #image.save(imagePath, 'jpeg')

                str_cap=input("Ingresa el Captcha:")

                loaded=True
            except:
                driver.close()
                loaded=False

        #---------------------------------------Ingreso de credenciales------------------------------------------
        loaded=False
        wait=1
        while loaded==False:
            try:
                rfc = driver.find_element_by_id("rfc")
                rfc.clear()
                rfc.send_keys(str_rfc)

                pwd=driver.find_element_by_id("password")
                pwd.clear()
                pwd.send_keys(str_pwd)

                cap=driver.find_element_by_id("userCaptcha")
                cap.clear()
                cap.send_keys(str_cap)

                btn_Login=driver.find_element_by_id("submit")
                btn_Login.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                #focus(driver)
                print('Waiting in Login... ',wait)
                if wait==max_attempts:
                    break

        #--------------------------Ingreso a consulta de Facturas Recibidas---------------------------------------
        loaded=False
        wait=1
        while loaded==False:
            try:
                #Click en Consultar Facturas Recibidas
                #loadok(driver.find_element_by_link_text("Consultar Facturas Recibidas"))
                lnk_Emitidas= driver.find_element_by_link_text("Consultar Facturas Recibidas")
                lnk_Emitidas.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                #focus(driver)
                print('Waiting in Ingreso a Consulta Facturas Recibidas... ',wait)
                if wait==max_attempts:
                    break
        #--------------------------Parametros de Consulta de Facturas Recibidas---------------------------------------            
        loaded=False
        wait=1
        while loaded==False:
            try:
                #Selección del tipo de busqueda de facturas "Por fecha"
                #loadok(driver.find_element_by_id("ctl00_MainContent_RdoFechas"))
                sel_fecha_emision=driver.find_element_by_id("ctl00_MainContent_RdoFechas")
                sel_fecha_emision.click()
                time.sleep(1)

                #Selección del mes
                mes= 12 if time.localtime().tm_mon == 1 else time.localtime().tm_mon - 1

                #loadok(Select(driver.find_element_by_id('ctl00_MainContent_CldFecha_DdlMes')))
                sel_mes = Select(driver.find_element_by_id('ctl00_MainContent_CldFecha_DdlMes'))
                sel_mes.select_by_value(str(mes))

                #Click en el boton de búsqueda de las facturas del mes
                #loadok(driver.find_element_by_name("ctl00$MainContent$BtnBusqueda"))
                btn_BuscarCFDI=driver.find_element_by_name("ctl00$MainContent$BtnBusqueda")
                btn_BuscarCFDI.click()

                #Seleccion del Año
                #anno= time.localtime().tm_year - 1 if time.localtime().tm_mon == 1 else time.localtime().tm_year
                ## Scraping pendiente de la seleccion del año ------------------ !!!!

                loaded=True

            except:
                x=input()
                loaded=False
                time.sleep(wait)
                wait=wait+1
                #focus(driver)
                print('Waiting in Parametros de Consulta Facturas Recibidas... ',wait)
                if wait==max_attempts:
                    break


        #------------------------------Descarga de todas las facturas en las páginas disponibles----------------------
        time.sleep(2)
        fallos=[]
        btns_Descarga=[]
        btns_Descarga = driver.find_elements_by_id("BtnDescarga")

        for j in tqdm(range(len(btns_Descarga)),'Facturas'):
            try:
                driver.execute_script(btns_Descarga[j].get_attribute('onclick')) #Ejecuta el metodo de Java Script para la descarga
                #Verificacion de descarga --- OPTIMIZACION PENDIENTE TIP: Comparar nombre de archivo con el desplegado en la pagina
                time.sleep(3)
                #loadok(driver.switch_to_window(driver.window_handles[1]),stage=str(j),verbose=False) #Mueve el foco a la ventana de descarga
                driver.switch_to_window(driver.window_handles[1]) #Mueve el foco a la ventana de descarga
                driver.close()  #Cierra pagina de descarga
                driver.switch_to_window(driver.window_handles[0])    
            except:
                fallos.append(j) 
        #-------------------------------------Regreso a Inicio------------------------------------
        loaded=False
        wait=1
        while loaded==False:
            try:
                #loadok(driver.find_elements_by_tag_name('a'))
                driver.execute_script("window.scrollTo(0, 0);")
                btn_Inicio=lookuptag(driver.find_elements_by_tag_name('a'), 'Inicio')
                btn_Inicio.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                #focus(driver)
                print('Waiting in Regreso a Inicio... ',wait)
                if wait==max_attempts:
                    break
        #---------------------Cambio a Facturas Emitidas------------------------------------   
        loaded=False
        wait=1
        while loaded==False:
            try:
                #Click en Consultar Facturas Recibidas
                #loadok(driver.find_element_by_link_text("Consultar Facturas Emitidas"))
                lnk_Emitidas= driver.find_element_by_link_text("Consultar Facturas Emitidas")
                lnk_Emitidas.click()

                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                focus(driver)
                print('Waiting in Cambio a Facturas Emitidas... ',wait)
                if wait==max_attempts:
                    break
        #---------------------Ingreso de Parametros de de Facturas Emitidas------------------------------------               
        loaded=False
        wait=1
        while loaded==False:
            try:
                #Selección del tipo de busqueda de facturas "Por fecha"
                #loadok(driver.find_element_by_id("ctl00_MainContent_RdoFechas"))
                sel_fecha_emision=driver.find_element_by_id("ctl00_MainContent_RdoFechas")
                sel_fecha_emision.click()
                #Selección de fechas inicial y final
                f=fechas_ini_fin()
                fecha_inicial=f[0]
                driver.execute_script("updateDateField('ctl00$MainContent$CldFechaInicial2$Calendario_text',"+fecha_inicial+");")
                fecha_final=f[1]
                driver.execute_script("updateDateField('ctl00$MainContent$CldFechaFinal2$Calendario_text',"+fecha_final+");")
                #Click en el boton de búsqueda de las facturas del mes
                #loadok(driver.find_element_by_name("ctl00$MainContent$BtnBusqueda"))
                btn_BuscarCFDI=driver.find_element_by_name("ctl00$MainContent$BtnBusqueda")
                btn_BuscarCFDI.click()

                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                focus(driver)
                print('Waiting in Ingreso de parametros de Facturas Emitidas... ',wait)
                if wait==max_attempts:
                    break

        #-----------------------------------------Descarga de facturas emitidas----------------------------------------
        time.sleep(2)
        fallos=[]
        btns_Descarga=[]
        btns_Descarga = driver.find_elements_by_id("BtnDescarga")

        for j in tqdm(range(len(btns_Descarga)),'Facturas'):
            try:
                driver.execute_script(btns_Descarga[j].get_attribute('onclick')) #Ejecuta el metodo de Java Script para la descarga
                #Verificacion de descarga --- OPTIMIZACION PENDIENTE TIP: Comparar nombre de archivo con el desplegado en la pagina
                time.sleep(3)
                #loadok(driver.switch_to_window(driver.window_handles[1]),stage=str(j),verbose=False) #Mueve el foco a la ventana de descarga
                driver.switch_to_window(driver.window_handles[1]) #Mueve el foco a la ventana de descarga
                driver.close()  #Cierra pagina de descarga
                driver.switch_to_window(driver.window_handles[0])    
            except:
                fallos.append(j)

        #-----------------------------------Fin del API de descarga de facturas---------------------------------------
        driver.close()



        #------------------------------## Ingreso a la base de datos en Mongo Altas ##---------------------------------

        #--------------------Lectura de directorio y generacion de lista de facturas a analizar-----------------------

        filespath='./temp/'
        fileslist = [f for f in listdir(filespath) if isfile(join(filespath, f))]


        for i in fileslist:
            if i[-3:]!="xml":
                fileslist.remove(i)


        for k,z in tqdm(enumerate(fileslist)): 
            #Opening File
            xml=open('./temp/'+z,'r')#,encoding=predict_encoding('./temp/'+z))
            xml_parsed=xmltodict.parse(xml.read())

            #Extending XML
            xml_keys=list(xml_parsed['cfdi:Comprobante'].keys())
            xml_values=list(xml_parsed['cfdi:Comprobante'].values())
            xml_df=pd.DataFrame(xml_values).T
            xml_df.columns=xml_keys

            #Descartando columnas no útiles (por el momento)
            columnas=['@xmlns:cfdi','@xmlns:xsi','@Certificado','@xsi:schemaLocation','@Sello']
            for i in columnas:
                try:
                    xml_df.drop([i],axis=1,inplace=True)
                except:
                    pass

            #Elementos para hacer sub-despliegue
            list_sub=['cfdi:Emisor','cfdi:Receptor'] #cfdi:Conceptos tiene una estructura  de mas grandos de profundidad

            #Sub-despliegue de elementos en list_sub
            for i in list_sub:
                for j in list(dict(xml_df[i][0]).keys()):
                    xml_df[i+'_'+j] = xml_df[i][0][j]


            #Desplegar elementos con doble profundidad
            complemento='cfdi:Complemento'
            timbre='tfd:TimbreFiscalDigital'

            for i in list(dict(xml_df[[complemento]].values[0][0][timbre]).keys()):
                xml_df['tfd_'+i] = xml_df[[complemento]].values[0][0][timbre][i]


            #Quitar columnas con diccionarios de sub-despliegue
            xml_df.drop(['cfdi:Emisor','cfdi:Receptor','cfdi:Complemento'],axis=1,inplace=True)


            #Limpiar nombres columna
            for i,e in enumerate(xml_df.columns):
                xml_df.rename(columns={str(e):str(e).replace('cfdi:','')},inplace=True)
            for i,e in enumerate(xml_df.columns):
                xml_df.rename(columns={str(e):str(e).replace('@','')},inplace=True)
            for i,e in enumerate(xml_df.columns):
                xml_df.rename(columns={str(e):str(e).lower()},inplace=True)


            #Optimizar tipos de datos
            xml_df.fecha[0] = datetime.strptime(xml_df.fecha[0], '%Y-%m-%dT%H:%M:%S')
            xml_df.fecha

            '''#Se elimina la optimización, pues mongo no acepta datos optimizados con métodos de numpy
            for i in xml_df.columns:    
                try:
                    xml_df[i] = pd.to_numeric(xml_df[i])

                    if type(xml_df[i])==float:
                        xml_df[i] = pd.to_numeric(xml_df[i], downcast='float')
                    elif type(xml_df[i])==int:
                        xml_df[i] = pd.to_numeric(xml_df[i], downcast='int')
                except:
                    pass
            '''

            #Ingreso de identificadores

            xml_df['ingreso']= False if rfc_usuario==xml_df.receptor_rfc[0] else True
            xml_df['usuario']= id_usuario
            xml_df['rfc_usuario']=rfc_usuario

            #Ingresar xml completo como respaldo
            #xml_df['xml']=xml_txt

            #Cerrar archivo
            xml.close()


        #------------------------------Integracion de la base de datos final-------------------------------------------

            if k == 0: 
                df_xml = xml_df #Crea base de datos de salida en la primera iteracion
            else:
                columnas_nuevas = list(xml_df.columns)
                columnas_existentes = list(df_xml.columns)

                #Busca columnas nuevas en el nuevo registro y crea la columna correspondiente
                for e in columnas_existentes:
                    try:
                        columnas_nuevas=columnas_nuevas.remove(e)
                    except:
                        pass

                try:
                    for e in columnas_nuevas:
                        df_xml[e] = df_xml[e].apply(lambda x: None)
                except:
                    pass

                #copia la columna anterior con las nuevas columnas
                df_xml=df_xml.append(df_xml.iloc[0],ignore_index=True)

                #Ingreso de los registros uno a uno en donde pueden no existir todos los campos en el nuevo registro 
                columnas=df_xml.columns

                for i in columnas:
                    try:
                        df_xml[i].iloc[-1] = xml_df[i][0]
                    except:
                        df_xml[i].iloc[-1] = None

        dict_xml=df_xml.to_dict('records')

        #----------------------------Ingreso de datos en la base de datos de Mongo en la nube----------------------------

        pwd=open('pw.txt','r')
        pw=pwd.read()
        cliente=MongoClient('mongodb+srv://api:'+pw.split('\n')[0]+'@clusterdeclaro-tya5c.mongodb.net/test?retryWrites=true&w=majority')
        db_api=cliente.api
        col_facturas=db_api.facturas

        #Ingreso de facturas a Mongo
        col_facturas.insert_many(dict_xml);

        #------------------------------------Eliminación de los archivos XML---------------------------------------------

        #Borrar archivos de temp
        fileslist = [f for f in listdir(filespath) if isfile(join(filespath, f))]
        clean_folder(fl=fileslist)

        #--------------------------------------## API - Declaracion ##--------------------------------------------------
        load =False
        while load==False:
            try:
                #Deteccion de la raiz de los archivos
                directorio=pathlib.Path().absolute()
                filespath=str(directorio)+'/temp'

                #Seleccion de carpeta temporal para descarga de archivow
                chrome_options = webdriver.ChromeOptions()
                prefs = {'download.default_directory' : filespath, 
                         "download.prompt_for_download": False,
                         "download.directory_upgrade": True,
                         "plugins.always_open_pdf_externally": True,
                         "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
                         "download.extensions_to_open": "applications/pdf"}

                chrome_options.add_experimental_option('prefs', prefs)
                options = webdriver.ChromeOptions() 
                options.add_argument("download.default_directory="+filespath)


                #Inicializacion de driver de Selenium
                driver = webdriver.Chrome(chrome_options=chrome_options)

                #Inicializar Navegador y entrar a pagina web
                driver.get("https://ptscdecprov.clouda.sat.gob.mx/")

                #Espera dináminca de la carga del captcha
                loadok(driver.find_elements_by_tag_name("img"))
                time.sleep(2)

                #Obtener Captcha
                images=driver.find_elements_by_tag_name("img")
                captcha = images[1].get_attribute('src')[23:]

                #Integrar Captcha
                image_decoded = base64.b64decode(str(captcha))       
                image = Image.open(io.BytesIO(image_decoded))

                #Mostrar captcha en jupiter notebook
                imgplot = plt.imshow(image)
                plt.show()

                load=True
            except:
                driver.close()
                load=False



        loaded=False
        while loaded==False:
            #Enviar Captcha y solicitar rfc, pwd y cap
            #str_rfc=input("Ingresa tu RFC:")
            #str_pwd=input("Ingresa tu contraseña:")

            str_rfc='IADA810218HG5'
            str_pwd='DaSa0520'
            str_cap=input("Ingresa el Captcha:")

            #Ingreso de credenciales
            loaded=False
            while loaded==False:
                try:
                    rfc = driver.find_element_by_id("rfc")
                    rfc.clear()
                    rfc.send_keys(str_rfc)

                    pwd=driver.find_element_by_id("password")
                    pwd.clear()
                    pwd.send_keys(str_pwd)

                    cap=driver.find_element_by_id("userCaptcha")
                    cap.clear()
                    cap.send_keys(str_cap)

                    btn_Login=driver.find_element_by_id("submit")
                    btn_Login.click()



                    if error_captcha():
                        loaded=False
                        time.sleep(1)
                        #Obtener Captcha
                        images=driver.find_elements_by_tag_name("img")
                        captcha = images[1].get_attribute('src')[23:]

                        #Integrar Captcha
                        image_decoded = base64.b64decode(str(captcha))       
                        image = Image.open(io.BytesIO(image_decoded))

                        #Mostrar captcha en jupiter notebook
                        imgplot = plt.imshow(image)
                        plt.show()
                    else:
                        loaded=True
                except:
                    pass

        #-----------------------------------Ir a pestaña de Mi contabilidad---------------------------------------------

        #Ha tenido problemas en el click al quedarse seleccionado

        loaded=False
        wait=1
        while loaded==False:
            try:
                a_elements=driver.find_elements_by_class_name('ui-menuitem-text')
                btn_Presentacion=lookuptag(a_elements,'Presentación de la declaración')
                btn_Presentacion.click()
                #time.sleep(1)
                a_elements=driver.find_elements_by_class_name('ui-menuitem-text')
                btn_OtrasObligaciones=lookuptag(a_elements,'Mi Contabilidad')
                btn_OtrasObligaciones.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                focus(driver)
                btn_Presentacion=lookuptag(a_elements,'Consultas')
                btn_Presentacion.click()
                print('Waiting in seleccion pestaña Mi Cotablidad... ',wait)
                if wait==max_attempts:
                    break

        ventana_emergente_nueva_forma()

        #---------------------Ingreso de informacion del periodo de la declaracion----------------------------------

        loaded=False
        wait=1
        while loaded==False:
            try:
                sel_periodicidad = Select(driver.find_element_by_id('MainContent_wucConfigDeclaracion_wucDdlPeriodicidad_ddlCatalogo'))
                sel_periodicidad.select_by_value("M")

                #Selección del mes
                mes= '012' if time.localtime().tm_mon == 1 else ( str('00'+str(time.localtime().tm_mon-1)) if time.localtime().tm_mon<10 else str('0'+str(time.localtime().tm_mon -1)))
                sel_periodo = Select(driver.find_element_by_id('MainContent_wucConfigDeclaracion_wucDdlPeriodoFiscal_ddlCatalogo'))
                sel_periodo.select_by_value(mes)

                btn_siguiente=driver.find_element_by_id('MainContent_btnSiguiente')
                btn_siguiente.click()

                #Boton "+" utilizado en otras obligaciones
                #btn_mas=driver.find_element_by_id('MainContent_wucObligaciones_ImgOtrasOblig')
                #btn_mas.click()

                time.sleep(2)
                ventana_emergente_nueva_forma()
                loaded=True
            except:
                time.sleep(wait)
                wait+=1
                print('Waiting in Ingreso Periodo Declaracion... ',wait)
                if wait==max_attempts:
                    break

        #Selector de checkbox de obligaciones
        loaded=False
        wait=1
        while loaded==False:
            try:
                chb_isr=driver.find_element_by_id('MainContent_wucObligaciones_rptGvObligaciones_gvObligaciones_0_chkObligaciones_0')
                chb_isr.click()

                chb_iva=driver.find_element_by_id('MainContent_wucObligaciones_rptGvObligaciones_gvObligaciones_0_chkObligaciones_1')
                chb_iva.click()

                btn_siguiente=driver.find_element_by_id('MainContent_btnSiguiente')
                btn_siguiente.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in Checkboxes... ',wait)
                if wait==max_attempts:
                    break

        loaded= False
        wait=1
        while loaded==False:
            try:
                btn_msg=driver.find_element_by_id('MainContent_Btn_EnviarDeclaracionPMS')
                btn_msg.click()
                loaded=True
            except:
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting... ',wait)
                if wait==max_attempts:
                    break


        #Mucho tiempo en pasar al siguiente

        #----------------------------------------Ingreso de información en ISR----------------------------------------

        #focus()
        loaded=False
        wait=1
        while loaded==False:
            try:
                time.sleep(1)
                o_elements=driver.find_elements_by_tag_name('strong')
                btn_isr=lookuptag(o_elements,'ISR PERSONAS FÍSICAS, ACTIVIDAD EMPRESARIAL Y PROFESIONAL')
                btn_isr.click()
                loaded=True
            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waitingin in Ingreso ISR... ',wait)
                if wait==max_attempts:
                    break

        loaded=False
        wait=1
        while loaded==False:
            try:
                cmb_gastos=driver.find_element_by_id('342textbox8')
                cmb_gastos.clear()
                cmb_gastos.send_keys(gastos)

                cmb_ingresos=driver.find_element_by_id('342textbox5')
                cmb_ingresos.clear()
                cmb_ingresos.send_keys(ingresos)

                cmb_anterior=driver.find_element_by_id('342textbox16')
                cmb_anterior.clear()
                cmb_anterior.send_keys(anterior)

                cmb_retenido=driver.find_element_by_id('342textbox18')
                cmb_retenido.clear()
                cmb_retenido.send_keys(retenido)

                #Seleccion de pestaña de determinaciond e pago
                driver.execute_script("window.scrollTo(0, 0);") #Scroll a la parte de arriba
                li_elements=driver.find_elements_by_tag_name('li')
                tab_detpago=lookuptag(li_elements,'Determinación de pago')
                tab_detpago.click()

                #Extraccion de datos de la Determinacion de Pago
                val_isr_a_cargo = driver.find_element_by_id('342textbox10005').get_attribute('value')
                val_isr_total_de_contribucioes= driver.find_element_by_id('342textbox10009').get_attribute('value')
                val_isr_catidad_a_cargo= driver.find_element_by_id('342textbox100025').get_attribute('value')
                val_isr_cantidad_a_pagar= driver.find_element_by_id('342textbox100030').get_attribute('value')

                #Regreso a pantalla principal
                driver.execute_script("window.scrollTo(0, 0);")
                btn_menuprincipal=driver.find_element_by_id('btnMenuPrincipal')
                btn_menuprincipal.click()

                loaded=True
            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in Ingreso ISR data... ',wait)
                if wait==max_attempts:
                    break

        #-----------------------------------Ingreso de informacion de IVA---------------------------------------------

        loaded=False
        wait=1
        while loaded==False:
            try:
                o_elements=driver.find_elements_by_id('tituloObligacion')
                btn_iva=lookuptag(o_elements,'IMPUESTO AL VALOR AGREGADO')
                btn_iva.click()
                loaded=True
            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in Ingreso IVA... ',wait)
                if wait==max_attempts:
                    break

        loaded=False
        wait=1
        while loaded==False:
            try:
                cmb_actividades_gravadas_16=driver.find_element_by_id('332textbox4')
                cmb_actividades_gravadas_16.clear()
                cmb_actividades_gravadas_16.send_keys(actividades_gravadas_16)


                cmb_actividades_gravadas_0=driver.find_element_by_id('332textbox5')
                cmb_actividades_gravadas_0.clear()
                cmb_actividades_gravadas_0.send_keys(actividades_gravadas_0)

                cmb_actividades_excentas=driver.find_element_by_id('332textbox6')
                cmb_actividades_excentas.clear()
                cmb_actividades_excentas.send_keys(actividades_excentas)

                cmb_iva_acreditable_del_periodo=driver.find_element_by_id('332textbox8')
                cmb_iva_acreditable_del_periodo.clear()
                cmb_iva_acreditable_del_periodo.send_keys(iva_acreditable_del_periodo)

                cmb_iva_retenido=driver.find_element_by_id('332textbox9')
                cmb_iva_retenido.clear()
                cmb_iva_retenido.send_keys(iva_retenido)

                cmb_actividades_gravadas_16=driver.find_element_by_id('332textbox4')
                cmb_actividades_gravadas_16.clear()
                cmb_actividades_gravadas_16.send_keys(actividades_gravadas_16)

                cmb_otras_a_cargo=Select(driver.find_element_by_id('332select10'))
                cmb_otras_a_cargo.select_by_value('2')#0=Sin Seleccion 1=Si 2=No

                cmb_otras_a_favor=Select(driver.find_element_by_id('332select16'))
                cmb_otras_a_favor.select_by_value('2')#0=Sin Seleccion 1=Si 2=No

                #Seleccion de pestaña de determinaciond e pago IVA
                driver.execute_script("window.scrollTo(0, 0);") #Scroll a la parte de arriba
                li_elements=driver.find_elements_by_tag_name('li')
                tab_detpago=lookuptag(li_elements,'Determinación de pago')
                tab_detpago.click()

                #Extraccion de datos de la Determinacion de Pago del IVA
                val_iva_a_cargo = driver.find_element_by_id('342textbox10005').get_attribute('value')
                val_iva_total_de_contribucioes= driver.find_element_by_id('342textbox10009').get_attribute('value')
                val_iva_catidad_a_cargo= driver.find_element_by_id('342textbox100025').get_attribute('value')
                val_iva_cantidad_a_pagar= driver.find_element_by_id('342textbox100030').get_attribute('value')

                #Regreso a pantalla principal
                driver.execute_script("window.scrollTo(0, 0);")
                #btn_header=driver.find_elements_by_class_name('ui-menuitem-text')
                #btn_x=lookuptag(btn_header,'Consultas')
                #btn_x.click()
                btn_menuprincipal=driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div[1]/form/div[1]/div[2]/div[2]/div[2]/div/button[1]')
                btn_menuprincipal.click()

                loaded=True

            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in Ingreso IVA data... ',wait)
                if wait==max_attempts:
                    break

        #---------------------------------------------Total a Pagar------------------------------------------------------

        loaded=False
        wait=1
        while loaded==False:
            try:
                txt_totalapagar=driver.find_element_by_id('totalPagar')
                total_a_pagar=txt_totalapagar.text
                loaded=True
            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in obteniendo Total a Pagar... ',wait)
                if wait==max_attempts:
                    break


        '''
        # ------------------------------------------Vista Previa-------------------------------------------------------
        loaded=False
        wait=1
        while loaded==False:
            try:
                btn_vistaprevia=driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div[1]/form/div[1]/div[1]/div/div[1]/div[5]/div/a[1]/strong')
                btn_vistaprevia.click()

                #Guardar la vista previa
                #pdf = driver.find_element_by_id('ifrmVistaPrevia')
                #url = pdf.get_attribute('src')
                #wget.download(url, './vistaprevia.pdf')

                btn_cerrarvistaprevia=driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div[29]/div/div/div[2]/a/strong')
                btn_cerrarvistaprevia.click()

            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                print('Waiting in Vista Previa... ',wait)
                if wait==max_attempts:
                    print('Roto en Vista Previa')
                    break
        '''


        '''
        #------------------------------------------Envio de Desclaracion-----------------------------------------------

        loaded=False
        wait=1
        while loaded==False:
            try:
                btn_vistaprevia=driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div[1]/form/div[1]/div[1]/div/div[1]/div[5]/div/a[2]/strong')
                btn_vistaprevia.click()

                #Guardar comprobante


            except:
                focus(driver)
                loaded=False
                time.sleep(wait)
                wait=wait+1
                if wait==max_attempts:
                    break
        '''
        driver.close()
        print('Total a pagar:', total_a_pagar)
        print("Execucion correcta")
        
              
        return render_template('index.html',
            model_results='',
            model_plot=Markup('<img src="data:image/png;base64,{}">'.format(plot_url)),
            s_embarked=s_embarked,
            s_fare=s_fare,
            s_age=s_age,
            s_gender=s_gender,
            s_title=s_title,
            s_class=s_class,
            s_cabin=s_cabin,
            s_sibsp=s_sibsp,
            s_parch=s_parch)
    else:
        