# MEMORA — escalabilidad estructural

Fecha de esta revisión: 2026-09-25.

## Qué mide actualmente la batería

La batería de `experiments.benchmark` es un experimento de **estructura del grafo y compactación**, no una prueba completa de complejidad temporal.

Para cada tamaño de entrada registra:

- mensajes y chats;
- bytes de texto fuente y bytes de SQLite;
- nodos por tipo;
- aristas totales y aristas por mensaje;
- términos únicos;
- proxy contrafactual de conceptos ingenuos;
- conceptos por cada 100 mensajes;
- reducción frente al proxy ingenuo;
- aristas `mentions` y su densidad;
- duplicación de mensajes;
- recuperación léxica y reconstrucción;
- número de chats alcanzados durante la recuperación.

## Qué podemos afirmar

El diseño actual no materializa un nodo de concepto para cada término único. Un término sólo se promociona cuando alcanza `concept_min_frequency`, cuyo valor mínimo efectivo es 2.

Por tanto, para la batería sintética, el número de conceptos está gobernado por los términos reutilizados y no por el número total de fragmentos únicos.

La métrica `naive_concept_nodes_proxy` es deliberadamente contrafactual: representa cuántos nodos de concepto habría si cada término indexado se materializara como concepto.

La métrica `concept_reduction_vs_naive_proxy` permite cuantificar esa diferencia sin llamarla una prueba de complejidad asintótica.

## Qué NO demuestra

Esta batería, por sí sola, no demuestra:

1. que el tiempo de ingestión sea O(1), O(log n) u O(n);
2. que el coste de recuperación sea sublineal;
3. que el tamaño de SQLite sea sublineal respecto al contenido;
4. que los resultados se mantengan con distribuciones de lenguaje reales;
5. que el comportamiento observado para 5,000 mensajes pueda extrapolarse automáticamente a millones.

En particular, la implementación recorre los términos de cada mensaje y realiza consultas de frecuencia durante la promoción. El coste temporal debe medirse por separado.

## Próximo experimento controlado

La siguiente fase debe separar tres preguntas:

### A. Crecimiento estructural

Comparar varios tamaños y observar:

- mensajes;
- nodos de mensaje;
- conceptos;
- aristas;
- bytes almacenados.

### B. Coste temporal

Medir por separado:

- ingestión;
- búsqueda;
- reconstrucción.

La medición debe usar varias repeticiones y reportar mediana y dispersión, no una sola ejecución.

### C. Sensibilidad a la distribución

Repetir la batería con al menos:

- vocabulario altamente reutilizado;
- vocabulario intermedio;
- vocabulario casi único.

Esto evita confundir una propiedad del algoritmo con una propiedad accidental del corpus sintético.

## Criterio de cierre de esta fase

No se debe declarar "escalabilidad sublineal" hasta disponer de evidencia temporal y estructural que sustente específicamente esa afirmación.

El objetivo inmediato es producir una **caracterización reproducible del comportamiento**, no una etiqueta de rendimiento.
