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
@router.post("/do_insertar_netflix")
async def do_insertar_netflix(request: Request,
    tipo: Annotated[str, Form()],
    nombre: Annotated[str, Form()],
    genero: Annotated[str, Form()] = None,
    calificacion: Annotated[float, Form()] = None,
    visto: Annotated[str, Form()] = "",
    nota: Annotated[str, Form()] = None,
):
    """Inserta película/serie y crea valoración del usuario - Cualquier usuario autenticado"""
    # Obtener el usuario actual
    usuario = obtener_usuario_actual(request)
    
    # Convertir "si"/"no" a booleano
    visto_bool = True if visto.lower() == "si" else False
    
    # Insertar la película/serie
    netflix_repo = AriadnaRepository(database)
    netflix = Netflix(0, tipo, nombre, genero, calificacion, visto_bool, nota)
    netflix_repo.insertar_netflix(netflix)
    
    # Obtener el ID de la película recién insertada
    cursor = database.cursor()
    cursor.execute("SELECT id FROM Netflix WHERE Nombre = %s ORDER BY id DESC LIMIT 1", (nombre,))
    resultado = cursor.fetchone()
    cursor.close()
    
    # Si el usuario está autenticado y proporcionó una calificación, crear valoración
    if usuario and resultado and calificacion is not None:
        pelicula_id = resultado[0]
        print(f"Creando valoración: usuario_id={usuario.id}, pelicula_id={pelicula_id}, calificacion={calificacion}")
        try:
            valoracion_repo = ValoracionRepository()
            # Crear valoración con todos los datos
            valoracion = Valoracion(0, usuario.id, pelicula_id, calificacion, nota)
            # Asignar nombre y género de la película
            valoracion.pelicula_nombre = nombre
            valoracion.genero = genero
            valoracion_repo.insertar_valoracion(database, valoracion)
            print(f"✓ Valoración guardada correctamente")
        except Exception as e:
            import traceback
            print(f"✗ Error al insertar valoración: {e}")
            print(traceback.format_exc())
            # Continuar aunque falle la valoración (puede que la tabla no exista aún)
    else:
        print(f"No se creó valoración: usuario={usuario is not None}, resultado={resultado is not None}, calificacion={calificacion}")
    
    return templates.TemplateResponse("do_insert_netflix.html", {"request": request})
