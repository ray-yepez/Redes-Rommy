# 🎴 Rummy 500

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Juego de cartas Rummy 500 multijugador con interfaz gráfica completa**

[Características](#-características) • [Instalación](#-instalación) • [Cómo Jugar](#-cómo-jugar) • [Estructura](#-estructura-del-proyecto)

</div>

---

## 🎯 Descripción

**Rummy 500** es una implementación completa del popular juego de cartas, desarrollada en Python con Pygame. El proyecto incluye una interfaz gráfica intuitiva, sistema multijugador en red con arquitectura cliente-servidor, y todas las reglas oficiales del Rummy 500.

### ✨ Características

- 🎮 **Interfaz gráfica completa** con menús intuitivos y cartas visuales
- 🌐 **Multijugador en red** (2-7 jugadores, actualmente 2-5 habilitados)
- 🏠 **Sistema de salas** con lobby de espera
- 🔄 **Reconexión automática** al servidor
- 🎲 **Lógica de juego completa**:
  - Validación de tríos y seguidillas
  - Sistema de compra entre jugadores
  - Extensión de jugadas
  - Reemplazo de cartas en jugadas existentes
  - Manejo de Jokers
  - Cálculo automático de puntuaciones
- 🎨 **Diseño visual atractivo** con sistema de colores y fuentes personalizadas
- 📡 **Sincronización de estado** entre todos los jugadores

---

## 📋 Requisitos Previos

- **Python 3.8** o superior
- **Pygame 2.0** o superior
- Sistema operativo: Windows, Linux, macOS

---

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/JeikerM19/Rummy500-Completo.git
cd Rummy500-Completo
```

### 2. Instalar dependencias

```bash
pip install pygame
```

O si tienes un archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Verificar instalación

Asegúrate de que la carpeta `assets` contiene las imágenes de las cartas y fuentes necesarias.

---

## 🚀 Cómo Jugar

### Iniciar el juego

```bash
python ventana.py
```

### Opciones del menú principal

#### 🏠 **Crear Sala** (Ser Host)

1. Click en **"CREAR SALA"**
2. Selecciona la **cantidad de jugadores** (2-5)
3. Ingresa:
   - **Tu nombre**
   - **Nombre de la sala**
4. Click en **"CONFIRMAR"**
5. Espera en el **lobby** hasta que todos los jugadores se unan
6. El juego inicia automáticamente cuando la sala esté llena

#### 🚪 **Unirse a una Sala**

1. Click en **"UNIRSE A LA SALA"**
2. Ingresa **tu nombre**
3. Click en **"CONFIRMAR"**
4. Selecciona una **sala disponible** de la lista
   - Formato: `Nombre/Jugadores actuales/Máximo`
5. Click en **"CONFIRMAR"** para unirte
6. Espera en el lobby hasta que inicie la partida

#### 📖 **Cómo Jugar** (Tutorial)

Click en **"COMO JUGAR"** para ver las reglas del Rummy 500.

---

## 🎲 Reglas del Rummy 500

### Objetivo
Ser el primer jugador en quedarse sin cartas formando combinaciones válidas.

### Combinaciones Válidas

- **Trío**: 3 o más cartas del mismo número (ej: 7♠ 7♥ 7♦)
- **Seguidilla**: 3 o más cartas consecutivas del mismo palo (ej: 4♠ 5♠ 6♠)
- **Joker**: Comodín que puede sustituir cualquier carta

### Flujo del Juego

1. **Primera Jugada**: Debes bajar al menos 3 cartas válidas
2. **Turno**:
   - Roba una carta del **mazo cerrado** o del **descarte**
   - Opcionalmente: extiende jugadas en la mesa
   - **Descarta** una carta para terminar tu turno
3. **Compra**: Si descartas, otros jugadores pueden "comprarla" + robar carta extra
4. **Joker Descartado**: Se quema automáticamente
5. **Victoria**: El primer jugador sin cartas gana la ronda

### Después de la Primera Jugada

- Extender tríos/seguidillas existentes
- Reemplazar cartas en jugadas (tomando el Joker, por ejemplo)
- Robar del mazo o descarte en cada turno

---

## 📁 Estructura del Proyecto

```
Rummy500-Completo/
│
├── assets/                          # Recursos gráficos
│   ├── Imagenes/
│   │   ├── Cartas/                  # 52 cartas + Joker + Reverso
│   │   ├── Logos/                   # Logo del juego
│   │   └── Mazo/                    # Imágenes del mazo
│   └── fuentes/                     # Fuentes tipográficas
│
├── logica_juego/                    # Motor del juego (lógica pura)
│   ├── cartas.py                    # Clase Cartas
│   ├── mazo.py                      # Clase Mazo (barajar, repartir)
│   ├── jugador.py                   # Clase Jugador
│   ├── jugadas.py                   # Validación de jugadas (tríos, seguidillas)
│   ├── mesa.py                      # Control de turnos y flujo del juego
│   └── principal.py                 # Punto de entrada para juego local
│
├── logica_interfaz/                 # Adaptadores gráficos
│   ├── cartas_interfaz.py           # Representación visual de cartas
│   ├── mazo_interfaz.py             # Animaciones del mazo
│   ├── mesa_interfaz.py             # Mesa de juego visual
│   └── core/                        # Componentes UI avanzados
│
├── recursos_graficos/               # Sistema de interfaz de usuario
│   ├── elementos_de_interfaz_de_usuario.py  # Botones, campos, alertas
│   ├── constantes.py                # Colores, fuentes, tamaños
│   └── menu.py                      # Clase Menu genérica
│
├── redes_juego/                     # Sistema de networking
│   ├── server_main.py               # Servidor de juego
│   ├── client_main.py               # Cliente con reconexión
│   ├── conexion.py                  # Protocolos de red
│   └── core/                        # Lógica de red avanzada
│
├── redes_interfaz/                  # Controladores (red + UI)
│   └── controladores.py             # Acciones de botones y eventos
│
├── ventana.py                       # Ventana principal (915 líneas)
├── id_jugador.txt                   # ID local para reconexión
└── __init__.py
```

### Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| `logica_juego/` | Lógica pura del juego (independiente de UI) |
| `logica_interfaz/` | Adapta lógica para renderizado visual |
| `recursos_graficos/` | Elementos UI reutilizables (botones, menús) |
| `redes_juego/` | Cliente-servidor y sincronización |
| `redes_interfaz/` | Conecta eventos UI con acciones de red |
| `ventana.py` | Orquestador principal del juego |

---

## 🛠️ Configuración de Red

### Puerto por Defecto
El servidor usa el puerto **5555** (configurable en `conexion.py`).

### IP del Servidor
- **Crear sala**: Servidor en `127.0.0.1` (localhost)
- **Unirse**: Ingresa la IP del host de la sala

### Reconexión Automática
El juego guarda tu ID de jugador en `id_jugador.txt` para reconectarte si pierdes conexión.

---

## 🐛 Solución de Problemas

### El juego no inicia
```bash
# Verifica que Pygame esté instalado
python -m pygame.examples.aliens
```

### No encuentra las imágenes
- Asegúrate de ejecutar `python ventana.py` desde la raíz del proyecto
- Verifica que la carpeta `assets/Imagenes/Cartas/` existe

### Error de conexión en red
- Verifica que el firewall permita Python
- El host debe compartir su IP con los demás jugadores
- Ambos deben estar en la misma red (o usar port forwarding)

### Falta `requirements.txt`
Crea uno con:
```
pygame>=2.0.0
```

---

## 🎮 Controles

- **Mouse**: Navegación de menús y selección de cartas
- **Teclado**: Ingreso de nombres y datos

---

## 📊 Estadísticas del Proyecto

- **Lenguaje**: Python
- **Framework**: Pygame
- **Archivos**: ~120
- **Líneas de código**: ~40,000
- **Arquitectura**: MVC + Cliente-Servidor

---

## 🤝 Contribuir

¿Quieres mejorar el proyecto? Algunos TODOs pendientes:

- [ ] Implementar búsqueda de salas desde la red (actualmente mock)
- [ ] Habilitar partidas de 6-7 jugadores
- [ ] Agregar sistema de puntuación acumulativa entre rondas
- [ ] Implementar chat en el lobby
- [ ] Añadir efectos de sonido
- [ ] Crear modo "espectador"

---

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

---

## 👤 Autor

**Jeiker M19**

- GitHub: [@JeikerM19](https://github.com/JeikerM19)

---

## 📝 Notas Adicionales

### Versión Actual
- Solo están habilitados partidas de 2-5 jugadores
- La búsqueda de salas aún usa datos de ejemplo (ver línea 1 de `ventana.py`)

### Características Experimentales
- **Reemplazo de cartas en jugadas**: Nueva funcionalidad agregada recientemente

---

<div align="center">

**¿Disfrutas el juego? ¡Dale una ⭐ al proyecto!**

</div>
