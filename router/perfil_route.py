from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from data.database import database
from data.valoracion_repository import ValoracionRepository
from domain.model.Valoracion import Valoracion
from utils.dependencies import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/perfil", response_class=HTMLResponse)
async def perfil_usuario(request: Request, usuario = Depends(require_auth)):
    """Muestra el perfil del usuario con sus valoraciones"""
    
    valoracion_repo = ValoracionRepository(database)
    
    try:
        # Obtener las valoraciones del usuario
        valoraciones = valoracion_repo.get_by_usuario_id(usuario.id)
        print(f"Usuario ID: {usuario.id}, Valoraciones encontradas: {len(valoraciones)}")
        
        # Obtener estadísticas
        estadisticas = valoracion_repo.get_estadisticas_usuario(usuario.id)
        print(f"Estadísticas: {estadisticas}")
    except Exception as e:
        # Si hay error (tabla no existe, etc), devolver valores vacíos
        import traceback
        print(f"Error al obtener valoraciones: {e}")
        print(traceback.format_exc())
        valoraciones = []
        estadisticas = {
            'total': 0
        }
    
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "usuario": usuario,
        "valoraciones": valoraciones,
        "estadisticas": estadisticas
    })


@router.post("/perfil/borrar_valoracion/{valoracion_id}")
async def borrar_valoracion(
    request: Request,
    valoracion_id: int,
    usuario = Depends(require_auth)
):
    """Permite al usuario borrar SOLO su propia valoración (la película permanece en la BD)"""
    
    valoracion_repo = ValoracionRepository(database)
    
    try:
        # Intentar borrar verificando que pertenezca al usuario
        resultado = valoracion_repo.borrar_valoracion(valoracion_id, usuario.id)
        
        if not resultado:
            # El usuario no tiene permisos para borrar esta valoración
            print(f"❌ Usuario {usuario.id} intentó borrar valoración {valoracion_id} que no le pertenece")
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para borrar esta valoración"
            )
        
        print(f"✅ Valoración {valoracion_id} eliminada por usuario {usuario.id} - La película permanece en la BD")
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Error al borrar valoración: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error al borrar la valoración")
    
    return RedirectResponse(url="/perfil", status_code=303)
