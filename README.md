# Inventory

An inventory management system.

## Usage

### Docker Compose (recommended)

1. Ensure [Docker](https://docker.com/) and [Docker Compose](https://docs.docker.com/compose/) are installed.
2. Clone this repository.
3. Run `docker compose up`

Visit the site at http://localhost:1773. Data will be stored in a Docker volume named `data`.

### From source

1. Ensure [uv](https://docs.astral.sh/uv/) is installed.
2. Clone this repository.
3. Run `uv run -m inventory`.
