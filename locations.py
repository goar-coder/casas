import undetected_chromedriver as uc
import time
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generar_combinaciones_letras():
    """
    Genera todas las combinaciones posibles de 2 letras
    """
    import string
    
    letras = string.ascii_lowercase  # a-z
    combinaciones = []
    
    for primera in letras:
        if primera >= 'j':  # Solo letras a partir de 'f'
            for segunda in letras:
                if segunda >= 'x':  # Solo letras a partir de 'n'
                    combinaciones.append(primera + segunda)
    
    # combinaciones = []
    
    # for primera in letras:
    #     for segunda in letras:
    #         combinaciones.append(primera + segunda)
    
    print(f"📝 Generadas {len(combinaciones)} combinaciones de 2 letras")
    return combinaciones

def crear_directorio_json():
    """
    Crea el directorio json si no existe
    """
    directorio = "json"
    if not os.path.exists(directorio):
        os.makedirs(directorio)
        print(f"📁 Directorio '{directorio}' creado")
    else:
        print(f"📁 Directorio '{directorio}' ya existe")

def extraer_ubicaciones_sugeridas(driver):
    """
    Extrae las ubicaciones sugeridas después de escribir 'ab' en el input
    """
    try:
        print("🔍 Esperando que aparezcan las opciones...")
        
        wait = WebDriverWait(driver, 10)
        
        # Esperar a que aparezca el contenedor de resultados
        container_result = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".container-result-list")
        ))
        
        # Esperar un momento adicional para que se carguen todas las opciones
        time.sleep(2)
        
        # Buscar todos los elementos li dentro del contenedor
        opciones = driver.find_elements(By.CSS_SELECTOR, ".container-result-list li")
        
        print(f"📊 Encontradas {len(opciones)} opciones")
        
        ubicaciones = []
        
        for i, opcion in enumerate(opciones):
            try:
                # Extraer data-location (nombre de la ubicación)
                data_location = opcion.get_attribute("data-location")
                
                # Extraer href del enlace interno
                enlace = opcion.find_element(By.CSS_SELECTOR, "a")
                href_completo = enlace.get_attribute("href")
                
                # Procesar href para remover "/mapa" al final
                if href_completo:
                    # Extraer solo la parte de la URL después del dominio
                    if "idealista.com" in href_completo:
                        url_parte = href_completo.split("idealista.com")[1]
                    else:
                        url_parte = href_completo
                    
                    # Remover "/mapa" del final si existe
                    if url_parte.endswith("/mapa"):
                        url_parte = url_parte[:-5]  # Remover los últimos 5 caracteres "/mapa"
                    
                    # Asegurar que termine con /
                    if not url_parte.endswith("/"):
                        url_parte += "/"
                    
                    ubicacion_data = {
                        "text": data_location,
                        "url": url_parte
                    }
                    
                    ubicaciones.append(ubicacion_data)
                    
                    print(f"   ✅ Opción {i+1}: {data_location}")
                    print(f"      🔗 URL: {url_parte}")
                
            except Exception as e:
                print(f"   ❌ Error procesando opción {i+1}: {e}")
                continue
        
        return ubicaciones
        
    except Exception as e:
        print(f"❌ Error extrayendo ubicaciones: {e}")
        return []

def escribir_en_input_busqueda(driver, texto):
    """
    Escribe texto en el input de búsqueda y espera las sugerencias
    """
    try:
        print(f"✏️ Escribiendo '{texto}' en el input de búsqueda...")
        
        wait = WebDriverWait(driver, 15)
        
        # Buscar el input por ID
        input_busqueda = wait.until(EC.element_to_be_clickable((By.ID, "campoBus")))
        
        # Scroll hacia el elemento
        driver.execute_script("arguments[0].scrollIntoView(true);", input_busqueda)
        time.sleep(1)
        
        # Limpiar el input
        input_busqueda.clear()
        time.sleep(0.5)
        
        # Escribir el texto letra por letra (simular comportamiento humano)
        for letra in texto:
            input_busqueda.send_keys(letra)
            time.sleep(0.1)  # Pausa entre letras
        
        print("✅ Texto escrito correctamente")
        
        # Esperar a que aparezcan las sugerencias
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Error escribiendo en input: {e}")
        return False

def aceptar_cookies(driver):
    """
    Hace clic en el botón de aceptar cookies si está presente
    """
    try:
        print("🍪 Buscando botón de cookies...")
        
        wait = WebDriverWait(driver, 10)
        
        # Buscar el botón de aceptar cookies por ID
        try:
            boton_cookies = wait.until(EC.element_to_be_clickable(
                (By.ID, "didomi-notice-agree-button")
            ))
            
            # Hacer clic en el botón
            driver.execute_script("arguments[0].click();", boton_cookies)
            print("✅ Cookies aceptadas correctamente")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"⚠️ No se encontró el botón de cookies o ya fue aceptado: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error manejando cookies: {e}")
        return False

def cargar_ubicaciones_existentes(nombre_archivo="json/locations.json"):
    """
    Carga ubicaciones existentes del archivo JSON si existe
    """
    try:
        if os.path.exists(nombre_archivo):
            with open(nombre_archivo, 'r', encoding='utf-8') as f:
                ubicaciones = json.load(f)
            print(f"📂 Cargadas {len(ubicaciones)} ubicaciones existentes")
            return ubicaciones
        else:
            print("📂 No existe archivo previo, iniciando lista vacía")
            return []
    except Exception as e:
        print(f"⚠️ Error cargando archivo existente: {e}")
        return []

def guardar_json(ubicaciones, nombre_archivo="json/locations.json"):
    """
    Guarda las ubicaciones en un archivo JSON
    """
    try:
        # Crear directorio si no existe
        crear_directorio_json()
        
        # Guardar el archivo JSON
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(ubicaciones, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Archivo guardado: {nombre_archivo}")
        print(f"📊 Total de ubicaciones guardadas: {len(ubicaciones)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando archivo JSON: {e}")
        return False

def agregar_ubicaciones_unicas(ubicaciones_existentes, nuevas_ubicaciones):
    """
    Agrega solo las ubicaciones que no existen ya en la lista
    """
    urls_existentes = {ub['url'] for ub in ubicaciones_existentes}
    agregadas = 0
    
    for nueva in nuevas_ubicaciones:
        if nueva['url'] not in urls_existentes:
            ubicaciones_existentes.append(nueva)
            urls_existentes.add(nueva['url'])
            agregadas += 1
    
    print(f"➕ {agregadas} ubicaciones nuevas agregadas")
    return agregadas

def extraer_locations():
    """
    Script principal para extraer ubicaciones de Idealista
    """
    print("🚀 Iniciando extracción de ubicaciones...")
    
    # Configurar opciones básicas de Chrome
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        # Inicializar el navegador
        driver = uc.Chrome(options=options)
        
        # Eliminar marcadores básicos de webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Navegando a Idealista.com...")
        
        # Abrir Idealista
        driver.get("https://www.idealista.com/")
        
        # Esperar a que cargue
        time.sleep(5)
        
        # Verificar que la página cargó correctamente
        try:
            titulo = driver.title
            print(f"📄 Título de la página: {titulo}")
            print("✅ Página cargada correctamente")
        except Exception as e:
            print(f"❌ Error verificando la página: {e}")
            return
        
        # Aceptar cookies si es necesario
        aceptar_cookies(driver)
        
        # Cargar ubicaciones existentes
        todas_ubicaciones = cargar_ubicaciones_existentes()
        
        # Generar todas las combinaciones de 2 letras
        combinaciones = generar_combinaciones_letras()
        
        print(f"🚀 Iniciando búsqueda de {len(combinaciones)} combinaciones...")
        
        # Procesar cada combinación
        for i, combinacion in enumerate(combinaciones):
            print(f"\n🔍 Procesando combinación {i+1}/{len(combinaciones)}: '{combinacion}'")
            
            # Escribir la combinación en el input de búsqueda
            if escribir_en_input_busqueda(driver, combinacion):
                # Extraer las ubicaciones sugeridas
                nuevas_ubicaciones = extraer_ubicaciones_sugeridas(driver)
                
                if nuevas_ubicaciones:
                    # Agregar solo ubicaciones únicas
                    agregadas = agregar_ubicaciones_unicas(todas_ubicaciones, nuevas_ubicaciones)
                    
                    # Guardar progreso cada 10 búsquedas o si es la última
                    if (i + 1) % 10 == 0 or i == len(combinaciones) - 1:
                        guardar_json(todas_ubicaciones)
                        print(f"💾 Progreso guardado - Total acumulado: {len(todas_ubicaciones)} ubicaciones")
                else:
                    print(f"   ⚠️ No se encontraron ubicaciones para '{combinacion}'")
            
            # Pausa entre búsquedas para simular comportamiento humano
            if i < len(combinaciones) - 1:  # No pausar en la última iteración
                pausa = 2 + (i % 3)  # Pausa variable entre 2-4 segundos
                print(f"   ⏳ Pausando {pausa} segundos...")
                time.sleep(pausa)
        
        # Guardar resultado final
        if guardar_json(todas_ubicaciones):
            print("\n🎉 ¡Extracción completada exitosamente!")
            print(f"📁 Archivo final guardado en: json/locations.json")
            print(f"📊 Total final: {len(todas_ubicaciones)} ubicaciones únicas")
            
            # Mostrar resumen de las primeras ubicaciones
            print(f"\n📋 RESUMEN (primeras 10):")
            for i, ubicacion in enumerate(todas_ubicaciones[:10]):
                print(f"{i+1}. {ubicacion['text']}")
                print(f"   🔗 {ubicacion['url']}")
            
            if len(todas_ubicaciones) > 10:
                print(f"   ... y {len(todas_ubicaciones) - 10} más")
        else:
            print("❌ Error guardando el archivo JSON final")
        
        # Esperar un momento antes de cerrar
        print("\n⏳ Esperando 10 segundos antes de cerrar...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    finally:
        # Cerrar el navegador
        try:
            driver.quit()
            print("🔒 Navegador cerrado.")
        except:
            pass

if __name__ == "__main__":
    extraer_locations()