from domain.netflix import Netflix

# Repositorio para interactuar con la base de datos
class AriadnaRepository:
    def __init__(self, db):
        self.db = db
    
    def insertar_netflix(self, netflix: Netflix):
        """Añadir una nueva película/serie a la base de datos"""
        cursor = self.db.cursor()
        sql = "INSERT INTO Netflix (tipo, nombre, genero, calificacion, visto, nota) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (netflix.tipo, netflix.nombre, netflix.genero, netflix.calificacion, netflix.visto, netflix.nota)
        cursor.execute(sql, valores)
        self.db.commit()
        cursor.close()

    def get_all(self):
        """Obtener todas las películas/series"""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Netflix")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def borrar_netflix(self, id: int):
        """Borrar una película/serie por ID"""
        cursor = self.db.cursor()
        sql = "DELETE FROM Netflix WHERE id = %s"
        cursor.execute(sql, (id,))
        self.db.commit()
        cursor.close()
    
    def get_by_id(self, id: int):
        """Obtener una película/serie por ID"""
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM Netflix WHERE id = %s"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def actualizar_netflix(self, netflix: Netflix):
        """Actualizar una película/serie existente"""
        cursor = self.db.cursor()
        sql = "UPDATE Netflix SET tipo=%s, nombre=%s, genero=%s, calificacion=%s, visto=%s, nota=%s WHERE id=%s"
        valores = (netflix.tipo, netflix.nombre, netflix.genero, netflix.calificacion, netflix.visto, netflix.nota, netflix.id)
        cursor.execute(sql, valores)
        self.db.commit()
        cursor.close()
