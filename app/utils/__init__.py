# Este archivo hace que 'utils' sea un paquete Python
# Imports de funciones comunes

from .dashboard import get_dashboard_stats, get_low_stock_alert
from .sales import process_sale, get_sale_details, cancel_sale
from .validators import validate_product_data, validate_user_data, validate_sale_data

# Puedes importar funciones específicas aquí para facilitar su uso
__all__ = [
    'get_dashboard_stats',
    'get_low_stock_alert', 
    'process_sale',
    'get_sale_details',
    'cancel_sale',
    'validate_product_data',
    'validate_user_data',
    'validate_sale_data'
]