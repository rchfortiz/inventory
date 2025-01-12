# TLE Inventory System Specification

## 1. Core Features

- Item management (CRUD operations)
- Borrower's slip generation
- Data persistence (CSV/JSON/SQLite)
- Simple text-based UI (optional: Tkinter GUI)

## 2. Data Model

- Item: ID, name, quantity, location, description
- Borrower: ID, name, contact, borrowed items

## 3. Implementation Requirements

### Storage

- File-based storage (CSV/JSON) or SQLite database
- Data validation and error handling

### User Interface

- Command-line menu system
- Input validation
- Clear error messages

### Core Functions

- Inventory management (add/view/edit/delete)
- Generate borrower's slip
- Search and filter items
- Basic reporting

## 4. Testing & Documentation

- Unit tests for CRUD operations
- User documentation
- Code comments
- System demo
