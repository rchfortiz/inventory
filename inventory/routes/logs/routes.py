from fastapi import APIRouter, Depends, Response
from sqlmodel import desc, select

from inventory.db.connection import DBSessionDep
from inventory.db.models import Log
from inventory.frontend import RenderTemplate
from inventory.routes.auth.dependencies import get_user

logs_router = APIRouter(prefix="/logs", dependencies=[Depends(get_user)])


@logs_router.get("/")
async def all_logs(db: DBSessionDep, render_template: RenderTemplate) -> Response:
    logs = db.exec(select(Log).order_by(desc(Log.created_at))).all()
    return render_template("logs/all", {"logs": logs})
