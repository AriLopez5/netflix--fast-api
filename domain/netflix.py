class Netflix:
    def __init__(self, id: int, tipo: str, nombre: str, genero: str = None, calificacion: float = None, visto: bool = False, nota: str = None):
        self.id = id
        self.tipo = tipo
        self.nombre = nombre
        self.genero = genero
        self.visto = visto
        self.calificacion = calificacion
        self.nota = nota