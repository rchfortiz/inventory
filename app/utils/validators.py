class QuantityValidator:
    """Validator for quantity inputs."""
    @staticmethod
    def validate(quantity_str):
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

class ItemAvailabilityChecker:
    """Checker for item availability."""
    @staticmethod
    def check(item, requested_quantity):
        """Check if requested quantity is available."""
        if item.quantity < requested_quantity:
            return False, f'Not enough {item.name} in stock. Available: {item.quantity}'
        return True, None 