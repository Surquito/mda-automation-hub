import os
import subprocess
import time
from datetime import datetime
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import (
    POWERBI_URL,
    POWERBI_URL_TENDENCIA_1,
    POWERBI_URL_TENDENCIA_2,
    POWERBI_URL_TENDENCIA_3,
    POWERBI_URL_TENDENCIA_4,
    REPORT_PATH,
    REPORT_PATH_TENDENCIAS,
)
from src.logger import logger


class PowerBI:
    def __init__(self):
        subprocess.run(
            "taskkill /F /IM chrome.exe",
            shell=True,
            capture_output=True,
            text=True,
        )
        time.sleep(5)

        os.makedirs(REPORT_PATH, exist_ok=True)
        os.makedirs(REPORT_PATH_TENDENCIAS, exist_ok=True)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": os.path.abspath(REPORT_PATH),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        })
        options.add_argument(
            r"--user-data-dir=C:\Automatizaciones\MDA\SEND_REPORTS\chrome_profile"
        )
        # Renderizado normal de Chrome, ubicado fuera del escritorio visible.
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--window-position=-32000,-32000")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--force-device-scale-factor=1")

        self.driver = webdriver.Chrome(
            service=Service("drivers/chromedriver.exe"),
            options=options,
        )
        self.driver.set_window_size(1920, 1080)
        self.driver.set_window_position(-32000, -32000)

        logger.info(
            "🖥️ Chrome ejecutándose fuera de pantalla: 1920x1080"
        )
        self.driver.set_page_load_timeout(600)

    def _esperar_reporte(
        self,
        url,
        nombre
    ):
        logger.info(
            "🌐 Abriendo página Power BI: %s",
            nombre
        )

        self.driver.get(
            url
        )

        WebDriverWait(
            self.driver,
            180
        ).until(
            lambda driver: (
                "signin" not in driver.current_url.lower()
                and "singlesignon" not in driver.current_url.lower()
            )
        )

        logger.info(
            "📄 URL cargada: %s",
            self.driver.current_url
        )

        logger.info(
            "📄 Título: %s",
            self.driver.title
        )

        # Power BI realiza renderizado asíncrono
        time.sleep(20)

        # Cerrar el panel de filtros si está expandido
        self._cerrar_panel_filtros()

        time.sleep(5)

    def _buscar_visual_principal(self):
        logger.info(
            "🔍 Buscando el contenedor principal del gráfico"
        )

        selectores = [
            "[data-testid='visual-container']",
            "div.visualContainerHost",
            "div.visual-container",
            "div.visualContent",
            "visual-container",
            "[role='img']",
            "svg",
            "canvas"
        ]

        candidatos = []

        for selector in selectores:
            elementos = self.driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            logger.info(
                "🔎 Selector %s: %s elementos",
                selector,
                len(elementos)
            )

            for elemento in elementos:
                try:
                    if not elemento.is_displayed():
                        continue

                    ancho = int(
                        elemento.size.get(
                            "width",
                            0
                        )
                    )

                    alto = int(
                        elemento.size.get(
                            "height",
                            0
                        )
                    )

                    if ancho >= 300 and alto >= 150:
                        candidatos.append(
                            {
                                "elemento": elemento,
                                "selector": selector,
                                "ancho": ancho,
                                "alto": alto,
                                "area": ancho * alto
                            }
                        )

                except Exception:
                    continue

        if not candidatos:
            logger.warning(
                "⚠️ No se encontró un contenedor del gráfico"
            )

            return None

        seleccionado = max(
            candidatos,
            key=lambda elemento: elemento["area"]
        )

        logger.info(
            "✅ Contenedor seleccionado: %s | %sx%s",
            seleccionado["selector"],
            seleccionado["ancho"],
            seleccionado["alto"]
        )

        return seleccionado["elemento"]

    def _esperar_visual_renderizado(
        self,
        nombre_visual
    ):
        timeout = 240
        inicio = time.time()
        ultimo_log = 0

        selectores = [
            "div.visualContainerHost",
            "div.visual-container",
            "div.visualContent",
            "[data-testid='visual-container']",
            "visual-container",
            "svg",
            "canvas"
        ]

        while time.time() - inicio < timeout:

            # Power BI puede redirigir temporalmente durante la carga
            url_actual = self.driver.current_url.lower()

            if (
                "signin" in url_actual
                or "singlesignon" in url_actual
            ):
                logger.info(
                    "⏳ Power BI continúa autenticando la sesión"
                )

                time.sleep(5)
                continue

            candidatos = []

            for selector in selectores:

                elementos = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector
                )

                for elemento in elementos:

                    try:
                        if not elemento.is_displayed():
                            continue

                        rect = self.driver.execute_script(
                            """
                            const r = arguments[0].getBoundingClientRect();

                            return {
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                top: Math.round(r.top),
                                left: Math.round(r.left)
                            };
                            """,
                            elemento
                        )

                        ancho = int(
                            rect.get("width", 0)
                        )

                        alto = int(
                            rect.get("height", 0)
                        )

                        # Umbral más flexible para visuales de barras
                        if ancho >= 180 and alto >= 100:

                            candidatos.append(
                                {
                                    "elemento": elemento,
                                    "selector": selector,
                                    "ancho": ancho,
                                    "alto": alto,
                                    "area": ancho * alto
                                }
                            )

                    except Exception:
                        continue

            if candidatos:

                candidato = max(
                    candidatos,
                    key=lambda item: item["area"]
                )

                logger.info(
                    "✅ Gráfico renderizado: %s | "
                    "Selector: %s | Tamaño: %sx%s",
                    nombre_visual,
                    candidato["selector"],
                    candidato["ancho"],
                    candidato["alto"]
                )

                # Devolver directamente el elemento encontrado
                return candidato["elemento"]

            tiempo_transcurrido = int(
                time.time() - inicio
            )

            # Evita llenar el log cada segundo
            if tiempo_transcurrido - ultimo_log >= 10:

                logger.info(
                    "⏳ Esperando renderizado de %s "
                    "(%s/%s segundos)",
                    nombre_visual,
                    tiempo_transcurrido,
                    timeout
                )

                ultimo_log = tiempo_transcurrido

            time.sleep(3)

        raise TimeoutError(
            "El gráfico no terminó de renderizarse: "
            f"{nombre_visual}"
        )

    def _precargar_informe_tendencias(self):
        logger.info("🔥 Precargando informe de tendencias")
        self.driver.get(POWERBI_URL_TENDENCIA_1)
        WebDriverWait(self.driver, 180).until(
            lambda driver: (
                "signin" not in driver.current_url.lower()
                and "singlesignon" not in driver.current_url.lower()
            )
        )
        logger.info("📄 Informe abierto para precarga: %s", self.driver.title)
        time.sleep(45)
        logger.info("✅ Precarga del informe finalizada")

    def _capturar_visual(self, url, archivo, nombre):
        ruta_final = os.path.join(REPORT_PATH_TENDENCIAS, archivo)
        ruta_temporal = os.path.join(REPORT_PATH_TENDENCIAS, f"temp_{archivo}")
        ruta_pantalla = os.path.join(REPORT_PATH_TENDENCIAS, f"pantalla_{archivo}")
        intentos = 3

        for intento in range(1, intentos + 1):
            try:
                logger.info(
                    "🌐 Capturando %s | Intento %s/%s",
                    nombre, intento, intentos
                )

                for ruta in (ruta_temporal, ruta_pantalla):
                    if os.path.isfile(ruta):
                        os.remove(ruta)

                self.driver.get(url)
                WebDriverWait(self.driver, 180).until(
                    lambda driver: (
                        "signin" not in driver.current_url.lower()
                        and "singlesignon" not in driver.current_url.lower()
                    )
                )

                logger.info("📄 Página cargada: %s", self.driver.title)
                time.sleep(25)
                self._cerrar_panel_filtros()
                time.sleep(5)

                self.driver.save_screenshot(ruta_pantalla)
                self._recortar_grafico_powerbi(
                    ruta_origen=ruta_pantalla,
                    ruta_destino=ruta_temporal,
                    nombre_visual=nombre,
                )
                self._validar_imagen_generada(ruta_temporal, nombre)

                # Solo sustituir la imagen anterior cuando la nueva sea válida.
                os.replace(ruta_temporal, ruta_final)
                logger.info("✅ Gráfico actualizado: %s", ruta_final)
                return ruta_final

            except Exception as error:
                logger.warning(
                    "⚠️ Intento %s/%s fallido para %s: %s",
                    intento, intentos, nombre, error
                )

                if intento < intentos:
                    logger.info("🔄 Recargando antes del siguiente intento")
                    self.driver.refresh()
                    time.sleep(15)
                    continue

                evidencia = os.path.join(
                    REPORT_PATH_TENDENCIAS,
                    f"error_{archivo}"
                )
                try:
                    self.driver.save_screenshot(evidencia)
                except Exception:
                    pass

                logger.error("❌ Falló definitivamente la captura de %s", nombre)
                logger.info("📸 Evidencia generada: %s", evidencia)

                if os.path.isfile(ruta_final) and os.path.getsize(ruta_final) > 0:
                    logger.warning(
                        "⚠️ Se utilizará la última captura válida: %s",
                        ruta_final
                    )
                    return ruta_final
                raise

            finally:
                for ruta in (ruta_temporal, ruta_pantalla):
                    if os.path.isfile(ruta):
                        try:
                            os.remove(ruta)
                        except OSError:
                            pass

    def _cargar_pagina_tendencia(
        self,
        url,
        nombre
    ):
        intentos = 3

        for intento in range(
            1,
            intentos + 1
        ):
            logger.info(
                "🌐 Cargando %s | Intento %s/%s",
                nombre,
                intento,
                intentos
            )

            self.driver.get(
                url
            )

            WebDriverWait(
                self.driver,
                180
            ).until(
                lambda driver: (
                    "signin"
                    not in driver.current_url.lower()
                    and "singlesignon"
                    not in driver.current_url.lower()
                )
            )

            time.sleep(20)

            try:
                visual = self._esperar_visual_renderizado(
                    nombre_visual=nombre
                )

                return visual

            except TimeoutError:

                if intento == intentos:
                    raise

                logger.warning(
                    "⚠️ %s no cargó correctamente. "
                    "Refrescando la página...",
                    nombre
                )

                self.driver.refresh()

                time.sleep(15)

        raise TimeoutError(
            f"No se pudo cargar el gráfico: {nombre}"
        )

    def capturar_tendencias(self):

        configuracion = [
            (
                POWERBI_URL_TENDENCIA_1,
                "01_Total_vs_Atendidos.png",
                "Total vs. Atendidos"
            ),
            (
                POWERBI_URL_TENDENCIA_2,
                "02_Pendientes.png",
                "Pendientes"
            ),
            (
                POWERBI_URL_TENDENCIA_3,
                "03_TMR.png",
                "TMR"
            ),
            (
                POWERBI_URL_TENDENCIA_4,
                "04_SLA.png",
                "SLA"
            )
        ]

        # Inicializa sesión, modelo semántico y recursos del informe.
        self._precargar_informe_tendencias()

        imagenes = []

        for url, archivo, nombre in configuracion:

            imagen = self._capturar_visual(
                url=url,
                archivo=archivo,
                nombre=nombre
            )

            imagenes.append(
                imagen
            )

        logger.info(
            "✅ Se generaron %s imágenes de tendencia",
            len(imagenes)
        )

        return imagenes

    def _recortar_grafico_powerbi(
        self,
        ruta_origen,
        ruta_destino,
        nombre_visual
    ):
        imagen = Image.open(
            ruta_origen
        )

        try:
            ancho, alto = imagen.size

            logger.info(
                "📐 Imagen original %s: %sx%s",
                nombre_visual,
                ancho,
                alto
            )

            # Recorte de la interfaz Power BI:
            # izquierda: panel de páginas
            # arriba: barra de acciones
            # derecha: márgenes/panel contraído
            # abajo: zoom y navegación
            izquierda = int(ancho * 0.180)
            arriba = int(alto * 0.100)
            derecha = int(ancho * 0.870)
            abajo = int(alto * 0.975)

            logger.info(
                "✂️ Recorte %s: (%s, %s, %s, %s)",
                nombre_visual,
                izquierda,
                arriba,
                derecha,
                abajo
            )

            grafico = imagen.crop(
                (
                    izquierda,
                    arriba,
                    derecha,
                    abajo
                )
            )

            grafico.save(
                ruta_destino,
                "PNG",
                optimize=True
            )

            grafico.close()

        finally:
            imagen.close()

    def _validar_imagen_generada(
        self,
        ruta_imagen,
        nombre_visual
    ):
        if not os.path.isfile(ruta_imagen):
            raise FileNotFoundError(
                f"No se creó la imagen: {ruta_imagen}"
            )

        if os.path.getsize(ruta_imagen) == 0:
            raise ValueError(
                f"La imagen está vacía: {ruta_imagen}"
            )

        with Image.open(ruta_imagen) as imagen:
            imagen_rgb = imagen.convert("RGB")

            ancho, alto = imagen_rgb.size

            if ancho < 300 or alto < 150:
                raise ValueError(
                    f"La captura de {nombre_visual} es demasiado pequeña: "
                    f"{ancho}x{alto}"
                )

            # Reducir temporalmente para analizar colores con rapidez
            muestra = imagen_rgb.resize(
                (
                    min(ancho, 200),
                    min(alto, 120)
                )
            )

            colores = muestra.getcolors(
                maxcolors=200 * 120
            )

            if colores:
                color_principal = max(
                    colores,
                    key=lambda item: item[0]
                )

                porcentaje_principal = (
                    color_principal[0]
                    / (
                        muestra.width
                        * muestra.height
                    )
                )

                # Si prácticamente toda la imagen es de un solo color,
                # probablemente Power BI quedó en blanco
                if porcentaje_principal >= 0.985:
                    raise ValueError(
                        f"La captura de {nombre_visual} parece estar en blanco"
                    )

        logger.info(
            "✅ Imagen validada: %s",
            ruta_imagen
        )

    def export_pdf(self):
        try:
            self._esperar_reporte(POWERBI_URL, "Dashboard principal")
            archivos_iniciales = set(os.listdir(REPORT_PATH))

            exportar = WebDriverWait(self.driver, 180).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Exportar']"))
            )
            self.driver.execute_script("arguments[0].click();", exportar)
            time.sleep(5)

            pdf_btn = WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[data-testid='export-to-pdf-btn']")
                )
            )
            self.driver.execute_script("arguments[0].click();", pdf_btn)

            confirmar = WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.ID, "okButton"))
            )
            self.driver.execute_script("arguments[0].click();", confirmar)
            logger.info("✅ Exportación PDF confirmada")
            return self._esperar_pdf(archivos_iniciales)
        except Exception:
            self.driver.save_screenshot(os.path.join(REPORT_PATH, "error_exportar.png"))
            raise

    def _esperar_pdf(self, archivos_iniciales):
        inicio = time.time()
        while time.time() - inicio <= 600:
            actuales = set(os.listdir(REPORT_PATH))
            nuevos = actuales - archivos_iniciales
            parciales = [f for f in nuevos if f.lower().endswith(".crdownload")]
            if parciales:
                logger.info("⏳ Descargando: %s", parciales)
            pdfs = [f for f in nuevos if f.lower().endswith(".pdf")]
            if pdfs:
                original = max(
                    pdfs,
                    key=lambda f: os.path.getmtime(os.path.join(REPORT_PATH, f)),
                )
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                destino = os.path.join(REPORT_PATH, f"Dashboard_MDA_{fecha}.pdf")
                os.replace(os.path.join(REPORT_PATH, original), destino)
                logger.info("✅ PDF renombrado: %s", destino)
                return destino
            time.sleep(2)
        raise TimeoutError("No se encontró un PDF nuevo en el tiempo máximo.")

    def _cerrar_panel_filtros(self):
        selectores = [
            "button[aria-label*='Cerrar panel de filtros']",
            "button[aria-label*='Collapse filters']",
            "button[title*='Cerrar']"
        ]

        for selector in selectores:
            elementos = self.driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for elemento in elementos:
                try:
                    if elemento.is_displayed():
                        self.driver.execute_script(
                            "arguments[0].click();",
                            elemento
                        )

                        logger.info(
                            "✅ Panel de filtros contraído"
                        )

                        return

                except Exception:
                    continue

    def close(self):
        if getattr(self, "driver", None):
            self.driver.quit()
