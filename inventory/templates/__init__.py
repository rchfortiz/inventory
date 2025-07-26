from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("inventory/templates")

Context = dict[str, object] | None
