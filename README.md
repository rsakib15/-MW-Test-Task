# MW-Test-Task

Weather application with FastAPI
This project is a FastAPI application that interacts with a PostgreSQL database and runs in a Docker environment. The setup includes asynchronous database access using SQLAlchemy and `asyncpg`.

## Features
- RESTful API built with FastAPI.
- Asynchronous database operations with PostgreSQL.
- Dockerized environment for easy deployment.

## Technologies Used
- **FastAPI**: Modern web framework for Python.
- **PostgreSQL**: Relational database.
- **SQLAlchemy**: ORM for database management.
- **asyncpg**: Async driver for PostgreSQL.
- **Docker Compose**: Orchestrates multi-container Docker applications.


## Getting Started
Follow these steps to get the application up and running:

### Prerequisites
- Docker and Docker Compose installed on your machine.

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/rsakib15/-MW-Test-Task.git
   cd -MW-Test-Task
2. **Setup envrionment variable**
   ```bash
   DATABASE_URL=your_database_url
3. **Build and start the application**
    ```bash
    docker compose up
### API Endpoints

```bash
   GET /weather: Get weather data
