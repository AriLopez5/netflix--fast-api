import mysql.connector 



database = mysql.connector.connect( # LLAMAMOS AL FUNCION CONNECT PARA CONECTARNOS
     host ='informatica.iesquevedo.es',  # IP directa del servidor
     port = 3333,
     ssl_disabled = False,
     user ='root', #USUARIO QUE USAMOS NOSOTROS
     password ='1asir', #CONTRASEÑA CON LA QUE NOS CONECTAMOS
     database='ariadna'
)  

#database = mysql.connector.connect( # LLAMAMOS AL FUNCION CONNECT PARA CONECTARNOS
#    host ='83.32.204.61',  # IP directa del servidor
#    port = 3333,
#    ssl_disabled = True,
#    user ='root', #USUARIO QUE USAMOS NOSOTROS
#    password ='1asir', #CONTRASEÑA CON LA QUE NOS CONECTAMOS
#    database='ariadna'
#) 