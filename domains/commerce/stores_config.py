"""
Configuración de Tiendas (Store Registry)
-----------------------------------------
Define los selectores y URLs de cada tienda en un solo lugar.
Agregar una tienda nueva = agregar un diccionario aquí.

# C# Equivalente:
# Similar a un appsettings.json o un IOptions<StoreConfig>
# public class StoreConfig { public string BaseUrl; public Selectors Selectors; }
"""

STORES = {
    "MercadoLibre": {
        "base_url": "https://listado.mercadolibre.com.pe/{query}",
        "query_format": "replace_dash",  # Reemplaza espacios por guiones
        "selectors": {
            "item": "li.ui-search-layout__item",
            "title": "h2.ui-search-item__title, .poly-component__title",
            "link": "a.ui-search-link, a.poly-component__title",
            "price": "span.andes-money-amount__fraction, .poly-price__current .andes-money-amount__fraction",
            "image": "img.ui-search-result-image__element, img.poly-component__picture"
        }
    },
    "Falabella": {
        "base_url": "https://www.falabella.com.pe/falabella-pe/search?Ntt={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.pod-summary, div[id^='testId-pod-display']",
            "title": "b[id^='testId-pod-display-subTitle'], b.pod-subTitle, b[id^='testId-pod-display-title']",
            "link": "a.pod-link, a[href*='/product/']",
            "price": "li[data-pod-price-main] span, span[id^='testId-pod-display-sales-price']",
            "image": "img[src*='falabella.scene7.com']"
        }
    },
    "Promart": {
        "base_url": "https://www.promart.pe/busqueda?q={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.vtex-product-summary-2-x-element, div.shelf-item",
            "title": "span.vtex-product-summary-2-x-productBrand",
            "link": "a.vtex-product-summary-2-x-clearLink",
            "price": "span.promart-promart-components-0-x-currencyInteger, .vtex-product-price-1-x-sellingPriceValue",
            "image": "img.vtex-product-summary-2-x-imageNormal"
        }
    },
    "Oechsle": {
        "base_url": "https://www.oechsle.pe/search?text={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.product-item, div.product-tile",
            "title": "a.product-name, h3.product-name",
            "link": "a.product-name, a[href*='/p/']",
            "price": "span.price-value, span.sales-price",
            "image": "img.tile-image"
        }
    },
    "Ripley": {
        "base_url": "https://simple.ripley.com.pe/buscar?Ntt={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.catalog-product-item, div.ProductItem",
            "title": "a.catalog-product-name, div.catalog-product-details__name",
            "link": "a.catalog-product-item, a[href*='/product/']",
            "price": "li.catalog-prices__offer-price, span.catalog-product-details__price",
            "image": "img.catalog-product-image"
        }
    },
    "Linio": {
        "base_url": "https://www.linio.com.pe/search?scroll=&q={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.catalogue-product, div.product-card",
            "title": "a.catalogue-product__name, div.product-name",
            "link": "a.catalogue-product__name, a[href*='/p/']",
            "price": "span.price-main-md, span.catalogue-product__price",
            "image": "img.catalogue-product__image"
        }
    },
    "Sodimac": {
        "base_url": "https://www.sodimac.com.pe/sodimac-pe/search/?Ntt={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.jsx-product-row, div.product-pod",
            "title": "h3.jsx-product-name, span.product-title",
            "link": "a[href*='/product/']",
            "price": "span.jsx-price, span.price",
            "image": "img.jsx-product-image"
        }
    },
    "PlazaVea": {
        "base_url": "https://www.plazavea.com.pe/search/?_query={query}",
        "query_format": "replace_plus",
        "selectors": {
            "item": "div.vtex-product-summary-2-x-element, div.product-item",
            "title": "span.vtex-product-summary-2-x-productBrand",
            "link": "a.vtex-product-summary-2-x-clearLink",
            "price": "span.vtex-product-price-1-x-sellingPriceValue",
            "image": "img.vtex-product-summary-2-x-imageNormal"
        }
    }
}

def get_all_store_names() -> list:
    """Retorna la lista de nombres de tiendas disponibles."""
    return list(STORES.keys())
