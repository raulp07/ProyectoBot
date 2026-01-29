"""
Interfaces Base del Sistema
---------------------------
Define los contratos que deben cumplir los módulos.

# C# Equivalente:
# public interface IScraper { ... }
# public interface INotifier { ... }
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from dataclasses import dataclass

# --- DTOs (Data Transfer Objects) ---
# Usamos dataclasses para pasar datos entre capas.

@dataclass
class SearchResult:
    """Clase base para resultados (Empleo, Producto, etc)."""
    title: str
    url: str
    source: str  # "LinkedIn", "Amazon", etc.

@dataclass
class JobResult(SearchResult):
    company: str
    location: str
    is_easy_apply: bool

@dataclass
class ProductResult(SearchResult):
    price: float
    currency: str
    image_url: str

# --- Interfaces ---

class IScraper(ABC):
    """
    Contrato que todo scraper debe seguir.
    
    # C# Equivalente:
    # public interface IScraper {
    #     Task<List<SearchResult>> SearchAsync(string query);
    # }
    """
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[SearchResult]:
        """
        Ejecuta una búsqueda.
        Args:
            query: Texto a buscar (ej. "iphone 15", ".net backend").
            kwargs: Filtros extra (location, min_price, etc).
        """
        pass

class INotifier(ABC):
    """
    Contrato para enviar mensajes (Telegram, WhatsApp).
    
    # C# Equivalente:
    # public interface INotifier {
    #     Task SendMessageAsync(string chatId, string text);
    # }
    """
    
    @abstractmethod
    async def send_message(self, chat_id: str, text: str) -> bool:
        pass
