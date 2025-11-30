import json
import math
import os

def calcular_vpeh_indicator(precio, tamano, habitaciones):
    """
    Calcula el Indicador de Valor por Espacio y Habitación (VPEH)
    
    Fórmula: VPEH = Precio / (Tamaño × √Habitaciones)
    
    Args:
        precio (float): Precio de la propiedad en euros
        tamano (float): Tamaño en metros cuadrados
        habitaciones (int): Número de habitaciones
    
    Returns:
        float: Valor del indicador VPEH
    """
    if tamano <= 0 or habitaciones <= 0:
        return float('inf')  # Valor infinito para datos inválidos
    
    vpeh = precio / (tamano * math.sqrt(habitaciones))
    return round(vpeh, 2)

def procesar_json_con_vpeh(filename):
    """
    Lee el archivo JSON, calcula el indicador VPEH para cada propiedad,
    añade el campo y ordena por el indicador de menor a mayor
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(filename):
            print(f"❌ Error: El archivo '{filename}' no existe")
            return None
        
        # Leer el archivo JSON
        print(f"📂 Leyendo archivo: {filename}")
        with open(filename, 'r', encoding='utf-8') as file:
            propiedades = json.load(file)
        
        print(f"📊 Propiedades cargadas: {len(propiedades)}")
        
        # Calcular VPEH para cada propiedad
        propiedades_procesadas = 0
        propiedades_con_errores = 0
        
        for propiedad in propiedades:
            try:
                precio = propiedad.get('price_euro', 0)
                tamano = propiedad.get('size_sqm', 0)
                habitaciones = propiedad.get('bedrooms', 0)
                
                # Calcular el indicador VPEH
                vpeh = calcular_vpeh_indicator(precio, tamano, habitaciones)
                
                # Añadir el campo VPEH_indicator
                propiedad['VPEH_indicator'] = vpeh
                
                propiedades_procesadas += 1
                
                print(f"   ✅ {propiedad.get('title', 'Sin título')[:50]}...")
                print(f"      💰 {precio:,}€ - 📏 {tamano}m² - 🏠 {habitaciones}hab")
                print(f"      📈 VPEH: {vpeh}")
                
            except Exception as e:
                print(f"   ❌ Error procesando propiedad: {e}")
                propiedad['VPEH_indicator'] = float('inf')
                propiedades_con_errores += 1
        
        print(f"\n📊 Procesamiento completado:")
        print(f"   ✅ Propiedades procesadas: {propiedades_procesadas}")
        print(f"   ❌ Propiedades con errores: {propiedades_con_errores}")
        
        # Ordenar por VPEH de menor a mayor (mejor valor primero)
        print(f"\n🔄 Ordenando propiedades por indicador VPEH...")
        propiedades_ordenadas = sorted(propiedades, key=lambda x: x.get('VPEH_indicator', float('inf')))
        
        # Crear nombre de archivo de salida
        nombre_base = filename.replace('.json', '')
        archivo_salida = f"{nombre_base}_con_vpeh.json"
        
        # Guardar el archivo ordenado
        with open(archivo_salida, 'w', encoding='utf-8') as file:
            json.dump(propiedades_ordenadas, file, ensure_ascii=False, indent=2)
        
        print(f"💾 Archivo guardado: {archivo_salida}")
        
        # Mostrar resumen de los mejores valores
        print(f"\n🏆 TOP 5 MEJORES VALORES (VPEH más bajo):")
        print("="*80)
        
        for i, propiedad in enumerate(propiedades_ordenadas[:5], 1):
            vpeh = propiedad.get('VPEH_indicator', 0)
            precio = propiedad.get('price_euro', 0)
            tamano = propiedad.get('size_sqm', 0)
            habitaciones = propiedad.get('bedrooms', 0)
            titulo = propiedad.get('title', 'Sin título')
            
            print(f"\n{i}. {titulo}")
            print(f"   💰 Precio: {precio:,}€")
            print(f"   📏 Tamaño: {tamano} m²")
            print(f"   🏠 Habitaciones: {habitaciones}")
            print(f"   📈 VPEH: {vpeh} (menor = mejor valor)")
            print(f"   💡 Precio/m²: {precio/tamano if tamano > 0 else 'N/A':.2f}€/m²")
        
        return propiedades_ordenadas
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{filename}'")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo JSON no es válido: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def mostrar_explicacion_vpeh():
    """
    Muestra la explicación del indicador VPEH
    """
    print("📊 INDICADOR DE VALOR POR ESPACIO Y HABITACIÓN (VPEH)")
    print("="*60)
    print("Fórmula: VPEH = Precio / (Tamaño × √Habitaciones)")
    print("")
    print("📈 Interpretación:")
    print("• VPEH MÁS BAJO = MEJOR VALOR por dinero invertido")
    print("• Considera precio, tamaño Y número de habitaciones")
    print("• La raíz cuadrada suaviza el impacto de muchas habitaciones")
    print("• Ideal para comparar propiedades de diferentes características")
    print("")
    print("💡 Ejemplo:")
    print("• Casa A: 120,000€, 100m², 3 hab → VPEH = 120,000/(100×√3) = 693.19")
    print("• Casa B: 150,000€, 150m², 4 hab → VPEH = 150,000/(150×√4) = 500.00")
    print("• Casa B tiene MEJOR valor (VPEH más bajo)")
    print("="*60)

if __name__ == "__main__":
    # Configuración del archivo a procesar
    filename = "castellon.json"
    
    print("🚀 CALCULADORA DE INDICADOR VPEH")
    print("="*50)
    
    # Mostrar explicación del indicador
    mostrar_explicacion_vpeh()
    
    # Verificar si el archivo está en la carpeta json
    if not os.path.exists(filename):
        # Intentar buscar en la carpeta json
        json_filename = os.path.join("json", filename)
        if os.path.exists(json_filename):
            filename = json_filename
            print(f"📂 Archivo encontrado en carpeta json: {filename}")
        else:
            print(f"❌ No se encontró el archivo '{filename}' ni en 'json/{filename}'")
            print("📝 Archivos JSON disponibles:")
            
            # Listar archivos JSON disponibles
            for file in os.listdir('.'):
                if file.endswith('.json'):
                    print(f"   • {file}")
            
            if os.path.exists('json'):
                for file in os.listdir('json'):
                    if file.endswith('.json'):
                        print(f"   • json/{file}")
            
            exit(1)
    
    # Procesar el archivo
    resultado = procesar_json_con_vpeh(filename)
    
    if resultado:
        print(f"\n🎉 ¡Procesamiento completado exitosamente!")
        print(f"📊 Total de propiedades procesadas: {len(resultado)}")
        
        # Mostrar estadísticas del VPEH
        vpeh_valores = [p.get('VPEH_indicator', float('inf')) for p in resultado if p.get('VPEH_indicator', float('inf')) != float('inf')]
        
        if vpeh_valores:
            print(f"\n📈 Estadísticas VPEH:")
            print(f"   • VPEH mínimo (mejor): {min(vpeh_valores):.2f}")
            print(f"   • VPEH máximo (peor): {max(vpeh_valores):.2f}")
            print(f"   • VPEH promedio: {sum(vpeh_valores)/len(vpeh_valores):.2f}")
    else:
        print(f"\n❌ No se pudo procesar el archivo")
