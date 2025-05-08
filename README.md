# Team Management Application

A simple team management application built with FastAPI and HTMX.

## Features

- Create and view teams
- Add team members with roles
- Remove team members
- Real-time UI updates using HTMX

## Technologies

- FastAPI
- SQLite
- Jinja2 Templates
- HTMX

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   uvicorn app:app --reload
   ```
4. Access the application at http://localhost:8000

## Note

If port 8000 is already in use, you can specify a different port:
```
uvicorn app:app --port 8001 --reload
```