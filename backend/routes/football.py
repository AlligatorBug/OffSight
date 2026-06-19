import csv
import io
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.db import get_db, CachedFixture, CachedSquad
from backend.services.football_api import FootballAPI, RateLimitError

router = APIRouter(prefix="/api")

SQUAD_TTL_HOURS = 24


def _get_api() -> FootballAPI:
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="API_FOOTBALL_KEY not configured")
    return FootballAPI(key)


def _is_stale(synced_at: datetime) -> bool:
    return datetime.now(timezone.utc) - synced_at > timedelta(hours=SQUAD_TTL_HOURS)


@router.get("/teams/search")
def search_teams(q: str):
    try:
        api = _get_api()
        return api.search_teams(q)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="API rate limit reached — try again tomorrow")


@router.get("/teams/{team_id}/fixtures")
def get_team_fixtures(team_id: int):
    try:
        api = _get_api()
        return api.get_team_fixtures(team_id)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="API rate limit reached — try again tomorrow")


@router.get("/fixtures/{fixture_id}/squads")
def get_fixture_squads(fixture_id: int, db: Session = Depends(get_db)):
    cached: CachedSquad | None = db.get(CachedSquad, fixture_id)

    if cached and not _is_stale(cached.synced_at):
        return {"data": cached.data, "synced_at": cached.synced_at.isoformat()}

    try:
        api = _get_api()
        players = api.get_fixture_lineups(fixture_id)
    except RateLimitError:
        if cached:
            return {"data": cached.data, "synced_at": cached.synced_at.isoformat()}
        raise HTTPException(status_code=429, detail="API rate limit reached — try again tomorrow")

    now = datetime.now(timezone.utc)
    if cached:
        cached.data = players
        cached.synced_at = now
    else:
        db.add(CachedSquad(fixture_id=fixture_id, data=players, synced_at=now))
    db.commit()

    return {"data": players, "synced_at": now.isoformat()}


@router.post("/squads/manual")
async def upload_squad_csv(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")

    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]

    if "number" not in (reader.fieldnames or []) or "name" not in (reader.fieldnames or []):
        raise HTTPException(status_code=400, detail="CSV must have 'number' and 'name' columns")

    players = []
    for row in reader:
        number = row.get("number", "").strip()
        name = row.get("name", "").strip()
        if number and name:
            players.append({
                "number": int(number),
                "name":   name,
                "side":   row.get("team", row.get("side", "")).strip().lower() or None,
            })

    return {"data": players, "synced_at": None}
