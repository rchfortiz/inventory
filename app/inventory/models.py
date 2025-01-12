from app import db

class Item(db.Model):
    """Model representing inventory items."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    borrowed_items = db.relationship('BorrowedItem', backref='item', lazy=True)

    def __repr__(self):
        return f'<Item {self.name}>'

    def update_quantity(self, amount):
        """Update item quantity and validate it's not negative."""
        new_quantity = self.quantity + amount
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity = new_quantity 