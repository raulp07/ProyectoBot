"""
Motor Genérico de Scraping (Generic Scraper Engine)
---------------------------------------------------
Un solo scraper que funciona para cualquier tienda usando la configuración.

# Patrón Template Method:
La lógica de scraping es la misma, solo cambian los selectores.

# C# Equivalente:
# public class GenericScraper<TConfig> : IScraper where TConfig : IStoreConfig
"""
import asyncio
import re
from typing import List, Dict, Any

from core.interfaces import ProductResult, SearchResult
from core.browser import BrowserManager
from core.logger import setup_logger

logger = setup_logger("GenericScraper")

class GenericProductScraper:
    """
    Scraper configurable que funciona para cualquier tienda.
    
    Uso:
        config = STORES["MercadoLibre"]
        scraper = GenericProductScraper("MercadoLibre", config)
        results = await scraper.search("iphone 15")
    """
    
    def __init__(self, store_name: str, config: Dict[str, Any]):
        self.store_name = store_name
        self.config = config
        self.selectors = config["selectors"]
    
    def _format_query(self, query: str) -> str:
        """Formatea el query según el tipo de URL de la tienda."""
        fmt = self.config.get("query_format", "replace_plus")
        if fmt == "replace_dash":
            return query.replace(" ", "-")
        return query.replace(" ", "+")
    
    def _build_url(self, query: str) -> str:
        """Construye la URL de búsqueda."""
        formatted = self._format_query(query)
        return self.config["base_url"].format(query=formatted)
    
    def _clean_price(self, text: str) -> float:
        """Limpia el texto de precio y lo convierte a float."""
        if not text:
            return 0.0
        clean = text.replace("$", "").replace("S/", "").replace("S/.", "").strip()
        clean = clean.replace(".", "").replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return 0.0
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Ejecuta la búsqueda usando la configuración de la tienda.
        """
        url = self._build_url(query)
        logger.info(f"[{self.store_name}] Buscando: {url}")
        
        page = await BrowserManager.get_page()
        results: List[SearchResult] = []
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)  # Espera humana
            
            # Buscar items usando el selector configurado
            items = await page.query_selector_all(self.selectors["item"])
            logger.info(f"[{self.store_name}] Encontrados {len(items)} items con selector: {self.selectors['item']}")
            
            if len(items) == 0:
                # Debug: guardar screenshot para ver qué pasó
                logger.warning(f"[{self.store_name}] No se encontraron items. Puede ser captcha o selector incorrecto.")
            
            for i, item in enumerate(items[:max_results]):
                try:
                    # Título (obligatorio)
                    title_el = await item.query_selector(self.selectors["title"])
                    if not title_el:
                        continue
                    title = (await title_el.inner_text()).strip()
                    
                    # Link
                    link_el = await item.query_selector(self.selectors["link"])
                    href = await link_el.get_attribute("href") if link_el else ""
                    if href and not href.startswith("http"):
                        # Construir URL absoluta
                        base = self.config["base_url"].split("/")[0:3]
                        href = "/".join(base) + href
                    
                    # Precio
                    price_el = await item.query_selector(self.selectors["price"])
                    price_text = (await price_el.inner_text()).strip() if price_el else "0"
                    price = self._clean_price(price_text)
                    
                    # Imagen
                    img_el = await item.query_selector(self.selectors["image"])
                    img_src = await img_el.get_attribute("src") if img_el else ""
                    
                    if title:
                        results.append(ProductResult(
                            title=title,
                            url=href,
                            source=self.store_name,
                            price=price,
                            currency="PEN",
                            image_url=img_src
                        ))
                        
                except Exception as e:
                    # Continuar con el siguiente item si hay error
                    continue
                    
        except Exception as e:
            logger.error(f"[{self.store_name}] Error: {e}")
            
        await page.close()
        return results
