"""
Registro de Scrapers (Scraper Registry)
---------------------------------------
Provee una forma fácil de obtener todos los scrapers configurados.

# Patrón Factory:
Crea instancias de GenericProductScraper para cada tienda registrada.

# C# Equivalente:
# public class ScraperFactory {
#     public static IEnumerable<IScraper> GetAllScrapers() { ... }
# }
"""
from typing import List
from .stores_config import STORES, get_all_store_names
from .engine import GenericProductScraper

def get_all_scrapers() -> List[GenericProductScraper]:
    """
    Retorna una lista de scrapers, uno por cada tienda configurada.
    
    Uso:
        scrapers = get_all_scrapers()
        for scraper in scrapers:
            results = await scraper.search("laptop")
    """
    scrapers = []
    for name in get_all_store_names():
        config = STORES[name]
        scrapers.append(GenericProductScraper(name, config))
    return scrapers

def get_scraper_by_name(store_name: str) -> GenericProductScraper:
    """
    Retorna un scraper específico por nombre.
    
    Uso:
        meli = get_scraper_by_name("MercadoLibre")
        results = await meli.search("iphone")
    """
    if store_name not in STORES:
        raise ValueError(f"Tienda '{store_name}' no encontrada. Disponibles: {get_all_store_names()}")
    return GenericProductScraper(store_name, STORES[store_name])
