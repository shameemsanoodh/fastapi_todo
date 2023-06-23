from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from pytz import timezone
import datetime

templates = Jinja2Templates(directory="./app_main/demo")


#import_routers
from app_main.router_users import router_users

app = FastAPI()


#include_router
app.include_router(router_users)


# mainapp.include_router(router)
@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request, "title": "WOBOT", "body_content": "FAST API IS READY USE /docs"})


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)
