import undetected_chromedriver as uc
import time
import re
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

def abrir_idealista_inicial(driver):
    """
    Abre la página principal de Idealista y acepta cookies
    """
    try:
        print("🌐 Navegando a Idealista.com...")
        
        # Abrir página principal de Idealista
        driver.get("https://www.idealista.com/")
        
        # Esperar a que cargue
        time.sleep(8)
        
        # Verificar que la página cargó correctamente
        try:
            titulo = driver.title
            print(f"📄 Título de la página: {titulo}")
            print("✅ Página cargada correctamente")
        except Exception as e:
            print(f"❌ Error verificando la página: {e}")
            return False
        
        # Aceptar cookies si es necesario
        aceptar_cookies(driver)
        
        return True
        
    except Exception as e:
        print(f"❌ Error abriendo Idealista: {e}")
        return False

def navegar_a_castellon(driver):
    """
    Navega específicamente a la búsqueda de viviendas en Castellón
    """
    try:
        print("🏠 Navegando a búsqueda de viviendas en Castellón...")
        
        url_castellon = "https://www.idealista.com/venta-viviendas/castellon-de-la-plana-castello-de-la-plana-castellon/con-precio-hasta_160000,precio-desde_100000,metros-cuadrados-mas-de_100,de-cuatro-cinco-habitaciones-o-mas/"
        
        driver.get(url_castellon)
        time.sleep(8)  # Tiempo extra para cargar completamente
        
        # Verificar si fuimos bloqueados
        page_title = driver.title
        print(f"📄 Título de la página: {page_title}")
        
        if "DataDome" in driver.page_source or "Access Denied" in driver.page_source or "blocked" in page_title.lower():
            print("❌ Bloqueados por DataDome o sistema anti-bot")
            return False
        
        print("✅ Navegación a Castellón exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error navegando a Castellón: {e}")
        return False

def extraer_viviendas_de_pagina(driver, pagina_num=1):
    """
    Extrae las viviendas de la página actual
    """
    try:
        print(f"🔍 Extrayendo viviendas de la página {pagina_num}...")
        
        # Scroll para cargar contenido dinámico
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Buscar todos los artículos de viviendas
        viviendas = []
        articles = soup.find_all('article', class_='item')
        
        print(f"📊 Encontrados {len(articles)} artículos en página {pagina_num}")
        
        for article in articles:
            try:
                # Extraer precio
                price_span = article.find('span', class_='item-price')
                if not price_span:
                    continue
                
                price_text = price_span.get_text(strip=True)
                # Extraer números del precio (eliminar € y puntos de miles)
                price_match = re.search(r'([\d.]+)', price_text.replace('.', ''))
                if not price_match:
                    continue
                price = int(price_match.group(1))
                
                # Extraer detalles (habitaciones, m², etc.)
                detail_div = article.find('div', class_='item-detail-char')
                if not detail_div:
                    continue
                
                detail_spans = detail_div.find_all('span', class_='item-detail')
                if len(detail_spans) < 1:
                    continue
                
                # Buscar metros cuadrados en los detalles
                metros = 0
                habitaciones = 0
                banos = 0
                planta = ""
                
                for span in detail_spans:
                    span_text = span.get_text(strip=True)
                    
                    # Buscar metros cuadrados
                    metros_match = re.search(r'(\d+)\s*m²', span_text)
                    if metros_match and metros == 0:  # Solo tomar el primero
                        metros = int(metros_match.group(1))
                    
                    # Buscar habitaciones
                    hab_match = re.search(r'(\d+)\s*hab', span_text)
                    if hab_match:
                        habitaciones = int(hab_match.group(1))
                    
                    # Buscar baños
                    bano_match = re.search(r'(\d+)\s*baño', span_text)
                    if bano_match:
                        banos = int(bano_match.group(1))
                    
                    # Buscar información de planta
                    planta_match = re.search(r'Planta\s+[^,]+', span_text, re.IGNORECASE)
                    if planta_match and not planta:
                        planta = planta_match.group(0)
                
                # Saltar si no encontramos metros cuadrados
                if metros == 0:
                    continue
                
                # Extraer enlace
                link_element = article.find('a', class_='item-link')
                if not link_element:
                    continue
                
                href = link_element.get('href', '')
                full_link = urljoin("https://www.idealista.com", href)
                title = link_element.get('title', link_element.get_text(strip=True))
                
                # Calcular precio por m² (menor es mejor)
                precio_por_m2 = price / metros if metros > 0 else float('inf')
                
                # Extraer descripción/ubicación si está disponible
                descripcion = ""
                description_element = article.find('div', class_='item-description')
                if description_element:
                    descripcion = description_element.get_text(strip=True)
                
                # Extraer descripción detallada visitando el enlace
                descripcion_detallada = extraer_descripcion_detallada(driver, full_link, title[:50])
                
                vivienda_data = {
                    'precio': price,
                    'metros': metros,
                    'habitaciones': habitaciones,
                    'banos': banos,
                    'precio_por_m2': precio_por_m2,
                    'enlace': full_link,
                    'titulo': title,
                    'descripcion': descripcion,
                    'descripcion_detallada': descripcion_detallada,
                    'planta': planta
                }
                
                viviendas.append(vivienda_data)
                print(f"   ✅ P{pagina_num}: {title[:60]}...")
                print(f"      💰 {price:,}€ - 📏 {metros}m² - 🏠 {habitaciones}hab - 🛿 {banos}baños")
                if planta:
                    print(f"      🏢 {planta}")
                print(f"      📊 Precio/m²: {precio_por_m2:.2f}€/m²")
                
            except Exception as e:
                print(f"   ❌ Error procesando artículo: {e}")
                continue
        
        return viviendas
        
    except Exception as e:
        print(f"❌ Error extrayendo viviendas: {e}")
        return []

def ir_a_siguiente_pagina(driver, pagina_num):
    """
    Navega a la siguiente página haciendo clic en el número de página
    """
    try:
        print(f"📄 Intentando ir a página {pagina_num}...")
        
        # Scroll hacia abajo para asegurar que la paginación sea visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Buscar el enlace de paginación específico en el div.pagination
        try:
            # Buscar por número de página exacto en el div de paginación
            pagination_link = driver.find_element(By.XPATH, f"//div[@class='pagination']//a[text()='{pagina_num}']")
            
            # Hacer scroll hasta el elemento de paginación
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_link)
            time.sleep(2)
            
            # Obtener la URL antes del clic para verificar el cambio
            url_antes = driver.current_url
            print(f"   📍 URL antes: {url_antes}")
            
            # Clic usando JavaScript para evitar problemas de interceptación
            driver.execute_script("arguments[0].click();", pagination_link)
            print(f"✅ Clic en página {pagina_num} ejecutado")
            
            # Esperar a que cargue la nueva página
            time.sleep(6)
            
            # Verificar que la URL cambió
            url_despues = driver.current_url
            print(f"   📍 URL después: {url_despues}")
            
            if url_antes != url_despues:
                print(f"✅ Navegación a página {pagina_num} exitosa")
                return True
            else:
                print(f"⚠️ La URL no cambió, puede que no se haya navegado")
                return False
            
        except Exception as e:
            print(f"   ⚠️ No se encontró el enlace para página {pagina_num}: {e}")
            
            # Intentar con el botón "Siguiente" usando la clase correcta
            try:
                siguiente_btn = driver.find_element(By.XPATH, "//div[@class='pagination']//a[contains(@class, 'icon-arrow-right-after')]")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
                time.sleep(2)
                
                url_antes = driver.current_url
                driver.execute_script("arguments[0].click();", siguiente_btn)
                print(f"✅ Clic en 'Siguiente' ejecutado")
                time.sleep(6)
                
                url_despues = driver.current_url
                if url_antes != url_despues:
                    print(f"✅ Navegación con 'Siguiente' exitosa")
                    return True
                else:
                    print(f"⚠️ La URL no cambió con 'Siguiente'")
                    return False
                
            except Exception as e2:
                print(f"   ❌ Tampoco se encontró botón 'Siguiente': {e2}")
                return False
        
    except Exception as e:
        print(f"❌ Error navegando a página {pagina_num}: {e}")
        return False

def extraer_descripcion_detallada(driver, enlace, titulo_corto):
    """
    Visita el enlace de la propiedad y extrae la descripción completa del anunciante
    """
    descripcion_html = ""
    
    try:
        print(f"      🔗 Visitando: {titulo_corto}...")
        
        # Guardar la URL actual para volver después
        url_original = driver.current_url
        
        # Navegar al enlace de la propiedad
        driver.get(enlace)
        time.sleep(4)  # Esperar a que cargue la página
        
        # Buscar el comentario del anunciante
        try:
            # Buscar el div comment que contiene la descripción
            comment_div = driver.find_element(By.CSS_SELECTOR, "div.comment[data-expandable='true']")
            
            # Buscar el párrafo dentro del div comment
            descripcion_element = comment_div.find_element(By.CSS_SELECTOR, "div.adCommentsLanguage p")
            
            # Extraer el texto sin tags HTML
            descripcion_html = descripcion_element.get_attribute('textContent')
            
            # Limpiar saltos de línea y espacios extra
            if descripcion_html:
                descripcion_html = descripcion_html.replace('\n', ' ').replace('\r', ' ').strip()
                # Eliminar espacios múltiples
                descripcion_html = ' '.join(descripcion_html.split())
                print(f"      ✅ Descripción extraída ({len(descripcion_html)} caracteres)")
            else:
                print(f"      ⚠️ Descripción vacía")
                
        except NoSuchElementException:
            print(f"      ⚠️ No se encontró descripción del anunciante")
        except Exception as e:
            print(f"      ❌ Error extrayendo descripción: {e}")
        
        # Volver a la página original
        driver.get(url_original)
        time.sleep(2)  # Esperar a que cargue la página original
        
    except Exception as e:
        print(f"      ❌ Error visitando enlace: {e}")
        # Intentar volver a la página original en caso de error
        try:
            driver.get(url_original)
            time.sleep(2)
        except:
            pass
    
    return descripcion_html

def hay_mas_paginas(driver, pagina_actual):
    """
    Verifica si hay más páginas disponibles
    """
    try:
        # Buscar si existe un enlace a la siguiente página
        siguiente_pagina = pagina_actual + 1
        
        # Buscar por número de página específico
        try:
            next_link = driver.find_element(By.XPATH, f"//div[@class='pagination']//a[text()='{siguiente_pagina}']")
            return True
        except:
            pass
        
        # Buscar botón "Siguiente"
        try:
            siguiente_btn = driver.find_element(By.XPATH, "//div[@class='pagination']//a[contains(@class, 'icon-arrow-right-after')]")
            return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"❌ Error verificando páginas disponibles: {e}")
        return False

def extraer_todas_las_paginas(driver):
    """
    Extrae viviendas de todas las páginas disponibles
    """
    todas_las_viviendas = []
    pagina_actual = 1
    max_paginas = 10  # Límite de seguridad para evitar bucles infinitos
    
    print("🔄 Iniciando extracción de todas las páginas...")
    
    while pagina_actual <= max_paginas:
        print(f"\n📖 Procesando página {pagina_actual}...")
        
        # Extraer viviendas de la página actual
        viviendas_pagina = extraer_viviendas_de_pagina(driver, pagina_actual)
        
        if not viviendas_pagina:
            print(f"⚠️ No se encontraron viviendas en página {pagina_actual}")
            break
        
        print(f"✅ Extraídas {len(viviendas_pagina)} viviendas de página {pagina_actual}")
        todas_las_viviendas.extend(viviendas_pagina)
        
        # Verificar si hay más páginas antes de intentar navegar
        if not hay_mas_paginas(driver, pagina_actual):
            print(f"🔚 No hay más páginas disponibles después de página {pagina_actual}")
            break
        
        # Intentar ir a la siguiente página
        pagina_actual += 1
        
        if pagina_actual <= max_paginas:
            if not ir_a_siguiente_pagina(driver, pagina_actual):
                print(f"🔚 Error navegando a página {pagina_actual}, finalizando...")
                break
        
        # Pausa entre páginas para comportamiento humano
        time.sleep(3)
    
    # Ordenar todas las viviendas por mejor precio por m²
    print(f"\n📊 Ordenando {len(todas_las_viviendas)} viviendas totales por precio/m²...")
    viviendas_ordenadas = sorted(todas_las_viviendas, key=lambda x: x['precio_por_m2'])
    
    return viviendas_ordenadas

def extract_viviendas_castellon():
    """
    Función principal que coordina todo el proceso paso a paso
    """
    print("🚀 Iniciando búsqueda de viviendas en Castellón...")
    
    options = uc.ChromeOptions()
    # Configuraciones básicas más compatibles
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Iniciar navegador con evasión de detección
    try:
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"Error inicializando Chrome: {e}")
        print("Intentando con configuración básica...")
        driver = uc.Chrome()
    
    try:
        # Paso 1: Abrir Idealista y aceptar cookies
        if not abrir_idealista_inicial(driver):
            return []
        
        # Paso 2: Navegar a la búsqueda específica de Castellón
        if not navegar_a_castellon(driver):
            return []
        
        # Paso 3: Extraer las viviendas de todas las páginas
        viviendas = extraer_todas_las_paginas(driver)
        
        # Mostrar resultados inmediatamente
        mostrar_resultados(viviendas)
        
        # Guardar en JSON
        guardar_json(viviendas)
        
        # Mantener el navegador abierto
        print("\n🌐 Navegador abierto. Presiona Ctrl+C para cerrar...")
        
        try:
            # Bucle para mantener el navegador abierto
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔒 Cerrando navegador...")
            driver.quit()
        
        return viviendas
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return []
    
    except KeyboardInterrupt:
        print("\n🔒 Cerrando navegador por interrupción...")
        try:
            driver.quit()
        except:
            pass
        return []

def cumple_filtro_planta(planta_info):
    """
    Verifica si la planta cumple con los criterios de filtrado:
    - Planta 1ª (cualquier condición)
    - Planta 2ª, 3ª, etc. solo si tiene "con ascensor"
    - Casas/chalets (sin información de planta) se incluyen
    """
    if not planta_info:
        # Si no hay información de planta, probablemente es casa/chalet - incluir
        return True
    
    planta_lower = planta_info.lower()
    
    # Si es planta 1ª, siempre se incluye
    if "planta 1" in planta_lower or "planta baja" in planta_lower:
        return True
    
    # Si es planta 2ª o superior, solo si tiene ascensor
    if any(f"planta {i}" in planta_lower for i in range(2, 20)):  # Planta 2ª a 19ª
        return "con ascensor" in planta_lower
    
    # Si no coincide con ningún patrón, incluir por defecto
    return True

def guardar_json(viviendas):
    """
    Guarda las viviendas en formato JSON aplicando filtros de planta
    """
    try:
        # Convertir al formato JSON solicitado aplicando filtros
        json_data = []
        viviendas_filtradas = 0
        
        for vivienda in viviendas:
            # Aplicar filtro de planta
            if not cumple_filtro_planta(vivienda['planta']):
                viviendas_filtradas += 1
                print(f"   ❌ Filtrada por planta: {vivienda['planta']} - {vivienda['titulo'][:50]}...")
                continue
            
            json_item = {
                "title": vivienda['titulo'],
                "price_euro": vivienda['precio'],
                "size_sqm": vivienda['metros'],
                "bedrooms": vivienda['habitaciones'],
                "bathrooms": vivienda['banos'],
                "price_per_sqm_euro": round(vivienda['precio_por_m2'], 2),
                "description_snippet": vivienda['descripcion'],
                "description": vivienda['descripcion_detallada'] if vivienda['descripcion_detallada'] else None,
                "link": vivienda['enlace'],
                "floor": vivienda['planta'] if vivienda['planta'] else None
            }
            json_data.append(json_item)
        
        # Obtener la ruta de la carpeta json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, 'castellon.json')
        
        # Guardar el archivo JSON
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Datos guardados en: {json_file_path}")
        print(f"📊 Total de viviendas encontradas: {len(viviendas)}")
        print(f"🚫 Viviendas filtradas por planta: {viviendas_filtradas}")
        print(f"✅ Viviendas guardadas en JSON: {len(json_data)}")
        print(f"\n📋 Criterios de filtro aplicados:")
        print(f"   • Planta 1ª: ✅ Incluidas todas")
        print(f"   • Planta baja: ✅ Incluidas todas") 
        print(f"   • Planta 2ª-19ª: ✅ Solo con ascensor")
        print(f"   • Casas/Chalets: ✅ Incluidas todas")
        
        return json_file_path
        
    except Exception as e:
        print(f"❌ Error guardando JSON: {e}")
        return None

def mostrar_resultados(viviendas):
    print("\n" + "="*80)
    print("VIVIENDAS EN CASTELLÓN ORDENADAS POR MEJOR PRECIO/M²")
    print("="*80)
    
    if not viviendas:
        print("No se encontraron viviendas que cumplan los criterios.")
        return
    
    for i, vivienda in enumerate(viviendas, 1):
        print(f"\n{i}. {vivienda['titulo']}")
        print(f"   Precio: {vivienda['precio']:,}€")
        print(f"   Metros: {vivienda['metros']} m²")
        print(f"   Habitaciones: {vivienda['habitaciones']}")
        print(f"   Baños: {vivienda['banos']}")
        print(f"   Precio/m²: {vivienda['precio_por_m2']:.2f}€/m²")
        if vivienda['descripcion']:
            print(f"   Descripción: {vivienda['descripcion'][:100]}...")
        print(f"   Enlace: {vivienda['enlace']}")
        print(f"   {'-'*60}")
    
    print(f"\nTotal encontradas: {len(viviendas)} viviendas")

if __name__ == "__main__":
    print("Iniciando búsqueda de viviendas en Castellón...")
    viviendas = extract_viviendas_castellon()
