from functools import wraps
from flask import flash, redirect, request, url_for, render_template
from app.models import Item

def get_error_template(endpoint, **kwargs):
    """Return appropriate template based on endpoint with context."""
    if endpoint == 'main.add_item':
        return render_template('inventory/add.html')
    elif endpoint == 'main.edit_item':
        item_id = kwargs.get('id')
        item = Item.query.get_or_404(item_id)
        return render_template('inventory/edit.html', item=item)
    else:
        items = Item.query.filter(Item.quantity > 0).all()
        return render_template('borrower/create_slip.html', items=items)

def validate_quantity(quantity_str):
    """Validate quantity value and return tuple (is_valid, error_message)."""
    if not quantity_str:
        return False, 'Quantity is required'
        
    try:
        quantity = int(quantity_str)
        if quantity < 0:
            return False, 'Quantity must be positive'
        return True, None
    except ValueError:
        return False, 'Quantity must be a number'

def validate_item_quantity(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip validation for non-POST requests
        if request.method != 'POST':
            return f(*args, **kwargs)
            
        quantity = request.form.get('quantity')
        is_valid, error_message = validate_quantity(quantity)
        
        if not is_valid:
            flash(error_message, 'error')
            return get_error_template(request.endpoint, **kwargs)
            
        return f(*args, **kwargs)
    return decorated_function

def check_item_availability(item_id, requested_quantity):
    """Check if requested quantity is available for given item."""
    item = Item.query.get_or_404(item_id)
    if item.quantity < requested_quantity:
        return False, f'Not enough {item.name} in stock. Available: {item.quantity}'
    return True, None 