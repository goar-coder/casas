import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def seleccionar_terrenos(driver):
    """
    Selecciona 'Terrenos' del dropdown de tipo de inmueble
    """
    try:
        print("Seleccionando 'Terrenos' del dropdown...")
        
        # Esperar a que el elemento esté presente
        wait = WebDriverWait(driver, 15)
        
        # Método 1: Hacer clic en el botón dropdown primero
        try:
            # Buscar el botón dropdown
            dropdown_button = wait.until(EC.element_to_be_clickable((By.ID, "qa_typology")))
            
            # Scroll hacia el elemento para asegurar visibilidad
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_button)
            time.sleep(1)
            
            # Hacer clic para abrir el dropdown
            print("Abriendo dropdown...")
            driver.execute_script("arguments[0].click();", dropdown_button)
            time.sleep(2)
            
            # Buscar y hacer clic en la opción "Terrenos"
            print("Buscando opción Terrenos...")
            terrenos_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-value='land']")))
            driver.execute_script("arguments[0].click();", terrenos_option)
            
            print("✅ Terrenos seleccionado correctamente")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Método dropdown falló: {e}")
        
        # Método 2: JavaScript directo como backup
        try:
            print("Intentando método JavaScript...")
            script = """
            // Encontrar el select oculto
            var select = document.getElementById('typology');
            if (select) {
                select.value = 'land';
                
                // Disparar eventos
                var changeEvent = new Event('change', { bubbles: true });
                select.dispatchEvent(changeEvent);
                
                // También actualizar el botón visible
                var button = document.getElementById('qa_typology');
                if (button) {
                    var span = button.querySelector('span.placeholder');
                    if (span) span.textContent = ' Terrenos';
                }
                
                return true;
            }
            return false;
            """
            result = driver.execute_script(script)
            if result:
                print("✅ Terrenos seleccionado con JavaScript")
                return True
            else:
                print("❌ No se pudo encontrar el select")
        except Exception as e:
            print(f"Método JavaScript falló: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Error general seleccionando terrenos: {e}")
        return False

def escribir_ubicacion(driver, ubicacion):
    """
    Escribe la ubicación en el input de búsqueda
    """
    try:
        print(f"Escribiendo ubicación: {ubicacion}")
        
        wait = WebDriverWait(driver, 15)
        
        # Buscar el input por ID
        input_ubicacion = wait.until(EC.element_to_be_clickable((By.ID, "campoBus")))
        
        # Scroll hacia el elemento
        driver.execute_script("arguments[0].scrollIntoView(true);", input_ubicacion)
        time.sleep(1)
        
        # Limpiar el input y escribir la ubicación
        input_ubicacion.clear()
        time.sleep(0.5)
        
        # Escribir letra por letra para simular escritura humana
        for letra in ubicacion:
            input_ubicacion.send_keys(letra)
            time.sleep(0.1)
        
        print("✅ Ubicación escrita correctamente")
        time.sleep(2)  # Esperar a que aparezcan sugerencias
        return True
        
    except Exception as e:
        print(f"❌ Error escribiendo ubicación: {e}")
        return False

def hacer_busqueda(driver):
    """
    Hace clic en el botón de búsqueda
    """
    try:
        print("Haciendo clic en el botón de búsqueda...")
        
        wait = WebDriverWait(driver, 15)
        
        # Buscar el botón específico primero
        try:
            boton_buscar = wait.until(EC.element_to_be_clickable((By.ID, "btn-free-search")))
            
            # Scroll hacia el botón
            driver.execute_script("arguments[0].scrollIntoView(true);", boton_buscar)
            time.sleep(1)
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", boton_buscar)
            print("✅ Clic exitoso en el botón 'Buscar' (btn-free-search)")
            
            # Esperar a que cargue la página de resultados
            time.sleep(5)
            
            print(f"📍 Nueva URL: {driver.current_url}")
            
            # Después de la búsqueda exitosa, hacer clic en el enlace específico
            hacer_clic_cigarrales(driver)
            return True
            
        except Exception as e:
            print(f"No se pudo hacer clic en btn-free-search: {e}")
        
        # Buscar el botón de búsqueda - selectores de respaldo
        selectores_boton = [
            "button.btn.action",
            "button[type='submit']",
            "input[type='submit']", 
            "button.btn-primary",
            ".search-button",
            "#btn-search"
        ]
        
        boton_encontrado = None
        
        for selector in selectores_boton:
            try:
                if selector.startswith("#") or selector.startswith("."):
                    boton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                else:
                    boton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                boton_encontrado = boton
                print(f"✅ Botón encontrado con selector: {selector}")
                break
            except:
                continue
        
        # Si no encontramos con selectores específicos, buscar por texto
        if not boton_encontrado:
            try:
                boton_encontrado = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Buscar') or contains(text(), 'BUSCAR')]")))
                print("✅ Botón encontrado por texto")
            except:
                pass
        
        # Si aún no lo encontramos, buscar cualquier botón cerca del input
        if not boton_encontrado:
            try:
                # Buscar botón submit en el formulario que contiene el input
                boton_encontrado = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[@type='submit'] | //form//input[@type='submit']")))
                print("✅ Botón encontrado en formulario")
            except:
                pass
        
        if boton_encontrado:
            # Scroll hacia el botón
            driver.execute_script("arguments[0].scrollIntoView(true);", boton_encontrado)
            time.sleep(1)
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", boton_encontrado)
            print("✅ Búsqueda iniciada correctamente")
            
            # Esperar a que cargue la página de resultados
            time.sleep(5)
            
            print(f"📍 Nueva URL: {driver.current_url}")
            return True
        else:
            print("❌ No se pudo encontrar el botón de búsqueda")
            return False
            
    except Exception as e:
        print(f"❌ Error haciendo búsqueda: {e}")
        return False

def hacer_clic_cigarrales(driver):
    """
    Hace clic en el enlace 'El Beato' después de cargar los resultados
    """
    try:
        print("Esperando que cargue la página de resultados...")
        
        wait = WebDriverWait(driver, 20)
        
        # Esperar un poco más para que la página cargue completamente
        time.sleep(3)
        
        print("Buscando enlace por XPath específico...")
        
        # Método 1: Usar el XPath específico
        try:
            enlace_beato = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='sublocations']/li[2]/a")
            ))
            
            # Scroll hacia el enlace
            driver.execute_script("arguments[0].scrollIntoView(true);", enlace_beato)
            time.sleep(1)
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", enlace_beato)
            print("✅ Clic exitoso usando XPath específico: //*[@id='sublocations']/li[2]/a")
            
            # Esperar a que cargue la nueva página
            time.sleep(5)
            print(f"📍 Nueva URL: {driver.current_url}")
            
            # Extraer y procesar las ofertas
            enlaces_ordenados = extraer_y_procesar_ofertas(driver)
            
            return True
            
        except Exception as e:
            print(f"Método por XPath específico falló: {e}")
        
        # Método 2: Backup - Buscar por texto "El Beato" 
        try:
            enlace_beato = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'El Beato')]")
            ))
            
            # Scroll hacia el enlace
            driver.execute_script("arguments[0].scrollIntoView(true);", enlace_beato)
            time.sleep(1)
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", enlace_beato)
            print("✅ Clic exitoso en 'El Beato' (por texto - método backup)")
            
            # Esperar a que cargue la nueva página
            time.sleep(5)
            print(f"📍 Nueva URL: {driver.current_url}")
            
            # Extraer y procesar las ofertas
            enlaces_ordenados = extraer_y_procesar_ofertas(driver)
            
            return True
            
        except Exception as e:
            print(f"Método por texto falló: {e}")
        
        # Método 3: Backup - Buscar por href específico
        try:
            enlace_beato = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[@href='/venta-terrenos/toledo/el-beato/mapa']")
            ))
            
            # Scroll hacia el enlace
            driver.execute_script("arguments[0].scrollIntoView(true);", enlace_beato)
            time.sleep(1)
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", enlace_beato)
            print("✅ Clic exitoso en 'El Beato' (por href - método backup)")
            
            # Esperar a que cargue la nueva página
            time.sleep(5)
            print(f"📍 Nueva URL: {driver.current_url}")
            
            # Extraer y procesar las ofertas
            enlaces_ordenados = extraer_y_procesar_ofertas(driver)
            
            return True
            
        except Exception as e:
            print(f"Método por href falló: {e}")
        
        # Método 5: Listar todos los enlaces disponibles para debug
        try:
            print("🔍 Listando enlaces disponibles para debug...")
            enlaces = driver.find_elements(By.TAG_NAME, "a")
            enlaces_texto = []
            
            for enlace in enlaces[:20]:  # Solo los primeros 20 para no saturar
                texto = enlace.text.strip()
                href = enlace.get_attribute("href")
                if texto and len(texto) > 3:
                    enlaces_texto.append(f"Texto: '{texto}' | Href: {href}")
            
            for enlace_info in enlaces_texto:
                print(f"   {enlace_info}")
                
        except Exception as e:
            print(f"Error listando enlaces: {e}")
        
        print("❌ No se pudo encontrar el enlace 'El Beato'")
        return False
        
    except Exception as e:
        print(f"❌ Error general buscando enlace El Beato: {e}")
        return False

def extraer_y_procesar_ofertas(driver):
    """
    Extrae ofertas de terrenos, filtra los que no sean solares y los ordena por relación m²/precio
    """
    try:
        print("🔍 Extrayendo ofertas de la página...")
        
        # Esperar a que carguen las ofertas
        wait = WebDriverWait(driver, 15)
        time.sleep(3)
        
        # Buscar todos los artículos de ofertas
        ofertas = driver.find_elements(By.CSS_SELECTOR, "article.item")
        print(f"📊 Encontradas {len(ofertas)} ofertas")
        
        ofertas_procesadas = []
        
        for i, oferta in enumerate(ofertas):
            try:
                # Extraer precio
                precio_element = oferta.find_element(By.CSS_SELECTOR, ".item-price")
                precio_texto = precio_element.text.replace("€", "").replace(".", "").replace(",", "").strip()
                
                # Convertir precio a número
                try:
                    precio = int(''.join(filter(str.isdigit, precio_texto)))
                    if precio == 0:
                        continue
                except:
                    print(f"   ❌ Oferta {i+1}: No se pudo extraer el precio")
                    continue
                
                # Extraer detalles (metros cuadrados y descripción)
                item_details = oferta.find_elements(By.CSS_SELECTOR, ".item-detail")
                
                if len(item_details) < 2:
                    print(f"   ❌ Oferta {i+1}: No tiene suficientes detalles")
                    continue
                
                # Primer item-detail: metros cuadrados
                metros_texto = item_details[0].text.strip()
                metros = None
                try:
                    # Extraer números de metros cuadrados
                    import re
                    metros_match = re.search(r'(\d+(?:\.\d+)?)', metros_texto.replace(",", "."))
                    if metros_match:
                        metros = float(metros_match.group(1))
                    else:
                        print(f"   ❌ Oferta {i+1}: No se pudieron extraer los metros cuadrados de '{metros_texto}'")
                        continue
                except:
                    print(f"   ❌ Oferta {i+1}: Error procesando metros cuadrados")
                    continue
                
                # Segundo item-detail: descripción
                descripcion = item_details[1].text.strip()
                
                # Filtrar: excluir si contiene "(solar)"
                # if "(solar)" in descripcion.lower():
                #     print(f"   ⚠️ Oferta {i+1}: Excluida por ser solar - '{descripcion}'")
                #     continue
                
                # Extraer enlace
                try:
                    enlace_element = oferta.find_element(By.CSS_SELECTOR, "a.item-link")
                    enlace_href = enlace_element.get_attribute("href")
                    enlace_titulo = enlace_element.text.strip()
                except:
                    print(f"   ❌ Oferta {i+1}: No se pudo extraer el enlace")
                    continue
                
                # Calcular relación metros/precio (más metros por euro = mejor)
                relacion_m2_precio = metros / precio if precio > 0 else 0
                
                oferta_data = {
                    'indice': i + 1,
                    'precio': precio,
                    'metros': metros,
                    'descripcion': descripcion,
                    'enlace_href': enlace_href,
                    'enlace_titulo': enlace_titulo,
                    'relacion_m2_precio': relacion_m2_precio
                }
                
                ofertas_procesadas.append(oferta_data)
                
                print(f"   ✅ Oferta {i+1}: {metros}m² - {precio:,}€ - Relación: {relacion_m2_precio:.6f} m²/€")
                print(f"      📍 {descripcion}")
                print(f"      🔗 {enlace_titulo}")
                
            except Exception as e:
                print(f"   ❌ Error procesando oferta {i+1}: {e}")
                continue
        
        # Ordenar por relación m²/precio (descendente - mejor relación primero)
        ofertas_ordenadas = sorted(ofertas_procesadas, key=lambda x: x['relacion_m2_precio'], reverse=True)
        
        print(f"\n🏆 RESULTADOS ORDENADOS POR MEJOR RELACIÓN M²/PRECIO:")
        print("=" * 80)
        
        enlaces_ordenados = []
        for i, oferta in enumerate(ofertas_ordenadas):
            print(f"\n{i+1}. 📏 {oferta['metros']}m² | 💰 {oferta['precio']:,}€ | 📊 {oferta['relacion_m2_precio']:.6f} m²/€")
            print(f"   📝 {oferta['descripcion']}")
            print(f"   🏠 {oferta['enlace_titulo']}")
            print(f"   🔗 {oferta['enlace_href']}")
            
            enlaces_ordenados.append(oferta['enlace_href'])
        
        print(f"\n📋 LISTA DE ENLACES ORDENADOS:")
        for i, enlace in enumerate(enlaces_ordenados):
            print(f"{i+1}. {enlace}")
        
        return enlaces_ordenados
        
    except Exception as e:
        print(f"❌ Error general extrayendo ofertas: {e}")
        return []

def abrir_idealista():
    """
    Script simple para abrir Idealista.com usando undetected_chromedriver
    """
    print("Iniciando navegador...")
    
    # Configurar opciones básicas de Chrome (como funcionaba antes)
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        # Inicializar el navegador (configuración simple como antes)
        driver = uc.Chrome(options=options)
        
        # Eliminar marcadores básicos de webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Navegando a Idealista.com...")
        
        # Abrir Idealista
        driver.get("https://www.idealista.com/")
        
        # Esperar a que cargue (tiempo original)
        time.sleep(5)
        
        # Verificar que la ventana sigue abierta
        try:
            titulo = driver.title
            url = driver.current_url
            print(f"Título de la página: {titulo}")
            print(f"URL actual: {url}")
        except Exception as e:
            print(f"❌ Error obteniendo información de la página: {e}")
            return
        
        # Verificar si fuimos bloqueados
        page_source = ""
        try:
            page_source = driver.page_source
        except Exception as e:
            print(f"❌ Error obteniendo código fuente: {e}")
            return
            
        if "DataDome" in page_source:
            print("⚠️  Detectado bloqueo de DataDome")
            print("Intentando continuar...")
        elif "blocked" in titulo.lower() or "access denied" in page_source.lower():
            print("⚠️  Acceso bloqueado")
            return
        else:
            print("✅ Página cargada correctamente")
            
        # Verificar que la ventana sigue activa antes de continuar
        try:
            driver.current_window_handle
            print("✅ Ventana del navegador activa")
            
            # Seleccionar "Terrenos" del dropdown
            if seleccionar_terrenos(driver):
                # Escribir ubicación en el input
                escribir_ubicacion(driver, "Toledo, Toledo")
                
                # Hacer clic en el botón de búsqueda
                hacer_busqueda(driver)
                
        except Exception as e:
            print(f"❌ La ventana del navegador se cerró: {e}")
            return
        
        # Mantener el navegador abierto
        print("\nNavegador abierto. Presiona Ctrl+C para cerrar...")
        
        try:
            # Bucle para mantener el navegador abierto
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nCerrando navegador...")
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cerrar el navegador
        try:
            driver.quit()
            print("Navegador cerrado.")
        except:
            pass

if __name__ == "__main__":
    abrir_idealista()