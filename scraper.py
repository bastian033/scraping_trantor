import os
import re
import requests
import fitz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import nltk
import unicodedata
import string

# Configuración de NLTK
nltk.download('punkt')

class DiarioOficialScraper:
    def __init__(self, url):
        self.url = url
        self.ruta_base = "C:\\Users\\Usuario\\Documents\\scraping\\pdf"

    def configurar_driver(self):
        opciones = Options()
        opciones.add_argument("--headless")
        opciones.add_argument("--disable-gpu")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)

    def guardar_pdf_como_texto(self, enlace, ruta_categoria, nombre_archivo):
        try:
            respuesta = requests.get(enlace)
            if respuesta.status_code != 200 or not respuesta.content.startswith(b"%PDF"):
                print(f"Error al descargar o validar el PDF: {enlace}")
                return

            extraccion = fitz.open(stream=respuesta.content, filetype="pdf")
            archivo_txt = os.path.join(ruta_categoria, f"{nombre_archivo.replace(' ', '_')}.txt")

            with open(archivo_txt, mode="w", encoding="utf-8") as archivo_completo:
                for pagina in extraccion:
                    texto = pagina.get_text()
                    archivo_completo.write(texto + "\n")

            print(f"Archivo guardado: {archivo_txt}")

        except Exception as e:
            print(f"Error procesando PDF: {e}")
            raise

    def busqueda_y_guardado(self):
        driver = self.configurar_driver()
        driver.get(self.url)
        resultados = []

        try:
            categorias = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "title3"))
            )
            print(f"Categorías encontradas: {len(categorias)}")

            pdfs = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@target="_blank"]'))
            )
            print(f"PDFs encontrados: {len(pdfs)}")

            lista = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@style="float:left; width:550px;"]'))
            )
            print(f"Lista encontrada: {len(lista)}")

            for i, cat in enumerate(categorias):
                nombre_categoria = cat.text.strip()
                limite = categorias[i + 1].location["y"] if i + 1 < len(categorias) else float("inf")

                for pdf, lis in zip(pdfs, lista):
                    if cat.location["y"] <= pdf.location["y"] < limite:
                        enlace = pdf.get_attribute("href")
                        contenido = self.guardar_pdf_como_texto(enlace, nombre_categoria, lis.text)
                        resultados.append({
                            "categoria": nombre_categoria,
                            "archivo": lis.text,
                            "contenido": contenido
                        })

        except Exception as e:
            print(f"Error general: {e}")
            raise

        finally:
            driver.quit()

        return resultados

    def limpieza_texto(self):
        for carpeta in os.listdir(self.ruta_base):
            ruta_carpeta = os.path.join(self.ruta_base, carpeta)
            for archivo in os.listdir(ruta_carpeta):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                try:
                    with open(ruta_archivo, mode="r", encoding="utf-8") as archivo_lectura:
                        texto = archivo_lectura.read()
                        texto_limpio = self.procesar_texto(texto)

                    with open(ruta_archivo, mode="w", encoding="utf-8") as archivo_escritura:
                        archivo_escritura.write(texto_limpio)

                except Exception as e:
                    print(f"Error limpiando archivo {ruta_archivo}: {e}")

    def procesar_texto(self, texto):
        sin_puntuacion = texto.translate(str.maketrans("", "", string.punctuation))
        sin_caracteres = re.sub(r"[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s]", "", sin_puntuacion)
        sin_espacios = re.sub(r"\s+", " ", sin_caracteres).strip()
        normalizado = unicodedata.normalize("NFD", sin_espacios)
        sin_tildes = "".join(
            c for c in normalizado if unicodedata.category(c) != "Mn"
        )
        return sin_tildes

    def encontrar_patrones(self, texto, patrones):
        resultados = {}
        for patron in patrones:
            coincidencias = re.findall(patron, texto)
            if coincidencias:
                resultados[patron] = coincidencias
        return resultados

    def limpieza_y_patrones(self):
        patrones = [
            r"\b\d{1,2}-\d{1,2}-\d{4}\b", 
            r"\bRUT\s?\d{1,2}\.\d{3}\.\d{3}-[0-9kK]\b",  # RUTs 
            r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b",  # Nombres propios 
        ]

        resultados_totales = []

        for carpeta in os.listdir(self.ruta_base):
            ruta_carpeta = os.path.join(self.ruta_base, carpeta)
            for archivo in os.listdir(ruta_carpeta):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                try:
                    with open(ruta_archivo, mode="r", encoding="utf-8") as archivo_lectura:
                        texto = archivo_lectura.read()
                        texto_limpio = self.procesar_texto(texto)
                        patrones_encontrados = self.encontrar_patrones(texto_limpio, patrones)

                        resultados_totales.append({
                            "archivo": archivo,
                            "patrones": patrones_encontrados
                        })

                except Exception as e:
                    print(f"Error procesando archivo {ruta_archivo}: {e}")

        return resultados_totales
