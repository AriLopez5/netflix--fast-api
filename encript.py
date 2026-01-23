import bcrypt

palabra = input("Escribe una palabra: ")
salt = bcrypt.gensalt()
encriptada = bcrypt.hashpw(palabra.encode(), salt)
print(f"Palabra encriptada: {encriptada.decode()}")