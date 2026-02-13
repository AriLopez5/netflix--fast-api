from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from data.database import database
from data.ariadna_repository import AriadnaRepository
from domain.netflix import Netflix
from utils.session import obtener_usuario_actual


def verificar_admin(request: Request):

    usuario = obtener_usuario_actual(request)
    
    # Si no hay sesión, redirigir al login
    if not usuario:
        raise HTTPException(
            status_code=303,
            detail="Debe iniciar sesión",
            headers={"Location": "/login"}
        )
    
    # Si no es admin, lanzar error 403
    if usuario.username != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: Solo administradores"
        )
    
    return usuario

# Crear el router con la dependencia verificar_admin aplicada a todas las rutas
router = APIRouter(dependencies=[Depends(verificar_admin)])
templates = Jinja2Templates(directory="templates")

# RUTA BORRAR - Solo admin
@router.get("/borrar_netflix")
async def borrar_netflix(request: Request):
    """Página de navegación con enlaces - Solo admin"""
    netflix_repo = AriadnaRepository(database)
    netflix = netflix_repo.get_all()

    return templates.TemplateResponse("borrar_netflix.html", {"request": request,"netflix": netflix
})

# RUTA BORRADO - Solo admin
@router.post("/do_borrar_netflix")
async def do_borrar_netflix(request: Request,
                              id : Annotated[str, Form()]):
    """Página de navegación con enlaces - Solo admin"""
    netflix_repo = AriadnaRepository(database)
    netflix_repo.borrar_netflix(int(id))
    return templates.TemplateResponse("do_borrar_netflix.html", {"request": request})

# RUTA EDITAR - Solo admin
@router.get("/edit_netflix")
async def edit_netflix(request: Request):
    """Página de navegación con enlaces - Solo admin"""
    netflix_repo = AriadnaRepository(database)
    netflix = netflix_repo.get_all()

    return templates.TemplateResponse("edit_netflix.html", {"request": request,"netflix": netflix
})

# RUTA EDITADO - Solo admin
@router.post("/do_edit_netflix")
async def do_edit_netflix(request: Request,
                              id: Annotated[str, Form()],
                              tipo: Annotated[str, Form()],
                              nombre: Annotated[str, Form()],
                              genero: Annotated[str, Form()] = None,
                              calificacion: Annotated[float, Form()] = None,
                              nota: Annotated[str, Form()] = None,
                              ):
    """Página de navegación con enlaces - Solo admin"""
    netflix_repo = AriadnaRepository(database)
    calificacion_int = int(calificacion) if calificacion is not None else None
    netflix = Netflix(int(id), tipo, nombre, genero, calificacion_int)
    netflix_repo.actualizar_netflix(netflix)
    return templates.TemplateResponse("do_edit_netflix.html", {"request": request})