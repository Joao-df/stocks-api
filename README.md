# Stocks API

![License](https://img.shields.io/github/license/Joao-df/stocks-api)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Build Status](https://github.com/Joao-df/stocks-api/actions/workflows/ci.yml/badge.svg)


**Description**: This project is an API for querying and managing stock data, developed as a technical assignment for the company CIAL.


## Table of Contents

- [Stocks API](#stocks-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Key Technologies](#key-technologies)
  - [Installation and Setup](#installation-and-setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Unit Tests](#unit-tests)
  - [Usage](#usage)
  - [Main Endpoints](#main-endpoints)
  - [Notes](#notes)
  - [Pre-commit](#pre-commit)
    - [Installation](#installation-1)
    - [Configured Hooks](#configured-hooks)
    - [Usage](#usage-1)
  - [License](#license)

## Overview

This API is built using **FastAPI** and Docker, with support for Redis caching, PostgreSQL as a database, and data scraping via Selenium. The modular architecture enables the management of stock-related data, such as purchases and price lookups, with detailed logs on the response time for each request.

### Key Technologies

- FastAPI: Asynchronous API framework
- PostgreSQL: Relational database
- Redis: Cache for performance improvement
- Docker: Containerization for easier deployment
- Selenium: Data scraping tool
- Alembic: Database version control

## Installation and Setup

### Prerequisites

- Python 3.11+ (optional, in case you want to run it outside of containers)
- Docker and Docker Compose

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/username/stocks-api.git
   cd stocks-api
   ```

2. Create a `.env` file with the required environment variables (see `.env.example` for guidance).

3. To run with Docker Compose in **production mode**, use the `prod` profile to apply migrations and start the complete application:

   ```
   docker-compose --profile prod up --build
   ```

   The application will be available at `http://localhost:8000`.

4. To run in **development mode**, start Docker Compose without the `prod` profile. This will start only the dependencies (Redis, PostgreSQL, and Selenium remote driver), allowing the API to be run locally, outside containers:
   ```
   docker-compose up
   ```
   Then, install the dependencies:
   ```
   poetry install
   ```
   Then, start the API:
   ```
   poetry run fastapi dev .\app\main.py
   ```

### Unit Tests

To run unit tests, use the following command:

```
poetry run pytest --cov=.
```

## Usage

To use the API, visit the FastAPI auto-generated documentation at:

- `http://localhost:8000/docs` for Swagger UI
- `http://localhost:8000/redoc` for Redoc

You will find detailed information about endpoints, parameters, and usage examples.

## Main Endpoints

- **POST /stock/{stock_symbol}**: Registers a stock purchase
- **GET /stock/{stock_symbol}**: Details for a specific stock

## Notes

- Docker Compose includes an instance of **selenium/standalone-chrome** configured as a remote driver, enabling the use of Selenium for data scraping.
- Integrated middleware logs the execution time for each request, making performance monitoring easier.

## Pre-commit

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality and standardization before each commit. Make sure you have `pre-commit` installed and configured in your environment so that the hooks run automatically.

### Installation

To set up the hooks defined in `.pre-commit-config.yaml`, use:

```bash
pre-commit install
```

### Configured Hooks

- **Ruff**:
  - `ruff`: Checks code for linting issues.
  - `ruff-format`: Automatically formats the code according to defined rules.
- **Commitizen**:
  - Ensures commit messages follow a specific convention, helping maintain a consistent change history and facilitating changelog generation.

### Usage

The hooks will run automatically before each commit. You can also run them manually on all files with:

```bash
pre-commit run --all-files
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
