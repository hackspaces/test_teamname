from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from . import models
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Team Name Application")

# Configure templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    return templates.TemplateResponse("index.html", {"request": request, "teams": teams})

@app.post("/teams", response_class=HTMLResponse)
async def create_team(
    request: Request,
    team_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if team already exists
    existing_team = db.query(models.Team).filter(models.Team.name == team_name).first()
    if existing_team:
        teams = db.query(models.Team).all()
        return templates.TemplateResponse(
            "partials/team_list.html", 
            {"request": request, "teams": teams, "error": "Team already exists"}
        )
    
    # Create new team
    new_team = models.Team(name=team_name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    teams = db.query(models.Team).all()
    return templates.TemplateResponse(
        "partials/team_list.html", 
        {"request": request, "teams": teams}
    )

@app.get("/teams/{team_id}", response_class=HTMLResponse)
async def get_team(request: Request, team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return templates.TemplateResponse(
        "team_detail.html", 
        {"request": request, "team": team}
    )

@app.post("/teams/{team_id}/members", response_class=HTMLResponse)
async def add_team_member(
    request: Request,
    team_id: int,
    member_name: str = Form(...),
    db: Session = Depends(get_db)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    new_member = models.TeamMember(name=member_name, team_id=team_id)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return templates.TemplateResponse(
        "partials/member_list.html", 
        {"request": request, "team": team}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)