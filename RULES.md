# 📜 RULES.md - BJJ-BetSports Project Rules

Este documento es la **fuente única de verdad** para los estándares técnicos, arquitectónicos y de calidad de este proyecto. Todos los agentes (Orchestrator, Frontend, Backend, Architecture) deben cumplir estas reglas al pie de la letra.

## 🌍 Reglas Globales

- **Idioma**: Todas las respuestas y comentarios en el código deben ser en **español**.
- **Flujo de Trabajo**: Se prohíbe la implementación directa sin una especificación previa generada por el Orchestrator siguiendo el flujo **Spec Kit**.
- **Clean Architecture**: El proyecto sigue una arquitectura limpia (Hexagonal/Domain-Driven Design).
- **Seguridad**: Nunca incluir secretos o claves API hardcodeadas. Usar variables de entorno (`.env`).
- **Calidad**: No se permite el uso de `any` en TypeScript ni funciones sin tipado en Python.

---

## 🎨 Frontend (React 19 + Vite + MUI)

### Componentes y UI
- Usar **Material UI (MUI)** como librería base de componentes.
- Seguir las guías de diseño de la marca (estética premium, dark mode por defecto).
- Implementar estados de carga (`loading`) y error (`error boundary`) en todas las vistas interactivas.

### Estado y Tipado
- Mantener tipado estricto en todos los componentes y hooks.
- Preferir componentes funcionales con hooks sobre clases.
- Centralizar tipos compartidos en `frontend/src/types/`.

### Calidad y Verificación
- Ejecutar `npm run lint` antes de dar por completada una tarea.
- Asegurar que el bundle genere un build válido (`npm run build`).

---

## ⚙️ Backend (FastAPI + Python + ML)

### Estructura y Dominio
- Mantener la separación de capas: `domain`, `application`, `infrastructure` y `presentation`.
- La lógica de negocio pesada (indicadores, ML) reside en la capa de `domain`.

### Gestión de Datos y ML
- **Zero Stats Rule**: Nunca retornar estadísticas proyectadas como 0 si existe un fallback de predicción.
- **Cache Integrity**: Validar la frescura de la caché comparando `db_last_updated` con `generated_at`.
- **Merge Priority**: En agregación de fuentes, priorizar UK > Org > Open.

### Calidad y Verificación
- Todos los endpoints deben estar documentados con FastAPI (Swagger).
- Ejecutar `pytest` para la lógica crítica modificada.
- Mantener `type hints` completos en todas las firmas de funciones.

---

## 🏗️ Arquitectura e Infraestructura

### Integración y Flujo
- No modificar el esquema de base de datos sin una actualización previa del modelo de dominio.
- Mantener la coherencia entre el frontend y el backend mediante contratos claros.

### Despliegue y Docker
- Mantener el archivo `render.yaml` y la configuración de Docker Compose actualizada.
- Asegurar que las variables de entorno necesarias estén documentadas en `.env.example`.

---

> [!IMPORTANT]
> Si una solicitud del usuario entra en conflicto con estas reglas, el agente debe notificarlo y solicitar aclaración antes de proceder.
