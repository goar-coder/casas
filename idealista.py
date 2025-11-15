import undetected_chromedriver as uc
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_terrenos_data():
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
    
    url = "https://www.idealista.com/areas/venta-terrenos/con-precio-hasta_100000,terrenos-urbanos/?shape=%28%28%7BuftF%7CiwXgjRmiIyxCmiIkOkea%40vgB%7BeMvnGsxJtsM%7BbH%60pHfzGzhGjbQ%7DUvpY%7DqBvnZygNn%7EG%29%29&ordenado-por=precios-asc"
    
    try:
        print("Accediendo a Idealista terrenos...")
        driver.get(url)
        time.sleep(8)  # Tiempo extra para cargar completamente
        
        # Verificar si fuimos bloqueados
        page_title = driver.title
        print(f"Título de la página: {page_title}")
        
        if "DataDome" in driver.page_source or "Access Denied" in driver.page_source or "blocked" in page_title.lower():
            print("❌ Bloqueados por DataDome o sistema anti-bot")
            return []
        
        # Scroll para cargar contenido dinámico
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Buscar todos los artículos de terrenos
        terrenos = []
        articles = soup.find_all('article', class_='item')
        
        print(f"Encontrados {len(articles)} artículos")
        
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
                
                # Extraer detalles (m² y tipo)
                detail_div = article.find('div', class_='item-detail-char')
                if not detail_div:
                    continue
                
                detail_spans = detail_div.find_all('span', class_='item-detail')
                if len(detail_spans) < 2:
                    continue
                
                # Primer item-detail: metros cuadrados
                metros_text = detail_spans[0].get_text(strip=True)
                metros_match = re.search(r'([\d.]+)', metros_text.replace('.', '').replace(',', ''))
                if not metros_match:
                    continue
                metros = int(metros_match.group(1))
                
                # Segundo item-detail: descripción/tipo
                tipo_text = detail_spans[1].get_text(strip=True)
                
                # Filtrar: excluir si contiene "(solar)"
                if "(solar)" in tipo_text.lower():
                    print(f"Excluido (solar): {tipo_text}")
                    continue
                
                # Extraer enlace
                link_element = article.find('a', class_='item-link')
                if not link_element:
                    continue
                
                href = link_element.get('href', '')
                full_link = urljoin("https://www.idealista.com", href)
                title = link_element.get('title', link_element.get_text(strip=True))
                
                # Calcular relación m²/precio (mayor es mejor)
                ratio = metros / price if price > 0 else 0
                
                terreno_data = {
                    'precio': price,
                    'metros': metros,
                    'tipo': tipo_text,
                    'enlace': full_link,
                    'titulo': title,
                    'ratio_m2_precio': ratio
                }
                
                terrenos.append(terreno_data)
                print(f"Añadido: {title} - {price}€ - {metros}m² - Ratio: {ratio:.6f}")
                
            except Exception as e:
                print(f"Error procesando artículo: {e}")
                continue
        
        # Ordenar por mejor relación m²/precio (descendente)
        terrenos_ordenados = sorted(terrenos, key=lambda x: x['ratio_m2_precio'], reverse=True)
        
        return terrenos_ordenados
        
    except Exception as e:
        print(f"Error general: {e}")
        return []
    
    finally:
        print("Cerrando navegador...")
        driver.quit()

def mostrar_resultados(terrenos):
    print("\n" + "="*80)
    print("TERRENOS ORDENADOS POR MEJOR RELACIÓN M²/PRECIO")
    print("="*80)
    
    if not terrenos:
        print("No se encontraron terrenos que cumplan los criterios.")
        return
    
    for i, terreno in enumerate(terrenos, 1):
        print(f"\n{i}. {terreno['titulo']}")
        print(f"   Precio: {terreno['precio']:,}€")
        print(f"   Metros: {terreno['metros']:,} m²")
        print(f"   Tipo: {terreno['tipo']}")
        print(f"   Ratio m²/€: {terreno['ratio_m2_precio']:.6f}")
        print(f"   Enlace: {terreno['enlace']}")
        print(f"   {'-'*60}")
    
    print(f"\nTotal encontrados: {len(terrenos)} terrenos")

if __name__ == "__main__":
    print("Iniciando búsqueda de terrenos en Idealista...")
    terrenos = extract_terrenos_data()
    mostrar_resultados(terrenos)