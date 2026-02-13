from domain.model.Valoracion import Valoracion


class ValoracionRepository:
    def __init__(self, db):
        self.db = db

    def get_by_usuario_id(self, usuario_id: int) -> list[Valoracion]:
        """Obtiene todas las valoraciones de un usuario con el nombre de la película"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT v.id, v.usuario_id, v.pelicula_id, v.puntuacion,
                   v.comentario, v.fecha_valoracion, n.nombre, n.tipo, n.genero
            FROM Valoraciones v
            LEFT JOIN Netflix n ON v.pelicula_id = n.id
            WHERE v.usuario_id = %s
            ORDER BY v.fecha_valoracion DESC
        """, (usuario_id,))
        valoraciones_db = cursor.fetchall()
        cursor.close()
        
        valoraciones = []
        for val in valoraciones_db:
            valoracion = Valoracion(
                val[0],  # id
                val[1],  # usuario_id
                val[2],  # pelicula_id
                val[3],  # puntuacion
                val[4],  # comentario
                str(val[5]) if val[5] else None  # fecha_valoracion
            )
            # Agregar información de la película obtenida del JOIN
            valoracion.pelicula_nombre = val[6]
            valoracion.pelicula_tipo = val[7] if val[7] else 'N/A'
            valoracion.pelicula_genero = val[8] if val[8] else 'N/A'
            valoraciones.append(valoracion)
        
        return valoraciones

    def get_by_id(self, valoracion_id: int) -> Valoracion:
        """Obtiene una valoración por su ID"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha_valoracion
            FROM Valoraciones 
            WHERE id = %s
        """, (valoracion_id,))
        val = cursor.fetchone()
        cursor.close()
        
        if val:
            return Valoracion(val[0], val[1], val[2], val[3], val[4], val[5])
        return None

    def get_all(self) -> list[Valoracion]:
        """Obtiene todas las valoraciones"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha_valoracion
            FROM Valoraciones
            ORDER BY fecha_valoracion DESC
        """)
        valoraciones_db = cursor.fetchall()
        cursor.close()
        
        valoraciones = []
        for val in valoraciones_db:
            valoraciones.append(Valoracion(val[0], val[1], val[2], val[3], val[4], val[5]))
        
        return valoraciones

    def insertar_valoracion(self, valoracion: Valoracion) -> None:
        """Inserta una nueva valoración"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO Valoraciones (usuario_id, pelicula_id, puntuacion, comentario, fecha_valoracion)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                puntuacion = VALUES(puntuacion),
                comentario = VALUES(comentario),
                fecha_valoracion = NOW()
        """, (
            valoracion.usuario_id,
            valoracion.pelicula_id,
            valoracion.puntuacion,
            valoracion.comentario
        ))
        
        self.db.commit()
        cursor.close()

    def actualizar_valoracion(self, valoracion: Valoracion, usuario_id: int = None) -> bool:
        """Actualiza una valoración existente. Si se proporciona usuario_id, verifica que sea el dueño.
        Retorna True si se actualizó correctamente, False si no tiene permisos."""
        cursor = self.db.cursor()
        
        # Si se proporciona usuario_id, verificar que sea el dueño de la valoración
        if usuario_id is not None:
            cursor.execute("SELECT usuario_id FROM Valoraciones WHERE id = %s", (valoracion.id,))
            resultado = cursor.fetchone()
            
            if not resultado or resultado[0] != usuario_id:
                cursor.close()
                return False  # No tiene permisos para actualizar esta valoración
        
        cursor.execute("""
            UPDATE Valoraciones 
            SET puntuacion = %s, comentario = %s, fecha_valoracion = NOW()
            WHERE id = %s
        """, (valoracion.puntuacion, valoracion.comentario, valoracion.id))
        
        self.db.commit()
        cursor.close()
        return True

    def borrar_valoracion(self, valoracion_id: int, usuario_id: int = None) -> bool:
        """Elimina una valoración. Si se proporciona usuario_id, verifica que sea el dueño.
        Solo borra el comentario y valoración del usuario, la película permanece en la base de datos.
        Retorna True si se eliminó correctamente, False si no tiene permisos."""
        cursor = self.db.cursor()
        
        # Si se proporciona usuario_id, verificar que sea el dueño de la valoración
        if usuario_id is not None:
            cursor.execute("SELECT usuario_id FROM Valoraciones WHERE id = %s", (valoracion_id,))
            resultado = cursor.fetchone()
            
            if not resultado or resultado[0] != usuario_id:
                cursor.close()
                return False  # No tiene permisos para borrar esta valoración
        
        # Elimina solo la valoración del usuario, la película sigue en su tabla correspondiente
        cursor.execute("DELETE FROM Valoraciones WHERE id = %s", (valoracion_id,))
        self.db.commit()
        cursor.close()
        return True

    def get_by_usuario_y_pelicula(self, usuario_id: int, pelicula_id: int) -> Valoracion:
        """Obtiene la valoración de un usuario para una película específica"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, usuario_id, pelicula_id, puntuacion, comentario, fecha_valoracion
            FROM Valoraciones 
            WHERE usuario_id = %s AND pelicula_id = %s
        """, (usuario_id, pelicula_id))
        val = cursor.fetchone()
        cursor.close()
        
        if val:
            return Valoracion(val[0], val[1], val[2], val[3], val[4], val[5])
        return None

    def get_estadisticas_usuario(self, usuario_id: int) -> dict:
        """Obtiene estadísticas de valoraciones de un usuario"""
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Valoraciones 
            WHERE usuario_id = %s
        """, (usuario_id,))
        stats = cursor.fetchone()
        cursor.close()
        
        return {
            'total': stats[0] if stats else 0
        }
