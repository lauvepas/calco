# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-24

### Added
- Nueva arquitectura modular del proyecto con separación clara de responsabilidades:
  - Módulo `cleaning/` para procesamiento y limpieza de datos
  - Módulo `encoder/` para gestión de claves y codificación
  - Módulo `maths/` para cálculos y operaciones matemáticas
  
- Implementación completa del módulo de limpieza:
  - Clase `DataFrameCleaner` con arquitectura de componentes:
    - `columns_cleaner`: Gestión y transformación de columnas
    - `rows_cleaner`: Filtrado y limpieza de filas
    - `data_cleaner`: Transformación y normalización de datos
  - Sistema de herencia desde `BaseCleaner` para reutilización de código
  - Implementación de patrones de diseño para mejor mantenibilidad

- Sistema avanzado de parametrización:
  - Clase `Parameters` con configuración centralizada
  - Clase `DatasetParams` con implementación de dataclasses para:
    - Validación de tipos en tiempo de compilación
    - Inmutabilidad de parámetros (frozen=True)
    - Configuración específica por tipo de dataset

- Nuevas funcionalidades de procesamiento:
  - `OutliersManager` con capacidades de:
    - Detección de outliers mediante z-score
    - Procesamiento recursivo de valores atípicos
    - Sistema de reporting detallado
  - `Validator` con:
    - Validación configurable por columnas
    - Sistema de reglas personalizables
    - Gestión de errores granular
  - `Encoder` para:
    - Generación de claves únicas
    - Codificación de valores categóricos
    - Gestión de relaciones entre datasets

### Changed
- Refactorización arquitectónica completa:
  - Migración a estructura modular
  - Implementación de principios SOLID
  - Mejora en la cohesión y acoplamiento del código

- Optimizaciones en el sistema de limpieza:
  - Nuevo pipeline de procesamiento más eficiente
  - Implementación de procesamiento por lotes
  - Mejora en el manejo de memoria para grandes datasets

- Sistema de gestión de outliers actualizado:
  - Nuevo algoritmo recursivo para cálculo de costes
  - Implementación de método iterativo para procesamiento
  - Sistema de logging detallado de operaciones

### Removed
- Eliminación de código legacy:
  - Clase `CostesCleaner` reemplazada por nueva arquitectura
  - Eliminación de funciones duplicadas
  - Limpieza de imports no utilizados

### Fixed
- Correcciones críticas:
  - Solución al problema de recursión en cálculo de costes
  - Corrección en el manejo de NaN en procesamiento
  - Mejora en la detección de duplicados

## [0.0.1] - 2025-04-16
### Added
- Configuración inicial del proyecto:
  - Estructura base de directorios
  - Configuración del entorno virtual
  - Archivos de configuración básicos

[0.1.0]: https://github.com/usuario/CalculadoraMargen/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/usuario/CalculadoraMargen/releases/tag/v0.0.1
