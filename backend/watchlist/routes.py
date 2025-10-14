from fastapi import APIRouter, HTTPException, Query
from typing import List
import re
from .db import (
    create_watchlist,
    get_watchlist,
    update_watchlist,
    delete_watchlist,
    list_watchlists,
    init_db,
)
from .schemas import WatchlistIn, WatchlistOut, WatchlistImport, ImportResponse

router = APIRouter()


def parse_symbols_text(text: str, delimiter: str = "auto") -> List[str]:
    """Parse symbols din text cu auto-detection"""
    if delimiter == "auto":
        # Auto-detect: split by common separators
        symbols = re.split(r"[,;\n\t\s]+", text)
    elif delimiter == ",":
        symbols = text.split(",")
    elif delimiter == ";":
        symbols = text.split(";")
    elif delimiter == "\\n":
        symbols = text.split("\n")
    else:
        symbols = [text]

    # Clean și filter empty
    return [s.strip() for s in symbols if s.strip()]


@router.on_event("startup")
async def startup():
    try:
        await init_db()
    except Exception as e:
        print(f"⚠️  Watchlist DB initialization failed (MongoDB not available): {e}")


@router.post("/", response_model=WatchlistOut)
async def create(watchlist: WatchlistIn):
    try:
        doc = await create_watchlist(
            watchlist.name, watchlist.symbols, watchlist.description
        )
        return WatchlistOut(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description"),
            symbols=doc["symbols"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=409, detail=f"Watchlist '{watchlist.name}' already exists"
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{name}", response_model=WatchlistOut)
async def get_by_name(name: str):
    doc = await get_watchlist(name)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")

    return WatchlistOut(
        id=doc["_id"],
        name=doc["name"],
        description=doc.get("description"),
        symbols=doc["symbols"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.put("/{name}", response_model=WatchlistOut)
async def update_by_name(name: str, watchlist: WatchlistIn, mode: str = Query("merge")):
    try:
        doc = await update_watchlist(name, watchlist.symbols, mode)
        return WatchlistOut(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description"),
            symbols=doc["symbols"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[WatchlistOut])
async def list_all(limit: int = Query(50, le=100)):
    docs = await list_watchlists(limit)
    return [
        WatchlistOut(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description"),
            symbols=doc["symbols"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
        for doc in docs
    ]


@router.delete("/{name}")
async def delete_by_name(name: str):
    success = await delete_watchlist(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")
    return {"message": f"Watchlist '{name}' deleted"}


@router.post("/import", response_model=ImportResponse)
async def import_watchlist(req: WatchlistImport):
    try:
        # Parse symbols
        symbols = parse_symbols_text(req.symbols_text, req.delimiter)

        # Get existing
        existing_doc = await get_watchlist(req.name)
        existing_count = len(existing_doc["symbols"]) if existing_doc else 0

        # Update/create
        doc = await update_watchlist(req.name, symbols, req.mode)

        if not existing_doc:
            # Created new
            inserted = len(doc["symbols"])
            updated = 0
        elif req.mode == "replace":
            # Replaced
            inserted = 0
            updated = len(doc["symbols"])
        else:
            # Merged
            inserted = len(doc["symbols"]) - existing_count
            updated = existing_count

        return ImportResponse(
            name=req.name,
            inserted=max(0, inserted),
            updated=max(0, updated),
            symbols=doc["symbols"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
