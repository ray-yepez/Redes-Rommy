# 🌐 Departamento de Redes – [Nombre del Videojuego]

> Este departamento debe contar con personas que estén dispuestas a investigar mucho, ya que los errores y complicaciones de redes suelen ser muy pesados ***(10 personas)***
---

## 📑 Tabla de Contenidos
- [📋️ Funciones del departamento](#funciones-del-departamento)
- [🛠️ Normas para Contribuir](#-normas-para-contribuir)
- [💡 Recomendaciones Técnicas](#-recomendaciones-técnicas)
- [📝 Convención de Commits Normalizados](#-convención-de-commits-normalizados)
- [📊 Uso del Kanban](#-uso-del-kanban)
- [📬 Contacto y Soporte](#-contacto-y-soporte)

---

## 📋️ Funciones del departamento

- Diseñar, implementar y mantener la capa de conectividad (sincronización, reconexión, etc.).
- Investigar y resolver errores complejos de red, latencias y pérdidas de conexión.
- Colaborar con Dpto. de Desarrollo para exponer servicios internos de forma eficiente.
- Documentar protocolos y arquitectura de red para el resto del equipo.

> 🎯 **Objetivo:** Garantizar una experiencia multijugador estable, segura y de baja latencia, manteniendo un código limpio, testeable y bien documentado.

---

## 🛠️ Normas para Contribuir

1. **Flujo de trabajo**
   - No se permiten pushes directos a `main`.
   - Crea ramas descriptivas siguiendo el formato: `tipo/descripcion-corta` (ej. `feat/matchmaking-regional`, `fix/packet-loss-rpc`) .
   - Todas las incorporaciones se realizan mediante **Pull Request (PR)**.

2. **Pull Requests**   - Incluye título claro y descripción detallada del cambio.
   - Enlaza issues/tickets relacionados (`Closes #123`, `Related to #456`).
   - Adjunta evidencia de pruebas (logs, métricas de latencia, etc.).
   - Requiere la aprobación del **líder de departamento o alguien autorizado por el mismo** en su representación.

3. **Calidad del Código**
   - Respeta el `.editorconfig` y las reglas de linter definidas en el repo.
   - Documenta cambios en protocolos, puertos, esquemas de serialización o configuraciones de servidor.

4. **Seguridad y Infraestructura**
   - Nunca commits credenciales, claves, certificados o IPs internas.
   - Usa variables de entorno o secretos gestionados por GitHub Actions / CI.
   - Cambios en infraestructura (Docker, K8s, routers, firewalls) deben pasar por revisión.

>[!note] Nota:
> El idioma para los mensajes de commit y ramas está por defninirse, pero dado que es de uso interno puede ser en español. Siempre que sea descriptivo y profesional.

---

## 💡 Recomendaciones Técnicas

*Estas recomendaciones fueron generadas por la inteligencia artificial. Pueden o no aplicar para nuestro proyecto, pero es bueno tenerlas en consideración*

- **Prioriza la autoridad del servidor**: el cliente nunca debe ser fuente de verdad para estados críticos (salud, posición, inventario, lógica de daño).
- **Predicción y reconciliación**: usa client-side prediction + server reconciliation con rollback determinista. Evita drifts acumulativos.
- **Compensación de latencia**: implementa lag compensation solo en mecánicas de impacto/colisión; documenta el margen de ventana aceptable.
- **Optimización de paquetes**: 
    - Agrupa mensajes, usa serialización binaria comprimida.
    - Prioriza delta encoding, quantization y snapshot compression.
    - Evita enviar datos redundantes o frecuencias de actualización innecesarias.
Block
- **Pruebas bajo condiciones adversas**: valida siempre con herramientas de throttling, packet loss (1-5%), jitter y alta latencia (150-300ms).
- **Seguridad**: valida todos los inputs en servidor, rate-limit por cliente, y mantén actualizadas las dependencias de criptografía/autenticación.
- **Documenta la arquitectura**: diagramas de flujo de mensajes, estados de conexión, timeouts y políticas de reconexión deben vivir en `/docs/network/`.
---

## 📝 Convención de Commits Normalizados

Utilizamos **Conventional Commits** para mantener un historial legible, automatizar versionado semántico y generar changelogs automáticamente.

### 📐 Formato
```
tipo(ámbito): descripción corta

[cuerpo opcional: explica el porqué, contexto o cambios en API/protocolos]

[pie de página opcional: notas de ruptura, referencias a issues]
```
- **tipo**: Obligatorio (ver tabla inferior)
- **ámbito**: Opcional. Módulo o sistema afectado (ej. `matchmaking`, `serialization`, `server`, `client-net`)
- **descripción**: En presente, 3a persona, sin punto final. Máx. 72 caracteres.
- **Cuerpo/Pie**: Opcional pero recomendado para cambios complejos o breaking changes.

### 🔖 Tipos de Commit Permitidos

| Tipo | Descripción | Ejemplo en Contexto de Red/Juego |
|------|-------------|----------------------------------|
| `feat` | Nueva funcionalidad o mejora visible al usuario/sistema | `feat(matchmaking): añadir cola regional con ping-based routing` |
| `fix` | Corrección de bug o comportamiento no deseado | `fix(client): resolver desincronización al reconectar tras timeout` |
| `docs` | Cambios únicamente en documentación | `docs(protocol): actualizar esquema de mensajes v2 en README` |
| `style` | Cambios de formato, espaciado, linting (sin impacto funcional) | `style(netcode): aplicar reglas de Prettier a serializadores` |
| `refactor` | Reestructuración de código sin cambiar comportamiento externo | `refactor(server): extraer lógica de validación de paquetes a clase dedicada` |
| `perf` | Mejoras de rendimiento, uso de recursos o eficiencia | `perf(udp): reducir overhead de cabeceras en mensajes de movimiento` |
| `test` | Añadir o modificar pruebas (unitarias, integración, stress) | `test(network): añadir suite de simulación de 5% packet loss` |
| `build` | Cambios en sistema de build, CI/CD, dependencias o herramientas | `build(ci): optimizar pipeline de compilación de servidor Linux` |
| `chore` | Tareas de mantenimiento, configuración, limpieza o actualizaciones menores | `chore(deps): actualizar libuv a v1.48 y ajustar Makefile` |
| `revert` | Revertir un commit anterior | `revert: deshacer "feat(matchmaking): regional queues" por fallo en staging` |

### ✅ Buenas Prácticas para Commits
- Usa verbos en imperativo (inglés): `add`, `fix`, `update`, `remove`, no `added` o `fixes`.
- Usa verbos en 3a persona (español): `añade`, `resuelve`, `actualiza`, no `añadido`, `resolver`, `limpié`, `cambios`
- Separa ámbito y descripción con dos puntos: `feat(serializer): ...`
- No mezcles múltiples tipos en un solo commit. Si tocas `fix` y `perf`, haz dos commits.
- Para **breaking changes**, añade `!` al tipo: `feat(api)!: cambiar versión de protocolo a v3`.



## 📊 Uso del Kanban
El tablero Kanban es la fuente única de verdad para el seguimiento de tareas de red. Síguelo estrictamente:
| Columna | Significado | Reglas de uso |
| ------- | ----------- | ------------- |
| `📥 Backlog` | Ideas, reportes y mejoras futuras sin prioridad definida. | Solo el líder de departamento puede promover a `To Do`. |
| `📋 To Do` | Tareas listas para desarrollo en el sprint actual. | Asigna un responsable, añade estimación (S/M/L) y enlaza rama/PR futuro. |
| `🔧 In Progress` | Desarrollo activo. Máximo 1 tarea por persona simultáneamente. | Actualiza estado diariamente. Si hay bloqueo, añade etiqueta `🚧 blocked`. |
| `👀 Review` | PR abierto, esperando revisión de código o pruebas de red en staging. | No avances hasta que el PR esté aprobado y los tests de netcode pasen. |
| `✅ Done` | Mergeado en `dev/main, verificado en build de red y documentación actualizada. | Solo el responsable puede moverla aquí tras cerrar PR y actualizar Kanban. |

### Automatización recomendada:
*Esto ya es algo avanzado, pero lo voy a dejar aquí por si acaso*

- Usa palabras clave en commits/PR para mover tarjetas automáticamente: `#<issue-id>`, `Fixes`, `Closes`, `Relates to`.
- Configura GitHub Actions para añadir etiqueta `🟢 net-ready cuando pasen los tests de conectividad y carga.
- revisa el tablero en la daily/standup; arquitecto red prioriza `In Progress y desbloquea tareas.

---
## 📬 Contacto y Soporte

- 🌐️ Líder de departamento: @Valentin-Or 
- 🔄 Scrum Master:
- 👤 Product Owner: 

---

> ⚙️ *Este README se mantiene actualizado con cada cambio significativo en la arquitectura o procesos del departamento. Las PRs que modiflan flujos de trabajo deben incluir la actualización correspondiente de este documento.*  
