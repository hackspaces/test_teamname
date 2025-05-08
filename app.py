from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import sqlite3
import os

# Initialize FastAPI application
app = FastAPI(title="Team Management")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database initialization
DB_NAME = "teams.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        """)
        conn.commit()
        conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()

# Database helper functions
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_teams():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY name")
    teams = cursor.fetchall()
    conn.close()
    return teams

def get_team(team_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cursor.fetchone()
    conn.close()
    return team

def get_team_members(team_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_members WHERE team_id = ? ORDER BY name", (team_id,))
    members = cursor.fetchall()
    conn.close()
    return members

# Routes
@app.get("/")
async def index(request: Request):
    teams = get_teams()
    return templates.TemplateResponse("index.html", {"request": request, "teams": teams})

@app.post("/teams")
async def add_team(request: Request, name: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    
    teams = get_teams()
    return templates.TemplateResponse("partials/teams_list.html", {"request": request, "teams": teams})

@app.get("/teams/{team_id}")
async def view_team(request: Request, team_id: int):
    team = get_team(team_id)
    if not team:
        return Response("Team not found", status_code=404)
    
    members = get_team_members(team_id)
    return templates.TemplateResponse(
        "partials/team_detail.html", 
        {"request": request, "team": team, "members": members}
    )

@app.post("/teams/{team_id}/members")
async def add_team_member(
    request: Request, 
    team_id: int, 
    name: str = Form(...), 
    role: str = Form(...)
):
    team = get_team(team_id)
    if not team:
        return Response("Team not found", status_code=404)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO team_members (name, role, team_id) VALUES (?, ?, ?)", 
        (name, role, team_id)
    )
    conn.commit()
    conn.close()
    
    members = get_team_members(team_id)
    return templates.TemplateResponse(
        "partials/members_list.html", 
        {"request": request, "team": team, "members": members}
    )

@app.delete("/members/{member_id}")
async def delete_team_member(request: Request, member_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get team_id before deleting
    cursor.execute("SELECT team_id FROM team_members WHERE id = ?", (member_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return Response("Member not found", status_code=404)
    
    team_id = result["team_id"]
    
    # Delete the member
    cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    
    team = get_team(team_id)
    members = get_team_members(team_id)
    return templates.TemplateResponse(
        "partials/members_list.html", 
        {"request": request, "team": team, "members": members}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)