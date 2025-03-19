from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("inventory/templates")


def render_template(request: Request, name: str, context: dict[str, object]) -> Response:
    return templates.TemplateResponse(request, f"{name}.html.jinja", context)


def register_static_page(router: APIRouter, path: str, name: str) -> None:
    """`GET path` -> `inventory/templates/name.html.jinja`"""

    async def handle(request: Request) -> Response:
        return render_template(request, name, {})

    router.get(path)(handle)
