from fastapi import Request
from data.usuario_repository import UsuarioRepository
from data.database import database


def crear_sesion(request: Request, user_id: int, username: str):
    """Crea una sesión para el usuario"""
    request.session["user_id"] = user_id
    request.session["username"] = username


def destruir_sesion(request: Request):
    """Destruye la sesión del usuario"""
    request.session.clear()


def obtener_usuario_actual(request: Request):
    """Obtiene el usuario actual de la sesión"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    usuario_repo = UsuarioRepository()
    return usuario_repo.get_by_id(database, user_id)
