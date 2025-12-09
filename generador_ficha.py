#--------------------------
# Generador ficha V 1.1
# -------------------------

from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import BaseFilter
from telegram import filters
import re
import requests
from bs4 import BeautifulSoup 
import sys

# ----------------------------------------------------------------------
# Configuracion del Usuario
# ----------------------------------------------------------------------
MI_NUMERO = "+54 9 2235385001"
TELEGRAM_BOT_TOKEN = '8586713628:AAFm9sVd_aysUs3cmux9dOkiWQZK6U152Vc'
LINK_PRUEBA = "https://cabrerapropmdq.com/apartamento-venta-centro-mar-del-plata/9627731?shared=whatsapp" 

# Regex estricto para evitar IDs (requiere al menos prefijo o formato largo)
PATRON_TELEFONO = r'(?:\+\d{1,3}\s?\d{2,4}\s?[\s\d]{4}[-\s]?\d{4,6})|(?:\d{3,5}[-\s]?\d{4}[-\s]?\d{4})'

# Patrón agresivo para limpiar desde 'Contáctanos' hasta el final
PATRON_LIMPIEZA_CONTACTO = r'Contáctanos Cabrera Propiedades.*'
PATRON_LIMPIEZA_CONTACTO = r'Escribania designada:.*'

def generar_ficha_desde_enlace():
    print("-" * 50)
    print(f"Iniciando Web Scraping en: {LINK_PRUEBA}")
    print("-" * 50)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(LINK_PRUEBA, headers=headers)
        response.raise_for_status() 
        sopa = BeautifulSoup(response.text, 'html.parser')
        
        titulo_elem = sopa.find('h2', class_='title-sup-property')
        titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Título no encontrado"
        
        descripcion_elem = sopa.find('article', id='article-container')
        
        if descripcion_elem:
            descripcion_limpia = descripcion_elem.get_text(separator=' ', strip=True)
            texto_de_la_ficha = f"{titulo} {descripcion_limpia}"
            print(f"✅ Título encontrado: {titulo}")
            print("✅ Descripción extraída con éxito.")
        else:
            texto_de_la_ficha = sopa.find('body').get_text(separator=' ', strip=True)
            print("⚠️ Advertencia: Usando texto completo del cuerpo.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return
    
    numeros_encontrados = re.findall(PATRON_TELEFONO, texto_de_la_ficha)

    if not numeros_encontrados:
        print("\n✅ No se encontraron números.")
        return

    print("\n" + "=" * 50)
    print(f"⚠️ CONTROL: Números encontrados:")
    numeros_unicos = sorted(list(set(n.strip() for n in numeros_encontrados if n.strip())))
    for num in numeros_unicos: 
        print(f"- {num}")
    print("=" * 50)

    # confirmacion = input(f"¿Reemplazar por {MI_NUMERO}? (S/N): ").upper()
    confirmacion = 'S'
    
    if confirmacion == 'S':
        # 3. Automatización: Reemplazo
        texto_modificado = re.sub(PATRON_TELEFONO, MI_NUMERO, texto_de_la_ficha)
        # Cortamos el texto donde empieza la frase "Buscar Departamento" 
        # y nos quedamos con la segunda parte [1]
        if "Buscar Departamento" in texto_modificado:
            texto_modificado = texto_modificado.split("Buscar Departamento")[-1]
            texto_modificado = "Departamento" + texto_modificado # Agregamos la palabra para que el título quede bien
        # 3b. Limpieza de contacto sobrante (AQUI ESTABA EL DETALLE)
        # Usamos flags=re.DOTALL para que capture el resto del documento
        texto_modificado_limpio = re.sub(PATRON_LIMPIEZA_CONTACTO, "", texto_modificado, flags=re.DOTALL | re.IGNORECASE)

        # 4. Output Final
        print("\n🎉 Publicación Modificada (Copia y Pega):")
        print("=" * 50)
        print(texto_modificado_limpio) # <-- AHORA IMPRIME LA VERSION LIMPIA
        print("=" * 50)
    else:
        print("\n❌ Cancelado.")

# ----------------------------------------------------
# NUEVA FUNCIÓN PRINCIPAL PARA TELEGRAM
# ----------------------------------------------------

def handle_message(update, context):
    """Maneja los mensajes entrantes, busca enlaces y procesa."""
    mensaje_recibido = update.message.text

    # Comprobación de seguridad/lógica: ¿Es un enlace de la inmobiliaria?
    if "cabrerapropmdq.com" in mensaje_recibido:

        # 1. Llamar a tu función principal para hacer el scraping
        print(f"🤖 Procesando enlace: {mensaje_recibido}")
        ficha_procesada = generar_ficha_desde_enlace(mensaje_recibido)

        # 2. Enviar la respuesta de vuelta por Telegram
        update.message.reply_text(ficha_procesada)

    else:
        # Respuesta si el mensaje no contiene un enlace válido
        update.message.reply_text("👋 Hola! Por favor, envíame el enlace completo de la ficha de cabrerapropmdq.com para que pueda procesar la publicación.")


if __name__ == "__main__":
    # 1. Iniciar el bot con el Token
    # Usamos el modo Updater/Long Polling (ideal para Railway Worker)
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 2. Añadir el manejador de mensajes de texto (filtra todos los mensajes que no son comandos)
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 3. Iniciar el bot y el ciclo de escucha
    print("🤖 Bot de Telegram iniciado y esperando mensajes...")
    # start_polling hace que el proceso se quede "escuchando", evitando el crash
    updater.start_polling() 
    updater.idle() # Mantiene el proceso vivo