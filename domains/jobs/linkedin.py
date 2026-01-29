"""
Scraper de LinkedIn (Implementación de Estrategia)
--------------------------------------------------
Implementa IScraper para buscar empleos en LinkedIn.

# Patrón Strategy:
Esta clase es una "Estrategia" concreta de búsqueda.

# C# Equivalente:
# public class LinkedInScraper : IScraper { ... }
"""
import asyncio
import re
from typing import List
from urllib.parse import quote_plus, urljoin

from config.settings import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from core.interfaces import IScraper, JobResult, SearchResult
from core.browser import BrowserManager
from core.logger import setup_logger

logger = setup_logger("LinkedInScraper")

class LinkedInScraper(IScraper):
    
    BASE_URL = "https://www.linkedin.com/jobs/search/"
    
    async def search(self, query: str, **kwargs) -> List[SearchResult]:
        """
        Ejecuta la búsqueda en LinkedIn.
        kwargs soporta: 'location', 'max_results'.
        """
        location = kwargs.get("location", "")
        max_results = kwargs.get("max_results", 10)
        
        page = await BrowserManager.get_page()
        url = self._build_url(query, location)
        
        logger.info(f"Navegando a: {url}")
        
        results: List[SearchResult] = []
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2) # Espera humana
            
            # Selectores
            cards = await page.query_selector_all("div.job-search-results__list li")
            
            for i, card in enumerate(cards[:max_results]):
                try:
                    # Extracción básica (Simplificada para la demo de arquitectura)
                    title_el = await card.query_selector(".job-card-list__title")
                    company_el = await card.query_selector(".job-card-container__company-name")
                    link_el = await card.query_selector("a[href*='/jobs/view/']")
                    
                    if not title_el or not link_el:
                        continue
                        
                    title = (await title_el.inner_text()).strip()
                    company = (await company_el.inner_text()).strip() if company_el else "Confidencial"
                    href = await link_el.get_attribute("href")
                    
                    # Filtro de Easy Apply (Lógica visual)
                    easy_apply_el = await card.query_selector("li[data-test-id='easy-apply']")
                    is_easy_apply = easy_apply_el is not None
                    
                    # Convertir a Objeto de Dominio
                    job = JobResult(
                        title=title,
                        url=href,
                        source="LinkedIn",
                        company=company,
                        location=location,
                        is_easy_apply=is_easy_apply
                    )
                    results.append(job)
                    
                except Exception as e:
                    logger.error(f"Error parseando tarjeta {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error global en LinkedIn: {e}")
            
        await page.close()
        return results

    def _build_url(self, query: str, location: str) -> str:
        """Construye la URL con filtros."""
        params = [f"keywords={quote_plus(query)}"]
        if location:
            params.append(f"location={quote_plus(location)}")
        
        # Filtros Hardcoded (Requisito de negocio anterior)
        params.append("f_AL=true")      # Easy Apply
        params.append("f_TPR=r172800")  # Últimos 2 días
        
        qs = "&".join(params)
        return f"{self.BASE_URL}?{qs}"
