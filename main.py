from typing import Annotated
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from data.database import database
from data.ariadna_repository import AriadnaRepository
from domain.netflix import Netflix
from starlette.middleware.sessions import SessionMiddleware
from router import juego_adivina, auth_route, admin_route, user_route, perfil_route
from utils.dependencies import require_auth
import uvicorn

app = FastAPI(title="CRUD FastAPI - Netflix")

# Configurar las plantillas
templates = Jinja2Templates(directory="templates")

# Configurar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key="tu_clave_secreta_muy_segura_cambiala_en_produccion",
    session_cookie="session",
    max_age=3600 * 24 * 7,  # 7 días
    same_site="lax",
    https_only=False  # Cambiar a True en producción con HTTPS
)

# Incluir el router del juego
app.include_router(juego_adivina.router)

# Incluir el router de autenticación
app.include_router(auth_route.router)

# Incluir el router de usuarios (insertar)
app.include_router(user_route.router)

# Incluir el router de perfil
app.include_router(perfil_route.router)

# Incluir el router de administración
app.include_router(admin_route.router)

# Manejador de excepciones para errores 403 y redirecciones de autenticación
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Redirigir al login si es error 303 (no autenticado)
    if exc.status_code == 303:
        return RedirectResponse(url=exc.headers.get("Location", "/login"), status_code=303)
    
    # Mostrar página 403 para acceso denegado
    if exc.status_code == 403:
        return templates.TemplateResponse("403.html", {
            "request": request,
            "message": exc.detail,
            "required_role": "Administrador",
            "current_role": "Usuario"
        }, status_code=403)
    
    # Para otros errores HTTP, comportamiento por defecto
    return RedirectResponse(url="/")

#RUTA RAIZ - Requiere autenticación
@app.get("/")
async def inicio(request: Request, usuario = Depends(require_auth)):
    """Página de inicio"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "usuario": usuario
    })




# RUTA VER - Requiere autenticación
@app.get("/netflix", response_class=HTMLResponse)
async def archivos(request: Request, usuario = Depends(require_auth)):
    """Listar todas las películas/series"""
    netflix_repo = AriadnaRepository(database)
    archivos = netflix_repo.get_all()
    return templates.TemplateResponse("netflix.html", {
        "request": request,
        "archivos": archivos,
        "usuario": usuario
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)