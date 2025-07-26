from fastapi import APIRouter, Response
from sqlmodel import desc, select

from inventory.db.connection import DBSession
from inventory.db.models import Log
from inventory.templates.private import RenderTemplate
from inventory.user import Staff

log_router = APIRouter(prefix="/log")


@log_router.get("/")
async def all_logs(_: Staff, db: DBSession, render_template: RenderTemplate) -> Response:
    logs = db.exec(select(Log).order_by(desc(Log.created_at))).all()
    return render_template("logs/all", {"logs": logs})
