import mysql.connector

db = mysql.connector.connect(
    host='informatica.iesquevedo.es',
    port=3333,
    ssl_disabled=False,
    user='root',
    password='1asir',
    database='ariadna'
)

cursor = db.cursor()

# Eliminar tabla si existe
print("Eliminando tabla Valoraciones...")
cursor.execute("DROP TABLE IF EXISTS Valoraciones")

# Crear tabla
print("Creando tabla Valoraciones...")
cursor.execute("""
    CREATE TABLE Valoraciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        pelicula_id INT NOT NULL,
        nombre_pelicula VARCHAR(255) NOT NULL,
        genero VARCHAR(100),
        nota DECIMAL(3,1),
        comentario TEXT,
        fecha_valoracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (pelicula_id) REFERENCES Netflix(id) ON DELETE CASCADE,
        UNIQUE KEY unique_usuario_pelicula (usuario_id, pelicula_id),
        INDEX idx_usuario (usuario_id),
        INDEX idx_pelicula (pelicula_id),
        INDEX idx_fecha (fecha_valoracion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

db.commit()
print("Tabla creada exitosamente!")

# Mostrar estructura
cursor.execute("DESCRIBE Valoraciones")
columns = cursor.fetchall()
print("\nEstructura:")
for col in columns:
    print(f"  {col[0]}: {col[1]}")

cursor.close()
db.close()
