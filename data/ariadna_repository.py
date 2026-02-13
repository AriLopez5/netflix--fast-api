from domain.netflix import Netflix

# Repositorio para interactuar con la base de datos
class AriadnaRepository:
    def __init__(self, db):
        self.db = db
    
    def insertar_netflix(self, netflix: Netflix):
        """Añadir una nueva película/serie a la base de datos y retornar el ID insertado"""
        cursor = self.db.cursor()
        sql = "INSERT INTO Netflix (tipo, nombre, genero, calificacion_media) VALUES (%s, %s, %s, %s)"
        valores = (netflix.tipo, netflix.nombre, netflix.genero, netflix.calificacion)
        cursor.execute(sql, valores)
        self.db.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        return inserted_id

    def get_all(self):
        """Obtener todas las películas/series"""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                MIN(n.id) as id,
                n.tipo, 
                n.nombre, 
                MAX(n.genero) as genero,
                COALESCE(ROUND(AVG(v.puntuacion)), MAX(n.calificacion_media)) as calificacion_media
            FROM Netflix n
            LEFT JOIN Valoraciones v ON n.id = v.pelicula_id
            GROUP BY n.nombre, n.tipo
            ORDER BY n.nombre
        """)
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
        sql = "UPDATE Netflix SET tipo=%s, nombre=%s, genero=%s, calificacion_media=%s WHERE id=%s"
        valores = (netflix.tipo, netflix.nombre, netflix.genero, netflix.calificacion, netflix.id)
        cursor.execute(sql, valores)
        self.db.commit()
        cursor.close()

    def buscar_por_nombre(self, nombre: str):
        """Busca una película/serie por nombre exacto"""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT id, tipo, nombre, genero, calificacion_media FROM Netflix WHERE nombre = %s", (nombre,))
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return Netflix(row['id'], row['tipo'], row['nombre'], row['genero'], row['calificacion_media'])
        return None