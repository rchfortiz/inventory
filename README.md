# TLE Inventory System

A modern Flask-based inventory management system designed for tracking items and managing borrower records. Built with Python, Flask, and SQLAlchemy.

## Features

- 📦 Complete inventory management (CRUD operations)
- 📝 Borrower's slip generation
- 🔍 Item availability tracking
- 📊 Borrowing history
- ✨ Clean and intuitive interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/tle-inventory.git
   cd tle-inventory
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```sh
   pip install -e ".[dev]"
   ```

4. Initialize the database:

   ```sh
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Development

### Running the Application

```sh
flask run
# or
python run.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```tree
inventory_system/
├── app/
│   ├── inventory/          # Inventory management
│   │   ├── models.py
│   │   └── routes.py
│   ├── borrowing/         # Borrowing management
│   │   ├── models.py
│   │   └── routes.py
│   ├── utils/             # Utility functions
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   └── template_utils.py
│   ├── errors/           # Error handlers
│   └── templates/        # HTML templates
├── tests/               # Test files
└── config.py           # Configuration
```

## Core Features

### Inventory Management

- Add, update, and remove items
- Track item quantities
- View inventory list
- Item location tracking

### Borrowing System

- Create borrower's slips
- Track borrowed items
- Record returns
- View borrowing history

## Contributing

1. Fork the repository
2. Create a feature branch:

   ```sh
   git checkout -b feature/amazing-feature
   ```

3. Make your changes and commit:

   ```sh
   git commit -m 'Add amazing feature'
   ```

4. Push to your branch:

   ```sh
   git push origin feature/amazing-feature
   ```

5. Open a Pull Request

### Commit Guidelines

- Use descriptive commit messages
- Reference issues and pull requests
- Keep commits focused and atomic

## Acknowledgments

- Flask framework and its extensions
- SQLAlchemy ORM
- Bootstrap for UI components
- The open-source community

## Support

For support, please open an issue in the GitHub issue tracker.
