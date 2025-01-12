from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import db, Item, Borrower, BorrowedItem
from app.utils import validate_item_quantity, check_item_availability
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    recent_borrows = BorrowedItem.query.order_by(BorrowedItem.borrow_date.desc()).limit(5).all()
    return render_template('index.html', recent_borrows=recent_borrows)

# Item routes
@bp.route('/inventory')
def inventory_list():
    items = Item.query.all()
    return render_template('inventory/list.html', items=items)

@bp.route('/inventory/add', methods=['GET', 'POST'])
@validate_item_quantity
def add_item():
    if request.method == 'POST':
        try:
            item = Item(
                name=request.form['name'].strip(),
                quantity=int(request.form['quantity']),
                location=request.form['location'].strip(),
                description=request.form['description'].strip()
            )
            if not item.name:
                flash('Item name is required', 'error')
                return render_template('inventory/add.html')
                
            db.session.add(item)
            db.session.commit()
            flash('Item added successfully', 'success')
            return redirect(url_for('main.inventory_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'error')
            return render_template('inventory/add.html')
            
    return render_template('inventory/add.html')

@bp.route('/inventory/<int:id>/edit', methods=['GET', 'POST'])
@validate_item_quantity
def edit_item(id):
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        try:
            item.name = request.form['name'].strip()
            item.quantity = int(request.form['quantity'])
            item.location = request.form['location'].strip()
            item.description = request.form['description'].strip()
            
            if not item.name:
                flash('Item name is required', 'error')
                return render_template('inventory/edit.html', item=item)
                
            db.session.commit()
            flash('Item updated successfully', 'success')
            return redirect(url_for('main.inventory_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'error')
            return render_template('inventory/edit.html', item=item)
            
    return render_template('inventory/edit.html', item=item)

# Borrower routes
@bp.route('/borrow', methods=['GET', 'POST'])
@validate_item_quantity
def create_slip():
    if request.method == 'POST':
        try:
            # Validate borrower information
            borrower_name = request.form['borrower_name'].strip()
            contact = request.form['contact'].strip()
            
            if not borrower_name:
                flash('Borrower name is required', 'error')
                return redirect(url_for('main.create_slip'))
                
            # Check item availability
            item_id = request.form['item_id']
            quantity = int(request.form['quantity'])
            available, message = check_item_availability(item_id, quantity)
            
            if not available:
                flash(message, 'error')
                return redirect(url_for('main.create_slip'))
            
            # Create borrower and slip
            borrower = Borrower(name=borrower_name, contact=contact)
            db.session.add(borrower)
            
            borrowed_item = BorrowedItem(
                item_id=item_id,
                quantity=quantity,
                borrower=borrower,
                borrow_date=datetime.utcnow()
            )
            db.session.add(borrowed_item)
            
            # Update item quantity
            item = Item.query.get(item_id)
            item.quantity -= quantity
            
            db.session.commit()
            flash('Borrower slip created successfully', 'success')
            return redirect(url_for('main.view_slip', slip_id=borrowed_item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating borrower slip: {str(e)}', 'error')
            return redirect(url_for('main.create_slip'))
            
    items = Item.query.filter(Item.quantity > 0).all()
    return render_template('borrower/create_slip.html', items=items)

@bp.route('/slip/<int:slip_id>')
def view_slip(slip_id):
    slip = BorrowedItem.query.get_or_404(slip_id)
    return render_template('borrower/view_slip.html', slip=slip)

@bp.route('/slip/<int:slip_id>/return', methods=['POST'])
def return_item(slip_id):
    slip = BorrowedItem.query.get_or_404(slip_id)
    
    if slip.return_date:
        flash('This item has already been returned', 'error')
        return redirect(url_for('main.view_slip', slip_id=slip_id))
        
    try:
        slip.return_date = datetime.utcnow()
        slip.item.quantity += slip.quantity
        db.session.commit()
        flash('Item returned successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error returning item: {str(e)}', 'error')
        
    return redirect(url_for('main.view_slip', slip_id=slip_id)) 