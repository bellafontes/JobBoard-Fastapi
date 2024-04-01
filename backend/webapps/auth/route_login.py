from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.version1.route_login import login_for_access_token
from db.session import get_db
from webapps.auth.forms import LoginForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request):
    x = request.cookies.get("access_token")
    print("ja tem acesso??", x)
    if x:
        print("ja ta logado!")
        return RedirectResponse(url="/home")
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    print("ja tem acesso??", request.cookies.get("access_token"))

    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = templates.TemplateResponse("auth/login.html", form.__dict__)
            payload = login_for_access_token(response=response, form_data=form, db=db)
            print(f"DEU BOA! payload: {payload}")
            access_token = payload.get("access_token")
            print(access_token)
            r = RedirectResponse(url="/home", status_code=303)
            r.set_cookie(
                key="access_token", value=f"Bearer {access_token}", httponly=True
            )
            return r

            # return RedirectResponse(url="/home", status_code=307)

            # return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)

    return templates.TemplateResponse("auth/login.html", form.__dict__)


@router.get("/logout")
def logout(
        request: Request,
        db: Session = Depends(get_db),
        # response: Response,

):
    x = request.cookies.keys()
    access_token = request.cookies.get("access_token")
    print(f"logout ===> {access_token}")
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie(key ='access_token')
    return response
