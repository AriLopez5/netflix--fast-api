from domain.model.Usuario import Usuario
import bcrypt


class UsuarioRepository:

    def get_by_username(self, db, username: str) -> Usuario:
        """Obtiene un usuario por su nombre de usuario"""
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = %s", (username,))
        usuario_db = cursor.fetchone()
        cursor.close()
        
        if usuario_db:
            # Verificar cuántas columnas tenemos
            if len(usuario_db) >= 4:
                return Usuario(usuario_db[0], usuario_db[1], usuario_db[2], usuario_db[3])
            elif len(usuario_db) == 3:
                # Si solo hay 3 columnas (id, username, password_hash), email será None
                return Usuario(usuario_db[0], usuario_db[1], usuario_db[2], None)
            else:
                print(f"[ERROR] Estructura de tabla incorrecta")
                return None
        return None

    def get_by_id(self, db, user_id: int) -> Usuario:
        """Obtiene un usuario por su ID"""
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE id = %s", (user_id,))
        usuario_db = cursor.fetchone()
        cursor.close()
        
        if usuario_db:
            # Verificar cuántas columnas tenemos
            if len(usuario_db) >= 4:
                return Usuario(usuario_db[0], usuario_db[1], usuario_db[2], usuario_db[3])
            elif len(usuario_db) == 3:
                # Si solo hay 3 columnas (id, username, password_hash), email será None
                return Usuario(usuario_db[0], usuario_db[1], usuario_db[2], None)
            else:
                print(f"[ERROR get_by_id] Estructura de tabla incorrecta")
                return None
        return None

    def get_all(self, db) -> list[Usuario]:
        """Obtiene todos los usuarios"""
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Usuarios")
        usuarios_en_db = cursor.fetchall()
        usuarios: list[Usuario] = list()
        
        for usuario in usuarios_en_db:
            # Verificar cuántas columnas tenemos
            if len(usuario) >= 4:
                usuario_obj = Usuario(usuario[0], usuario[1], usuario[2], usuario[3])
            elif len(usuario) == 3:
                usuario_obj = Usuario(usuario[0], usuario[1], usuario[2], None)
            else:
                continue
            usuarios.append(usuario_obj)
        cursor.close()
        
        return usuarios

    def insertar_usuario(self, db, username: str, password: str, email: str = None) -> None:
        """Inserta un nuevo usuario con contraseña hasheada"""
        cursor = db.cursor()
        
        # Hashear la contraseña con bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insertar solo username y password_hash (la tabla no tiene columna email)
        cursor.execute(
            "INSERT INTO Usuarios (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        
        db.commit()
        cursor.close()

    def verificar_password(self, password: str, password_hash: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        try:
            # Si password_hash es bytes, usarlo directamente, si es str, codificarlo
            if isinstance(password_hash, str):
                # Verificar si el string empieza con b' (indica bytes como string)
                if password_hash.startswith("b'") and password_hash.endswith("'"):
                    # Eliminar b' y ' del principio y final
                    password_hash = password_hash[2:-1]
                    password_hash = password_hash.encode('utf-8')
                else:
                    password_hash = password_hash.encode('latin-1')
            
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        except Exception as e:
            return False

    def actualizar_password(self, db, user_id: int, nueva_password: str) -> None:
        """Actualiza la contraseña de un usuario"""
        cursor = db.cursor()
        
        # Hashear la nueva contraseña
        password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute(
            "UPDATE Usuarios SET password_hash = %s WHERE id = %s",
            (password_hash, user_id)
        )
        
        db.commit()
        cursor.close()