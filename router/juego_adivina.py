from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import random

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/juego_adivina", response_class=HTMLResponse)
async def iniciar_juego(request: Request):
    """Iniciar o mostrar el juego de adivinar número"""
    # Limpiar solo los datos del juego, NO toda la sesión
    request.session["numero_secreto"] = random.randint(1, 100)
    request.session["intentos_restantes"] = 10
    request.session["historial"] = []
    request.session["mensaje"] = "¡Nuevo juego! Adivina el número entre 1 y 100."
    
    return templates.TemplateResponse("juego_adivina.html", {
        "request": request,
        "intentos_restantes": 10,
        "historial": [],
        "mensaje": "¡Nuevo juego! Adivina el número entre 1 y 100.",
        "juego_activo": True
    })

@router.post("/juego_adivina", response_class=HTMLResponse)
async def adivinar_numero(request: Request, numero: Annotated[int, Form()]):
    """Procesar el intento de adivinar el número"""
    
    # Verificar si hay un juego activo
    if "numero_secreto" not in request.session:
        request.session["numero_secreto"] = random.randint(1, 100)
        request.session["intentos_restantes"] = 10
        request.session["historial"] = []
    
    numero_secreto = request.session["numero_secreto"]
    intentos_restantes = request.session["intentos_restantes"]
    historial = request.session.get("historial", [])
    
    # Validar que el juego sigue activo
    if intentos_restantes <= 0:
        mensaje = f"El juego ha terminado. El número era {numero_secreto}. Reinicia para jugar de nuevo."
    else:
        # Procesar el intento
        intentos_restantes -= 1
        request.session["intentos_restantes"] = intentos_restantes
        
        if numero < numero_secreto:
            mensaje = f"El número {numero} es muy bajo. Intenta con uno más alto."
            historial.append(f"Intento: {numero} - Muy bajo")
        elif numero > numero_secreto:
            mensaje = f"El número {numero} es muy alto. Intenta con uno más bajo."
            historial.append(f"Intento: {numero} - Muy alto")
        else:
            intentos_usados = 10 - intentos_restantes
            mensaje = f"¡Felicidades! 🎉 Has adivinado el número {numero_secreto} en {intentos_usados} intentos."
            historial.append(f"Intento: {numero} - ¡CORRECTO! 🎯")
            # Marcar el juego como terminado
            intentos_restantes = 0
            request.session["intentos_restantes"] = 0
        
        # Si se acabaron los intentos y no adivinó
        if intentos_restantes == 0 and numero != numero_secreto:
            mensaje = f"Has agotado todos los intentos. El número era {numero_secreto}. Mejor suerte la próxima vez."
        
        request.session["historial"] = historial
    
    request.session["mensaje"] = mensaje
    
    return templates.TemplateResponse("juego_adivina.html", {
        "request": request,
        "intentos_restantes": intentos_restantes,
        "historial": historial,
        "mensaje": mensaje,
        "juego_activo": intentos_restantes > 0 and numero != numero_secreto
    })

@router.get("/juego_adivina/reiniciar")
async def reiniciar_juego(request: Request):
    """Reiniciar el juego"""
    # Limpiar solo los datos del juego, NO toda la sesión
    request.session["numero_secreto"] = random.randint(1, 100)
    request.session["intentos_restantes"] = 10
    request.session["historial"] = []
    request.session["mensaje"] = "¡Nuevo juego iniciado! Adivina el número entre 1 y 100."
    
    return templates.TemplateResponse("juego_adivina.html", {
        "request": request,
        "intentos_restantes": 10,
        "historial": [],
        "mensaje": "¡Nuevo juego iniciado! Adivina el número entre 1 y 100.",
        "juego_activo": True
    })