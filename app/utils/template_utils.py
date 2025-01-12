from flask import render_template
from app.inventory.models import Item

def get_error_template(endpoint, **kwargs):
    """Return appropriate template based on endpoint with context."""
    templates = {
        'main.add_item': ('inventory/add.html', {}),
        'main.edit_item': ('inventory/edit.html', 
                          {'item': Item.query.get_or_404(kwargs.get('id'))}),
        'main.create_slip': ('borrowing/create_slip.html',
                            {'items': Item.query.filter(Item.quantity > 0).all()})
    }
    
    template, context = templates.get(endpoint, ('errors/404.html', {}))
    return render_template(template, **context) 