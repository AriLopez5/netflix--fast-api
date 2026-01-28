from domain.model.Valoracion import Valoracion


class ValoracionRepository:

    def get_by_usuario_id(self, db, usuario_id: int) -> list[Valoracion]:
        """Obtiene todas las valoraciones de un usuario"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, nombre_pelicula, genero, 
                   nota, comentario, fecha_valoracion
            FROM Valoraciones
            WHERE usuario_id = %s
            ORDER BY fecha_valoracion DESC
        """, (usuario_id,))
        valoraciones_db = cursor.fetchall()
        cursor.close()
        
        valoraciones = []
        for val in valoraciones_db:
            valoracion = Valoracion(
                val[0],  # id
                val[1],  # usuario_id
                val[2],  # pelicula_id
                float(val[5]) if val[5] else 0.0,  # nota
                val[6],  # comentario
                str(val[7]) if val[7] else None  # fecha_valoracion
            )
            # Agregar datos de la película guardados en la tabla
            valoracion.pelicula_nombre = val[3]
            valoracion.genero = val[4]
            valoraciones.append(valoracion)
        
        return valoraciones

    def get_by_id(self, db, valoracion_id: int) -> Valoracion:
        """Obtiene una valoración por su ID"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha
            FROM Valoraciones 
            WHERE id = %s
        """, (valoracion_id,))
        val = cursor.fetchone()
        cursor.close()
        
        if val:
            return Valoracion(val[0], val[1], val[2], val[3], val[4], val[5])
        return None

    def get_all(self, db) -> list[Valoracion]:
        """Obtiene todas las valoraciones"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha
            FROM Valoraciones
            ORDER BY fecha DESC
        """)
        valoraciones_db = cursor.fetchall()
        cursor.close()
        
        valoraciones = []
        for val in valoraciones_db:
            valoraciones.append(Valoracion(val[0], val[1], val[2], val[3], val[4], val[5]))
        
        return valoraciones

    def insertar_valoracion(self, db, valoracion: Valoracion) -> None:
        """Inserta una nueva valoración"""
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Valoraciones (usuario_id, pelicula_id, nombre_pelicula, genero, nota, comentario, fecha_valoracion)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                nombre_pelicula = VALUES(nombre_pelicula),
                genero = VALUES(genero),
                nota = VALUES(nota),
                comentario = VALUES(comentario),
                fecha_valoracion = NOW()
        """, (
            valoracion.usuario_id,
            valoracion.pelicula_id,
            valoracion.pelicula_nombre,
            valoracion.genero,
            valoracion.puntuacion,
            valoracion.comentario
        ))
        
        db.commit()
        cursor.close()

    def actualizar_valoracion(self, db, valoracion: Valoracion) -> None:
        """Actualiza una valoración existente"""
        cursor = db.cursor()
        cursor.execute("""
            UPDATE Valoraciones 
            SET puntuacion = %s, comentario = %s
            WHERE id = %s
        """, (valoracion.puntuacion, valoracion.comentario, valoracion.id))
        
        db.commit()
        cursor.close()

    def borrar_valoracion(self, db, valoracion_id: int) -> None:
        """Elimina una valoración"""
        cursor = db.cursor()
        cursor.execute("DELETE FROM Valoraciones WHERE id = %s", (valoracion_id,))
        db.commit()
        cursor.close()

    def get_by_usuario_y_pelicula(self, db, usuario_id: int, pelicula_id: int) -> Valoracion:
        """Obtiene la valoración de un usuario para una película específica"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha
            FROM Valoraciones 
            WHERE usuario_id = %s AND pelicula_id = %s
        """, (usuario_id, pelicula_id))
        val = cursor.fetchone()
        cursor.close()
        
        if val:
            return Valoracion(val[0], val[1], val[2], val[3], val[4], val[5])
        return None

    def get_estadisticas_usuario(self, db, usuario_id: int) -> dict:
        """Obtiene estadísticas de valoraciones de un usuario"""
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   AVG(nota) as promedio,
                   MAX(nota) as maxima,
                   MIN(nota) as minima
            FROM Valoraciones 
            WHERE usuario_id = %s AND nota IS NOT NULL
        """, (usuario_id,))
        stats = cursor.fetchone()
        cursor.close()
        
        return {
            'total': stats[0] if stats else 0,
            'promedio': round(stats[1], 1) if stats and stats[1] else 0,
            'maxima': stats[2] if stats else 0,
            'minima': stats[3] if stats else 0
        }
