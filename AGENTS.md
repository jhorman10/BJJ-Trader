# 🤖 Agentes Especializados - BJJ-BetSports

Este repositorio utiliza una arquitectura de agentes especializados para guiar el desarrollo y mantener la coherencia con las reglas del proyecto (`RULES.md`).

## 📋 Directorio de Agentes

| Agente | Rol | Fuente (.github) | Ejecución (.claude) |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | Clasificación, delegación y flujo Specs-First | [.github/agents/hypergenia-orchestrator.agent.md](.github/agents/hypergenia-orchestrator.agent.md) | [.claude/agents/orchestrator.md](.claude/agents/orchestrator.md) |
| **Frontend** | React 19, Vite, MUI y lógica de interfaz | [.github/agents/hypergenia-frontend.agent.md](.github/agents/hypergenia-frontend.agent.md) | [.claude/agents/frontend.md](.claude/agents/frontend.md) |
| **Backend** | FastAPI, Python, ML y lógica de negocio | [.github/agents/hypergenia-backend.agent.md](.github/agents/hypergenia-backend.agent.md) | [.claude/agents/backend.md](.claude/agents/backend.md) |
| **Architecture** | Decisiones cross-cutting e infraestructura | [.github/agents/hypergenia-architecture.agent.md](.github/agents/hypergenia-architecture.agent.md) | [.claude/agents/architecture.md](.claude/agents/architecture.md) |

## 🚀 Flujo de Trabajo (Specs-First)

Para cualquier tarea que implique cambios de código, se debe seguir el protocolo **Spec Kit**:

1.  **Orquestación**: El `Orchestrator` recibe la solicitud y la clasifica.
2.  **Especificación**: `/speckit.specify` genera la especificación de la funcionalidad.
3.  **Planificación**: `/speckit.plan` define el enfoque técnico.
4.  **Tareas**: `/speckit.tasks` genera la lista de tareas accionables.
5.  **Implementación**: El especialista asignado (Frontend/Backend) ejecuta las tareas.

## ⚖️ Reglas Mandatarias

- Todas las respuestas deben ser en **español**.
- El cumplimiento de `RULES.md` es obligatorio para todos los agentes.
- No se permite la implementación sin una especificación previa generada por el Orchestrator.
