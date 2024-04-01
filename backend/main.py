from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apis.base import api_router
from core.config import settings
from db.base import Base
from db.session import engine
from db.utils import check_db_connected
from db.utils import check_db_disconnected
from webapps.base import api_router as web_app_router

templates = Jinja2Templates(directory="templates")


async def custom_404_handler(request, __):
    print("xiiiiiiiiiiii, 404")
    return templates.TemplateResponse("auth/404.html", {"request": request})


async def custom_401_handler(request: Request, __):
    print("xiiiiiiiiiiii, 401")
    return templates.TemplateResponse("auth/404.html", {"request": request})


def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_exception_handler(404, custom_404_handler)
    app.add_exception_handler(401, custom_401_handler)
    include_router(app)
    configure_static(app)
    create_tables()
    return app


app = start_application()


@app.on_event("startup")
async def app_startup():
    await check_db_connected()


@app.on_event("shutdown")
async def app_shutdown():
    await check_db_disconnected()
