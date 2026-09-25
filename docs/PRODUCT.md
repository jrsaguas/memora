# MEMORA — Definición del producto

## Problema
Las conversaciones quedan fragmentadas entre sesiones y la información útil puede existir en mensajes y chats distintos.

## Hipótesis
Si cada fragmento se representa como una unidad de memoria y las relaciones se conservan explícitamente, una consulta puede recuperar y reconstruir contexto sin almacenar una copia independiente de cada contexto posible.

## Producto
MEMORA será infraestructura de memoria personal/local para ingerir conversaciones, identificar unidades reutilizables, relacionarlas, recuperar memoria, reconstruir contexto, mantener trazabilidad y consolidar redundancia.

## No es
Un clon de Obsidian, una simple carpeta de notas, un chatbot ni una base vectorial obligatoria.

## Prueba de producto
Ante una pregunta como «¿Qué habíamos decidido sobre el proyecto de memoria hace meses?», el sistema debe encontrar piezas relacionadas y devolver un paquete de contexto trazable que una capa superior pueda convertir en una respuesta natural.

## Restricción
La hipótesis de crecimiento sublineal será medida experimentalmente; no se asumirá como propiedad hasta demostrarla.
