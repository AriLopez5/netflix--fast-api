class Valoracion:
    def __init__(self, id: int, usuario_id: int, pelicula_id: int, puntuacion: int, comentario: str = None, fecha: str = None):
        self.id = id
        self.usuario_id = usuario_id
        self.pelicula_id = pelicula_id
        self.puntuacion = puntuacion
        self.comentario = comentario
        self.fecha = fecha
        # Campo adicional para el nombre de la película (obtenido por JOIN)
        self.pelicula_nombre = None

