from datetime import datetime
from app import db

class Borrower(db.Model):
    """Model representing borrowers."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    borrowed_items = db.relationship('BorrowedItem', backref='borrower', lazy=True)

    def __repr__(self):
        return f'<Borrower {self.name}>'

class BorrowedItem(db.Model):
    """Model representing borrowed items."""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<BorrowedItem {self.id}>'

    def return_item(self):
        """Mark item as returned and update inventory."""
        if self.return_date:
            raise ValueError("Item already returned")
        self.return_date = datetime.utcnow()
        self.item.update_quantity(self.quantity) 