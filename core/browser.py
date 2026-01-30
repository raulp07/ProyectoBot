"""
Fachada del Navegador (Browser Facade)
--------------------------------------
Encapsula la complejidad de Playwright. Los scrapers usan esto en vez de llamar a Playwright directo.

# Patrón Facade:
Provee una interfaz simplificada para una librería compleja.

# C# Equivalente:
# public class BrowserService : IBrowserService {
#     private IPlaywright _playwright;
#     public async Task<string> GetContentAsync(string url) { ... }
# }
"""
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config.settings import BROWSER_HEADLESS
from core.logger import setup_logger

logger = setup_logger("BrowserFacade")

class BrowserManager:
    """ Singleton que maneja la instancia del navegador. """
    _instance = None
    _browser: Optional[Browser] = None
    _playwright = None

    @classmethod
    async def get_page(cls) -> Page:
        """
        Obtiene una nueva página lista para navegar.
        Si el navegador no está encendido, lo enciende.
        """
        if not cls._browser:
            logger.info("Iniciando motor Chromium...")
            cls._playwright = await async_playwright().start()
            
            # Anti-detect args más fuertes para la nube
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certifcate-errors",
                "--ignore-certifcate-errors-spki-list",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            cls._browser = await cls._playwright.chromium.launch(
                headless=BROWSER_HEADLESS,
                args=args
            )
            logger.info("Navegador iniciado.")

        # Contexto nuevo por cada página (cookies aisladas si quisiéramos)
        # --- Simulación de iPhone para saltar bloqueos ---
        context = await cls._browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            has_touch=True,
            locale="es-PE",
            timezone_id="America/Lima",
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Inyectamos sigilo adicional
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        return page

    @classmethod
    async def close(cls):
        """ Apaga todo. """
        if cls._browser:
            await cls._browser.close()
        if cls._playwright:
            await cls._playwright.stop()
        cls._browser = None
        cls._playwright = None
