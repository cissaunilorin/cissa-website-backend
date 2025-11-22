# CISSA Website Backend

A robust backend service for the CISSA (Computer and Information Systems Student Association) web application, built with FastAPI and Python.

## 🚀 Features

- **Authentication**: Secure user authentication and management using JWT and Supabase.
- **Announcements**: Comprehensive CRUD operations for managing announcements.
- **Signatories**: Management of signatories for announcements.
- **Rate Limiting**: Built-in rate limiting to protect API endpoints using `slowapi`.
- **Database**: PostgreSQL integration with SQLAlchemy ORM and Alembic for migrations.
- **Documentation**: Auto-generated interactive API documentation (Swagger UI & ReDoc).

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (Recommended)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11 or higher
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (optional but recommended for faster dependency management)

## 🔧 Installation & Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd cissa-website-backend
   ```

2. **Set up environment variables**
   Copy the sample environment file and configure your variables:

   ```bash
   cp .env.sample .env
   ```

   Update `.env` with your database credentials, secret keys, and other configuration.

3. **Install dependencies**

   Initialize the environment and install dependencies:

   ```bash
   uv sync
   ```

4. **Database Setup**

   Create your local PostgreSQL database:

   ```sql
   CREATE DATABASE cissa_backend;
   ```

   Run migrations to set up the schema:

   ```bash
   uv run alembic upgrade head
   ```

## ⚡ Running the Application

Start the development server:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 7001
```

The API will be available at `http://localhost:7001`.

## 📖 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://localhost:7001/v1/docs](http://localhost:7001/v1/docs)
- **ReDoc**: [http://localhost:7001/v1/redoc](http://localhost:7001/v1/redoc)

## 🧪 Running Tests

Run the test suite using pytest:

```bash
uv run pytest
```

## 📂 Project Structure

```text
cissa-website-backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API endpoints and logic
│   │   ├── models/       # Database models
│   │   ├── repositories/ # Data access layer
│   │   ├── services/     # Business logic
│   │   └── v1/           # API Routers (Auth, Announcement, etc.)
│   ├── core/             # Application configuration
│   ├── db/               # Database connection
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── tests/                # Test suite
├── .env.sample           # Environment variables template
├── pyproject.toml        # Project dependencies and config
└── README.md             # Project documentation
```
