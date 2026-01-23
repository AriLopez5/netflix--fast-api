from fastapi import HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from utils.session import obtener_usuario_actual

# Inicializar templates
templates = Jinja2Templates(directory="templates")


def require_auth(request: Request):

    usuario = obtener_usuario_actual(request)
    if not usuario:
        raise HTTPException(
            status_code=303,
            detail="Debe iniciar sesión",
            headers={"Location": "/login"}
        )
    return usuario


def optional_auth(request: Request) -> Optional[dict]:

    return obtener_usuario_actual(request)

def require_role(required_role: str):

    def role_checker(request: Request, usuario: dict = Depends(require_auth)) -> dict:
        if usuario.get("role") != required_role:
            # ✅ Devolver TemplateResponse con plantilla 403.html
            return templates.TemplateResponse(
                "403.html",
                {
                    "request": request,
                    "message": f"No tienes permisos suficientes para acceder a esta página.",
                    "required_role": f"Se requiere rol: {required_role}",
                    "current_role": usuario.get("role", "sin rol"),
                    "icon": "🚫"
                },
                status_code=403
            )
        return usuario
    return role_checker


def require_admin(request: Request, usuario: dict = Depends(require_auth)) -> dict:

    if usuario.get("role") not in ["admin", "superadmin"]:
        # ✅ Devolver TemplateResponse con plantilla 403.html
        return templates.TemplateResponse(
            "403.html",
            {
                "request": request,
                "message": "Esta página requiere permisos de Administrador.",
                "required_role": "Roles permitidos: admin, superadmin",
                "current_role": usuario.get("role", "sin rol"),
                "icon": "🔒"
            },
            status_code=403
        )
    return usuario


def require_superadmin(request: Request, usuario: dict = Depends(require_auth)) -> dict:

    if usuario.get("role") != "superadmin":
        # ✅ Devolver TemplateResponse con plantilla 403.html
        return templates.TemplateResponse(
            "403.html",
            {
                "request": request,
                "message": "Esta página requiere permisos de Super Administrador.",
                "required_role": "Solo el super administrador tiene acceso",
                "current_role": usuario.get("role", "sin rol"),
                "icon": "👑"
            },
            status_code=403
        )
    return usuario


def require_any_role(*roles: str):

    def role_checker(request: Request, usuario: dict = Depends(require_auth)) -> dict:
        if usuario.get("role") not in roles:
            # ✅ Devolver TemplateResponse con plantilla 403.html
            roles_text = ", ".join(roles)
            return templates.TemplateResponse(
                "403.html",
                {
                    "request": request,
                    "message": "No tienes permisos suficientes para acceder a esta página.",
                    "required_role": f"Roles permitidos: {roles_text}",
                    "current_role": usuario.get("role", "sin rol"),
                    "icon": "⚠️"
                },
                status_code=403
            )
        return usuario
    return role_checker

# Alias para mayor claridad
get_current_user = require_auth
get_optional_user = optional_auth