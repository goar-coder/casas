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

def extraer_viviendas_de_pagina(driver):
    """
    Extrae las viviendas de la página actual
    """
    try:
        print("🔍 Extrayendo viviendas de la página...")
        
        # Scroll para cargar contenido dinámico
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Buscar todos los artículos de viviendas
        viviendas = []
        articles = soup.find_all('article', class_='item')
        
        print(f"📊 Encontrados {len(articles)} artículos")
        
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
                
                vivienda_data = {
                    'precio': price,
                    'metros': metros,
                    'habitaciones': habitaciones,
                    'banos': banos,
                    'precio_por_m2': precio_por_m2,
                    'enlace': full_link,
                    'titulo': title,
                    'descripcion': descripcion,
                    'planta': planta
                }
                
                viviendas.append(vivienda_data)
                print(f"   ✅ Añadida: {title}")
                print(f"      💰 {price:,}€ - 📏 {metros}m² - 🏠 {habitaciones}hab - 🛿 {banos}baños")
                if planta:
                    print(f"      🏢 {planta}")
                print(f"      📊 Precio/m²: {precio_por_m2:.2f}€/m²")
                
            except Exception as e:
                print(f"   ❌ Error procesando artículo: {e}")
                continue
        
        # Ordenar por mejor precio por m² (menor precio por m² = mejor)
        viviendas_ordenadas = sorted(viviendas, key=lambda x: x['precio_por_m2'])
        
        return viviendas_ordenadas
        
    except Exception as e:
        print(f"❌ Error extrayendo viviendas: {e}")
        return []

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
        
        # Paso 3: Extraer las viviendas de la página
        viviendas = extraer_viviendas_de_pagina(driver)
        
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
