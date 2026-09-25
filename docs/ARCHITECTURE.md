# MEMORA — Arquitectura inicial

## Modelo

MEMORA representa una memoria como un grafo dirigido.

- **chat:** contenedor temporal/contextual.
- **message:** unidad de evidencia original.
- **concept:** término reutilizable entre mensajes.
- **edge:** relación explícita.

```text
chat
 ├── message ──mentions──> concept
 ├── message ──mentions──> concept
 └── message ──belongs_to──> chat
```

## Persistencia

SQLite mantiene datos, índices y relaciones en un único archivo. No se necesita un servidor.

## Recuperación

FTS5 proporciona una línea base determinista y auditable. Después podremos comparar embeddings contra ella.

## Compresión

Los cuerpos de mensajes se comprimen con zlib antes de persistirse.

## Reconstrucción

Una consulta produce **matches** (evidencia directa) y **reconstruction** (evidencia directa más vecinos del grafo). La capa superior podrá convertir ese paquete en lenguaje natural.

## Regla arquitectónica

El núcleo nunca depende de que un LLM recuerde correctamente. El LLM consulta MEMORA y recibe evidencia estructurada.
