from functools import wraps
from flask import request, flash
from .validators import QuantityValidator
from app.utils.template_utils import get_error_template

def validate_item_quantity(f):
    """Decorator to validate item quantity in forms."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method != 'POST':
            return f(*args, **kwargs)
            
        quantity = request.form.get('quantity')
        is_valid, error_message = QuantityValidator.validate(quantity)
        
        if not is_valid:
            flash(error_message, 'error')
            return get_error_template(request.endpoint, **kwargs)
            
        return f(*args, **kwargs)
    return decorated_function 