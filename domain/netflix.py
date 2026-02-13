class Netflix:
    def __init__(self, id: int, tipo: str, nombre: str, genero: str = None, calificacion: int = None):
        self.id = id
        self.tipo = tipo
        self.nombre = nombre
        self.genero = genero
        self.calificacion = calificacion