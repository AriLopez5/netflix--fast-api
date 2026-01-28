-- Asignar valoraciones existentes de la tabla Netflix a usuarios alumno (id=2) y ari (id=3)
-- Distribución alternada entre los usuarios

-- Valoraciones para usuario 'alumno' (id=2)
INSERT INTO Valoraciones (usuario_id, pelicula_id, nombre_pelicula, genero, nota, comentario)
VALUES 
(2, 1, 'Al filo del mañana', 'Saltos temporales', 10, 'Entretenida'),
(2, 5, 'Animal', 'Animalicos', 9, 'Me ha gustado'),
(2, 7, 'La princesa Mononoke', 'Animación', 10, 'Maravilla de pelicula'),
(2, 11, 'Juego de Tronos', 'Drama', 6, 'Mucha nota pongo para el final que tiene');

-- Valoraciones para usuario 'ari' (id=3)
INSERT INTO Valoraciones (usuario_id, pelicula_id, nombre_pelicula, genero, nota, comentario)
VALUES 
(3, 2, 'The Gentlemen', 'Drama', 10, 'Entretenida'),
(3, 6, 'Star Wars 8', 'Ficción', 1, 'Mierdon'),
(3, 9, 'Harry Potter y el prisionero de Azcaban', 'Fantasía Mágica', 9, 'Muy entretenida'),
(3, 12, 'Lost', 'Drama', 10, 'diez de diez');

-- Verificar las valoraciones insertadas
SELECT v.id, u.username, v.nombre_pelicula, v.nota, v.comentario 
FROM Valoraciones v
JOIN Usuarios u ON v.usuario_id = u.id
ORDER BY v.usuario_id, v.id;
