from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Optional
from data.database import database
from data.ariadna_repository import AriadnaRepository
from data.valoracion_repository import ValoracionRepository
from domain.netflix import Netflix
from domain.model.Valoracion import Valoracion
from utils.dependencies import require_auth
from utils.session import obtener_usuario_actual

# Crear el router con autenticación requerida (cualquier usuario autenticado puede insertar)
router = APIRouter(dependencies=[Depends(require_auth)])
templates = Jinja2Templates(directory="templates")

# RUTA INSERTAR - Cualquier usuario autenticado
@router.get("/insert_netflix")
async def insert_netflix(request: Request):
    """Formulario para insertar película/serie - Cualquier usuario autenticado"""
    return templates.TemplateResponse("insert_netflix.html", {"request": request})

# RUTA INSERTADO - Cualquier usuario autenticado
@router.post("/do_insertar_netflix", response_class=HTMLResponse)
def do_insertar_netflix(request: Request, tipo: str = Form(...), nombre: str = Form(...), 
                       genero: str = Form(...), calificacion: str = Form(...), 
                       nota: str = Form(...)):
    
    session_data = request.session
    user_id = session_data.get('user_id')
    
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Convertir calificacion a int
        calificacion_int = int(float(calificacion))
        
        # Crear objeto Netflix
        netflix = Netflix(None, tipo, nombre, genero, calificacion_int)
        
        # Intentar insertar en Netflix
        ariadna_repository = AriadnaRepository(database)
        pelicula_id = ariadna_repository.insertar_netflix(netflix)
        
        # Si no se insertó (ID es 0 o None), buscar si ya existe
        if not pelicula_id:
            existing = ariadna_repository.buscar_por_nombre(nombre)
            if existing:
                pelicula_id = existing.id
            else:
                print(f"Error: No se pudo insertar ni encontrar la película '{nombre}'")
        
        # Crear valoración solo si tenemos pelicula_id
        if pelicula_id:
            valoracion = Valoracion(None, user_id, pelicula_id, int(calificacion), nota)
            valoracion_repo = ValoracionRepository(database)
            valoracion_repo.insertar_valoracion(valoracion)
        
        return RedirectResponse(url="/perfil", status_code=303)
        
    except Exception as e:
        print(f"Error en do_insertar_netflix: {str(e)}")
        return RedirectResponse(url="/insert_netflix", status_code=303)


# RUTA EDITAR - Usuario puede editar solo sus valoraciones
@router.get("/edit_netflix")
async def edit_valoracion_usuario(request: Request):
    """Muestra las valoraciones del usuario para editar - NO edita películas"""
    usuario = obtener_usuario_actual(request)
    
    valoracion_repo = ValoracionRepository(database)
    valoraciones = valoracion_repo.get_by_usuario_id(usuario.id)
    
    # Convertir valoraciones a formato compatible con el template
    netflix_items = []
    for val in valoraciones:
        item = type('obj', (object,), {
            'ID': val.id,
            'Tipo': val.pelicula_tipo if hasattr(val, 'pelicula_tipo') else 'N/A',
            'Nombre': val.pelicula_nombre if val.pelicula_nombre else f'Película #{val.pelicula_id}',
            'Genero': val.pelicula_genero if hasattr(val, 'pelicula_genero') else 'N/A',
            'Calificacion': val.puntuacion,
            'Nota': val.comentario if val.comentario else ''
        })()
        netflix_items.append(item)
    
    return templates.TemplateResponse("edit_netflix.html", {
        "request": request,
        "netflix": netflix_items
    })


# RUTA EDITADO - Usuario actualiza solo su valoración
@router.post("/do_edit_netflix")
async def do_edit_valoracion_usuario(request: Request,
                                      id: Annotated[str, Form()],
                                      nota: Annotated[str, Form()] = None,
                                      tipo: Annotated[str, Form()] = None,
                                      nombre: Annotated[str, Form()] = None,
                                      genero: Annotated[str, Form()] = None,
                                      calificacion: Annotated[float, Form()] = None):
    """Actualiza solo la valoración del usuario - NO la película"""
    usuario = obtener_usuario_actual(request)
    valoracion_repo = ValoracionRepository(database)
    valoracion_id = int(id)
    
    # Crear objeto valoración con nuevos datos (puntuacion y comentario)
    puntuacion_int = int(calificacion) if calificacion is not None else 0
    valoracion = Valoracion(valoracion_id, usuario.id, 0, puntuacion_int, nota)
    
    # Actualizar verificando propiedad
    resultado = valoracion_repo.actualizar_valoracion(valoracion, usuario.id)
    
    if not resultado:
        print(f"❌ Usuario {usuario.id} intentó editar valoración {valoracion_id} que no le pertenece")
        return RedirectResponse(url="/perfil", status_code=303)
    
    print(f"✅ Valoración {valoracion_id} actualizada por usuario {usuario.id}")
    return templates.TemplateResponse("do_edit_netflix.html", {"request": request})


# RUTA BORRAR - Usuario puede borrar solo sus valoraciones
@router.get("/borrar_netflix")
async def borrar_valoracion_usuario(request: Request):
    """Muestra las valoraciones del usuario para borrar - NO borra películas"""
    usuario = obtener_usuario_actual(request)
    
    valoracion_repo = ValoracionRepository(database)
    valoraciones = valoracion_repo.get_by_usuario_id(usuario.id)
    
    # Convertir valoraciones a formato compatible con el template
    netflix_items = []
    for val in valoraciones:
        item = type('obj', (object,), {
            'ID': val.id,
            'Tipo': val.pelicula_tipo if hasattr(val, 'pelicula_tipo') else 'N/A',
            'Nombre': val.pelicula_nombre if val.pelicula_nombre else f'Película #{val.pelicula_id}'
        })()
        netflix_items.append(item)
    
    return templates.TemplateResponse("borrar_netflix.html", {
        "request": request,
        "netflix": netflix_items
    })


# RUTA BORRADO - Usuario borra solo su valoración
@router.post("/do_borrar_netflix")
async def do_borrar_valoracion_usuario(request: Request,
                                        id: Annotated[str, Form()]):
    """Elimina solo la valoración del usuario - La película permanece en BD"""
    usuario = obtener_usuario_actual(request)
    valoracion_repo = ValoracionRepository(database)
    valoracion_id = int(id)
    
    # Borrar verificando propiedad
    resultado = valoracion_repo.borrar_valoracion(valoracion_id, usuario.id)
    
    if not resultado:
        print(f"❌ Usuario {usuario.id} intentó borrar valoración {valoracion_id} que no le pertenece")
        return RedirectResponse(url="/perfil", status_code=303)
    
    print(f"✅ Valoración {valoracion_id} eliminada por usuario {usuario.id} - La película permanece en BD")
    return templates.TemplateResponse("do_borrar_netflix.html", {"request": request})
