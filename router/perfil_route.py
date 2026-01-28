from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from data.database import database
from data.valoracion_repository import ValoracionRepository
from utils.dependencies import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/perfil", response_class=HTMLResponse)
async def perfil_usuario(request: Request, usuario = Depends(require_auth)):
    """Muestra el perfil del usuario con sus valoraciones"""
    
    valoracion_repo = ValoracionRepository()
    
    try:
        # Obtener las valoraciones del usuario
        valoraciones = valoracion_repo.get_by_usuario_id(database, usuario.id)
        print(f"Usuario ID: {usuario.id}, Valoraciones encontradas: {len(valoraciones)}")
        
        # Obtener estadísticas
        estadisticas = valoracion_repo.get_estadisticas_usuario(database, usuario.id)
        print(f"Estadísticas: {estadisticas}")
    except Exception as e:
        # Si hay error (tabla no existe, etc), devolver valores vacíos
        import traceback
        print(f"Error al obtener valoraciones: {e}")
        print(traceback.format_exc())
        valoraciones = []
        estadisticas = {
            'total': 0,
            'promedio': 0,
            'maxima': 0,
            'minima': 0
        }
    
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "usuario": usuario,
        "valoraciones": valoraciones,
        "estadisticas": estadisticas
    })
