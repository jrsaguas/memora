# MEMORA — Plan de producto

Fecha de inicio: 2026-09-24

## Objetivo

Construir una memoria local, compacta y reconstruible capaz de conectar conversaciones, mensajes, conceptos y relaciones para recuperar contexto a través del tiempo.

## Principios

1. **Reducibilidad:** conservar lo mínimo que permita recuperar lo máximo útil.
2. **Reconstrucción:** recuperar contexto desde piezas relacionadas, no desde una copia gigante.
3. **Local-first:** funcionar sin servicios externos.
4. **LLM-optional:** la inteligencia generativa es una capa posterior.
5. **Trazabilidad:** toda reconstrucción debe poder regresar a nodos fuente.
6. **Incrementalidad:** cada versión debe producir un producto ejecutable.
7. **No sobreingeniería:** medir antes de introducir embeddings o infraestructura pesada.

## Fases

### A — Núcleo persistente
SQLite, nodos, aristas, compresión, hashing y tests.

### B — Recuperación
FTS5, ranking, expansión por vecindad y reconstrucción trazable.

### C — Consolidación
Duplicados, conceptos, relaciones temporales y resúmenes compactos.

### D — Memoria semántica opcional
Embeddings intercambiables y recuperación híbrida.

### E — Autoconocimiento
Métricas de densidad, cobertura, aislamiento y redundancia.

### F — Interfaz
Explorador, grafo, búsqueda, línea temporal y reconstrucción.

### G — Agentes
Ingesta de conversaciones, consulta contextual y consolidación controlada.

## Criterio de avance

No se avanza por cantidad de código. Se avanza cuando existe una prueba reproducible de que una capacidad nueva mejora recuperación, compactación, trazabilidad o estabilidad.
