# 📘 Análisis Completo de `ventana.py`

> **Archivo**: `ventana.py` (915 líneas, 38.3 KB)  
> **Propósito**: Orquestador principal del juego Rummy500 - Gestiona toda la interfaz gráfica y el flujo del juego

---

## 🎯 Resumen General

`ventana.py` es el **cerebro visual** del juego. Es el archivo que:
- Inicializa Pygame
- Crea todos los menús (inicio, salas, lobby, instrucciones)
- Gestiona eventos del mouse y teclado
- Renderiza todo en pantalla
- Coordina la comunicación entre UI y lógica de red

---

## 📦 Importaciones (Líneas 3-14)

```python
import pygame          # Motor gráfico del juego
import sys            # Para sys.exit()
import threading      # Para cargar imágenes en paralelo (línea 869-872)

from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import (
    Elemento_texto,    # Labels/texto estático
    Boton,             # Botones clickeables
    BotonRadio,        # Radio buttons para selecciones
    EntradaTexto,      # Campos de texto editables
    CartelAlerta       # Alertas/notificaciones
)
from recursos_graficos.menu import Menu  # Contenedor de elementos UI
from redes_interfaz import controladores  # Lógica de red
from logica_interfaz.mesa_interfaz import Mesa_interfaz
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
```

**¿Por qué threading?**: Para cargar las 54 imágenes de cartas + 5 del mazo en segundo plano mientras arranca el juego.

---

## 🏗️ Clase `Ventana` (Línea 18)

### 📊 Atributos de Clase (Estáticos)

#### `_cartas_imagenes` (Línea 19)
- **Tipo**: `dict | None`
- **Qué es**: Diccionario de imágenes de cartas ya cargadas
- **Por qué estático**: Para cargar UNA sola vez y compartir entre todas las instancias
- **Formato de claves**: `"Pica (A)"`, `"Corazon (5)"`, `"Especial (Joker)"`, `"Reverso"`
- **Valores**: Surfaces de Pygame (imágenes)

#### `_mazo_imagenes` (Línea 20)
- **Tipo**: `dict | None`
- **Qué es**: Diccionario con 5 imágenes del mazo (`mazo(1)` a `mazo(5)`)
- **Por qué estático**: Mismo motivo, optimización de memoria

---

### 🎬 Constructor `__init__` (Líneas 22-55)

**Propósito**: Inicializa Pygame, crea la ventana, carga recursos y construye todos los menús.

#### Paso a Paso:

```python
pygame.init()           # Inicializa sistema Pygame
pygame.font.init()      # Inicializa sistema de fuentes
```

#### `self.pantalla` (Línea 25)
- **Tipo**: `pygame.Surface`
- **Dimensiones**: `(ANCHO_VENTANA, ALTO_VENTANA)` desde constantes
- **Qué hace**: Crea la ventana del juego
- **Uso posterior**: Todas las funciones `dibujar()` pintan en esta superficie

#### `self.cartel_alerta` (Línea 26)
- **Tipo**: `CartelAlerta`
- **Qué hace**: Sistema de notificaciones emergentes (ej: "Nombre inválido")
- **Posición inicial**: `(0, 0)` - se reposiciona cuando se muestra
- **Prioridad de dibujado**: Se dibuja al FINAL (línea 865) para estar encima de todo

#### `self.lista_elementos` (Líneas 29-37)
- **Tipo**: `dict`
- **Qué es**: **ALMACÉN CENTRAL DE DATOS DE LA PARTIDA**
- **Estructura**:
  ```python
  {
      "nombre_creador": "",        # Nombre del host
      "nombre_sala": "",           # Nombre de la sala
      "cantidad_jugadores": 0,     # Cuántos jugadores seleccionados (2-7)
      "ip_sala": "",               # IP del servidor
      "lista_jugadores": [],       # Lista de jugadores conectados
      "nombre_unirse": "",         # Nombre del jugador que se une
      "salas_disponibles": []      # Lista de salas en la red
  }
  ```
- **Por qué importante**: Los menús leen/escriben aquí. Los controladores de red usan estos datos.

#### `self.elementos_creados` (Línea 40)
- **Tipo**: `list`
- **Qué contiene**: Referencias a todos los menús creados
- **Para qué**: El sistema de rendering itera sobre esta lista para dibujar solo los menús activos

#### `self.logo_rummy` (Línea 43)
- **Tipo**: `pygame.Surface`
- **Qué es**: Logo del juego
- **Dónde se usa**: Menú de inicio (línea 362)
- **⚠️ Nota**: Usa hardcoded path `"assets//Imagenes//Logos//Logo(1).png"`

#### Creación de Menús Iniciales (Líneas 46-51)

Todos estos menús se crean al iniciar, **pero solo se dibujan si están en `elementos_creados` y activos**:

```python
self.menu_instrucciones = self.Menu_instrucciones()      # Cómo jugar
self.menu_seleccion_sala = self.Menu_seleccion_sala()   # Lista de salas
self.menu_inicio = self.Menu_inicio()                    # Menú principal
self.boton_jugar = self.Boton_jugar()                    # Botón grande JUGAR
self.menu_Cantidad_Jugadores = self.Menu_Cantidad_Jugadores()  # 2-7 jugadores
self.menu_mesa_espera = self.Menu_mesa_espera()         # Lobby
```

#### `Buscar_salas` (Línea 52)
- **Tipo**: `controladores.Buscar_salas`
- **Qué hace**: Instancia el sistema de búsqueda de salas en red
- **Nota**: Variable local no usada después, ¿por qué? Probablemente inicia un thread interno

#### `self.clock` (Línea 55)
- **Tipo**: `pygame.time.Clock`
- **Para qué**: Controlar FPS del juego (línea 911: `self.clock.tick(constantes.FPS)`)
- **Efecto**: Asegura que el juego corra a velocidad constante

---

## 🛠️ Métodos de Utilidad

### `centrar(self, ancho_elemento, alto_elemento)` (Líneas 61-64)
**Propósito**: Calcular posición (x, y) para centrar un elemento en la ventana.

**Fórmula**:
```python
x = (ANCHO_VENTANA - ancho_elemento) / 2
y = (ALTO_VENTANA - alto_elemento) / 2
```

**Retorna**: `(x, y)` tupla con la posición centrada.

**Ejemplo de uso**:
```python
x, y = self.centrar(300, 200)  # Centrar un botón de 300x200
```

**Dónde se usa**: En TODOS los métodos `Menu_*()` para centrar menús.

---

### `preparar_imagenes_cartas(cls)` (Líneas 66-98)
**Tipo**: `@classmethod` (método de clase, no de instancia)

**Propósito**: Cargar TODAS las imágenes de cartas UNA sola vez.

**¿Por qué classmethod?**: Para que todas las instancias de `Ventana` compartan las mismas imágenes (ahorro de memoria).

**Lógica**:
1. **Cache check** (línea 67-68): Si ya están cargadas, retornarlas
2. **Iterar palos y números** (líneas 70-81):
   ```python
   palos = ('Pica', 'Corazon', 'Diamante', 'Trebol')
   nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')
   
   # Genera 52 cartas: Pica (A), Pica (2), ..., Trebol (K)
   for palo in palos:
       for carta in nro_carta:
           ruta = f"Imagenes/Cartas/{palo} ({carta}).png"
           cartas_imagenes[f"{palo} ({carta})"] = pygame.image.load(ruta)
   ```
3. **Cargar Joker** (líneas 84-88): `!Joker.png`
4. **Cargar reverso** (líneas 91-95): `!Reverso.png`
5. **Guardar en cache** (línea 97): `cls._cartas_imagenes = cartas_imagenes`

**Retorna**: Diccionario con 54 imágenes (52 cartas + Joker + Reverso).

**Optimización**: método `.convert_alpha()` en línea 80 optimiza el surface para transparencia.

---

### `preparar_imagenes_mazo(cls)` (Líneas 100-110)
**Tipo**: `@classmethod`

**Propósito**: Cargar imágenes del mazo (5 imágenes: `mazo1.png` a `mazo5.png`).

**Por qué 5 imágenes?**: Probablement animation/estados del mazo (lleno, medio, casi vacío, etc.).

**Lógica similar**: Cache check + loop + guardar.

**⚠️ Bug potencial** (línea 110): No retorna nada, debería tener `return cls._mazo_imagenes`.

---

### `boton_generico(...)` (Líneas 111-141)
**Propósito**: *Factory method* para crear botones con estilo consistente.

**Parámetros**:
- `x, y`: Posición
- `ancho, alto`: Tamaño
- `texto`: Texto del botón
- `accion`: Función a ejecutar al hacer click (ej: `lambda: self.salir()`)
- `tp_color`: Tipo de color (`"p"` = principal, `"s"` = secundario)
- `tp_borde`: Tipo de borde (`"i"` = intermedio, `"g"` = grueso, `"p"` = pequeño)

**Lógica**:
```python
# Líneas 114-119: Mapeo de tipo de borde
if tp_borde == "i": borde = constantes.BORDE_INTERMEDIO
elif tp_borde == "g": borde = constantes.BORDE_PRONUNCIADO
elif tp_borde == "p": borde = constantes.BORDE_LIGERO

# Líneas 120-123: Mapeo de color de borde
if tp_color == "p": color_borde = constantes.ELEMENTO_BORDE_PRINCIPAL
elif tp_color == "s": color_borde = constantes.ELEMENTO_BORDE_SECUNDARIO
```

**Retorna**: Instancia de `Boton` con todos los estilos aplicados.

**Por qué útil**: Evita repetir 15 líneas de configuración cada vez que creas un botón.

---

## 🎮 Botón Principal del Juego

### `Boton_jugar(self)` (Líneas 144-153)

**Propósito**: Crear el botón gigante "JUGAR" que se ve al iniciar el juego.

**Código paso a paso**:
```python
# 1. Centrar botón
x, y = self.centrar(
    constantes.ELEMENTO_MEDIANO_ANCHO,
    constantes.ELEMENTO_MEDIANO_ALTO
)

# 2. Definir acción: Mostrar menú de inicio
accion = lambda: controladores.Mostrar_seccion(self, self.menu_inicio)

# 3. Crear botón usando factory
boton_jugar = self.boton_generico(x, y, ancho, alto, "JUGAR", accion)

# 4. Agregarlo a la lista de elementos
self.elementos_creados.append(boton_jugar)

# 5. Retornar referencia
return boton_jugar
```

**Flujo de interacción**:
1. Usuario hace click en "JUGAR"
2. Se ejecuta `controladores.Mostrar_seccion(self, self.menu_inicio)`
3. Controlador oculta el botón JUGAR y muestra el menú de inicio

---

## 📋 Menú de Instrucciones

### `Menu_instrucciones(self)` (Líneas 156-176)

**Propósito**: Crear el menú que explica cómo jugar al Rummy 500.

**Estructura**:
```python
menu_instrucciones = Menu(...)  # Contenedor
self.crear_elementos_instrucciones(menu_instrucciones)  # Texto de reglas
self.crear_elementos_control_instrucciones(menu_instrucciones)  # Botón VOLVER
```

**Estilo visual**:
- Fondo: `ELEMENTO_FONDO_PRINCIPAL`
- Borde grueso: `BORDE_PRONUNCIADO`
- Esquinas redondeadas: `REDONDEO_PRONUNCIADO`

### `crear_elementos_instrucciones(...)` (Líneas 177-196)

**Propósito**: Agregar el texto de instrucciones al menú.

**Configuración importante**:
```python
# Línea 184: El texto viene de constantes
texto = constantes.TEXTO_DE_INSTRUCCIONES

# Líneas 185-186: Ocupa 70% de altura del menú
ancho = ANCHO_MENU_INSTRUCCIONES - (BORDE_PRONUNCIADO * 2)
alto = ALTO_MENU_INSTRUCCIONES * 0.70

# Líneas 194-195: Alineación especial
alineacion_vertical = "arriba"    # El texto empieza arriba
alineacion = "izquierda"          # Alineado a la izquierda
```

**Por qué importante**: Permite texto largo con scroll implícito.

### `crear_elementos_control_instrucciones(...)` (Líneas 197-214)

**Propósito**: Crear el botón "VOLVER" al final del menú.

**Posición**:
```python
# Centrado horizontalmente
x = (ANCHO_MENU_INSTRUCCIONES - ELEMENTO_PEQUENO_ANCHO) / 2

# Al final del menú (120% de la altura del botón desde abajo)
y = ALTO_MENU_INSTRUCCIONES - ELEMENTO_PEQUENO_ALTO * 1.2
```

**Acción**: `lambda: controladores.Mostrar_seccion(self, self.menu_inicio)` → Volver al menú principal.

---

## 👤 Menú de Nombre de Usuario

### `Menu_nombre_usuario(self, creador_sala)` (Líneas 216-237)

**Propósito**: Formulario para ingresar nombre de usuario (y datos de sala si eres el creador).

**Parámetro clave**: `creador_sala` (bool)
- `True`: Eres el host, muestra campos para nombre + nombre de sala
- `False`: Solo muestra campo para tu nombre

**Estructura visual**:
- Color secundario (`ELEMENTO_FONDO_SECUNDARO`)
- Borde secundario
- Centrado en pantalla

**Métodos auxiliares**:
- `crear_elementos_usuario()`: Campos de texto
- `crear_elementos_control_usuario()`: Botones VOLVER/CONFIRMAR

### `crear_elementos_usuario(...)` (Líneas 238-310)

**Propósito**: Crear los campos de entrada dinámicamente según si eres creador o no.

**Lógica compleja**:

```python
# Línea 239: Si eres CREADOR
textos = ("DATOS DE LA PARTIDA Y USUARIO", 
          "INGRESA TU NOMBRE", 
          "NOMBRE DE LA SALA", 
          "nombre",           # placeholder del campo
          "nombre sala")      # placeholder del campo

# Línea 242-243: Si NO eres creador
if not creador_sala:
    textos = ("INGRESA TU NOMBRE", "nombre")
```

**Distribución de elementos**:
- **Creador**: 1 título + 2 labels + 2 campos = 5 elementos en grid 2x2
- **No creador**: 1 título + 1 campo

**Validación de entrada** (líneas 289-309):
```python
permitir_espacios = False        # No puede tener espacios
permitir_numeros = False         # Solo letras
permitir_especiales = False      # Sin caracteres especiales
limite_caracteres = 20           # Máximo 20 caracteres
```

**Referencia al cartel de alerta** (línea 309):
```python
cartel_alerta = self.cartel_alerta  # Para mostrar errores de validación
```

### `crear_elementos_control_usuario(...)` (Líneas 311-342)

**Propósito**: Botones VOLVER y CONFIRMAR con comportamiento diferente según el modo.

**Lógica de acciones**:

```python
if not creador_sala:  # Modo UNIRSE
    accion_volver = lambda: Mostrar_seccion(self.menu_inicio)
    accion_confirmar = lambda: validar_y_unirse_sala(self, menu_nombre_usuario)
else:  # Modo CREAR SALA
    accion_volver = lambda: Mostrar_seccion(self.menu_Cantidad_Jugadores)
    accion_confirmar = lambda: validar_y_crear_servidor(self, menu_nombre_usuario)
```

**Por qué diferente**:
- **Unirse**: Vuelve al inicio, confirmar conecta a servidor
- **Crear**: Vuelve a selección de jugadores, confirmar crea servidor

**Posicionamiento** (líneas 326-327):
```python
# VOLVER a la izquierda (25%)
x = ANCHO_MENU * 0.25

# CONFIRMAR a la derecha (25% + 55% = 80%)
x = ANCHO_MENU * 0.80
```

---

## 🏠 Menú de Inicio (Pantalla Principal)

### `Menu_inicio(self)` (Líneas 345-364)

**Propósito**: La pantalla principal con 4 botones y el logo.

**Características únicas**:
```python
fondo_color = constantes.FONDO_VENTANA     # Mismo color que ventana (invisible)
borde_color = constantes.SIN_COLOR         # Sin borde
grosor_borde = constantes.SIN_BORDE        # Sin borde
```

**Por qué?**: Este menú ES la pantalla de inicio, no un popup. El fondo se funde con la ventana.

**Logo** (líneas 361-362):
```python
posicion_logo = (ANCHO_MENU_I * 0.05, ALTO_MENU_I * 0.1)  # Esquina superior izquierda
menu_inicio.agregar_imagen(self.logo_rummy, posicion_logo, constantes.SCALA)
```

### `crear_elementos_control_inicio(...)` (Líneas 365-392)

**Propósito**: Crear los 4 botones principales.

**Botones y acciones**:

| # | Texto | Acción |
|---|-------|--------|
| 1 | **CREAR SALA** | `Mostrar_seccion(self.menu_Cantidad_Jugadores)` |
| 2 | **UNIRSE A LA SALA** | `mostrar_menu_nombre_usuario(self, False)` |
| 3 | **COMO JUGAR** | `Mostrar_seccion(self.menu_instrucciones)` |
| 4 | **SALIR DEL JUEGO** | `self.salir()` → `pygame.quit()` + `sys.exit()` |

**Posicionamiento vertical**:
```python
incremetar_y = 0
for i, texto in enumerate(botones):
    y = (ALTO_MENU - ELEMENTO_ALTO) * (0.17 + incremetar_y)
    # Dibuja botón...
    incremetar_y += 0.25  # 25% de espacio entre botones
```

**Resultado**: Botones espaciados verticalmente con 25% de separación.

**Posición X** (línea 377):
```python
x = (ANCHO_MENU - ELEMENTO_ANCHO) * 0.9  # 90% hacia la derecha
```

**Efecto visual**: Botones alineados a la derecha, logo a la izquierda.

---

## 👥 Menú de Cantidad de Jugadores

### `Menu_Cantidad_Jugadores(self)` (Líneas 394-414)

**Propósito**: Seleccionar cuántos jugadores jugarán (2-7).

**Color**: Estilo secundario (diferente al menú principal).

**Métodos auxiliares**:
- `crear_elementos_cantidad_jugadores()`: Grid de radio buttons
- `crear_elementos_control_cantidad_jugadores()`: VOLVER/CONFIRMAR

### `crear_elementos_cantidad_jugadores(...)` (Líneas 415-473)

**Propósito**: Crear título + 6 radio buttons (2-7 jugadores).

**Título** (líneas 421-436):
```python
texto = "SELECCIONE EL NUMERO DE JUGADORES"
ancho = ELEMENTO_GRANDE_ANCHO * 2  # Doble de ancho
posicion_y = 0.10  # 10% desde arriba
```

**Radio Buttons** (líneas 439-472):

**Generación de textos**:
```python
texto_menu = (f"{i} JUGADORES" for i in range(2, 8))
# Genera: "2 JUGADORES", "3 JUGADORES", ..., "7 JUGADORES"
```

**Grid Layout** (3 columnas):
```python
posiciones_x = [0.04, 0.50, 0.96]  # Izquierda, centro, derecha

for i, texto in enumerate(texto_menu):
    columna = i % 3        # 0, 1, 2, 0, 1, 2
    fila = i // 3          # 0, 0, 0, 1, 1, 1
    posicion_x = posiciones_x[columna]
    posicion_y = 0.30 + (0.30 * fila)  # Fila 0: 30%, Fila 1: 60%
```

**Resultado visual**:
```
| 2 JUGADORES | 3 JUGADORES | 4 JUGADORES |
| 5 JUGADORES | 6 JUGADORES | 7 JUGADORES |
```

**Deshabilitar 6-7 jugadores** (líneas 449-451):
```python
deshabilitado = False
if i+2 in (6, 7):  # Si es el botón de 6 o 7 jugadores
    deshabilitado = True
```

**Por qué?**: Solo 2-5 jugadores están implementados actualmente.

**Grupo de radio** (línea 469):
```python
grupo = grupo_radio  # Todos los botones comparten el mismo grupo
valor = (i+2)        # Valor: 2, 3, 4, 5, 6, 7
```

**Efecto**: Solo un botón puede estar seleccionado a la vez. El valor seleccionado está en `grupo_radio[X].valor`.

**Retorna** (línea 473): `posicion_y` (la última posición Y usada) para posicionar los botones de control debajo.

### `crear_elementos_control_cantidad_jugadores(...)` (Líneas 474-507)

**Propósito**: VOLVER y CONFIRMAR.

**Acciones**:
- **VOLVER**: `Mostrar_seccion(self.menu_inicio)`
- **CONFIRMAR**: `mostrar_menu_nombre_usuario(self, True)` ← `True` = eres creador

**Posicionamiento dinámico** (línea 477):
```python
y = (ALTO_MENU - ELEMENTO_ALTO) * (posicion_y + 0.3)
```

**Por qué usar `posicion_y`?**: Para que los botones siempre estén debajo de los radio buttons, sin importar cuántas filas haya.

---

## ⏳ Menú de Mesa de Espera (Lobby)

### `Menu_mesa_espera(self)` (Líneas 510-529)

**Propósito**: Mostrar la sala de espera mientras todos los jugadores se conectan.

**Color**: Terciario (`ELEMENTO_FONDO_TERCIARIO`) - diferente para distinguir del resto.

**Característica clave** (línea 527):
```python
menu_mesa_espera.elemento_texto_espera = elemento_texto
```

**Por qué importante**: Guarda referencia al elemento de texto para actualizarlo dinámicamente cuando se conecta un jugador.

### `crear_elementos_mesa_espera(...)` (Líneas 530-552)

**Propósito**: Crear el elemento de texto centrado que muestra el estado.

**Tamaño grande** (líneas 531-532):
```python
ancho = ELEMENTO_GRANDE_ANCHO * 1.7   # 170% del ancho grande
alto = ELEMENTO_MEDIANO_ALTO * 3.2    # Altura de 3.2 elementos medianos
```

**Texto dinámico** (línea 540):
```python
texto = self.texto_menu_mesa_espera()  # Genera el texto actual
```

**Estilo** (líneas 543-550):
- Fuente llamativa (`FUENTE_LLAMATIVA`)
- Color de texto secundario
- Sin borde
- Alineación a la izquierda

### `texto_menu_mesa_espera(self)` (Líneas 554-577)

**Propósito**: Generar el texto dinámico del lobby.

**Lógica**:
```python
# Lee datos desde el diccionario central
lista_jugadores = self.lista_elementos.get("lista_jugadores") or []
jugadores_actuales = len(lista_jugadores)
max_esperados = self.lista_elementos.get("cantidad_jugadores", 0)
nombre_sala = self.lista_elementos.get("nombre_sala", "No definido")
nombre_creador = self.lista_elementos.get("nombre_creador", "No definido")

# Calcula cuántos faltan
faltan = max(0, max_esperados - jugadores_actuales)

# Genera texto formateado
texto = (
    f"NOMBRE DE LA SALA: {nombre_sala}\n"
    f"CREADOR DE LA SALA: {nombre_creador}\n"
    f"JUGADORES CONECTADOS: {jugadores_actuales}/{max_esperados}\n"
    f"ESPERANDO JUGADORES...\nFALTAN: {faltan}"
)
```

**Logging** (líneas 571-575): Imprime en consola para debugging.

**Ejemplo de output**:
```
NOMBRE DE LA SALA: SalaJeiker
CREADOR DE LA SALA: Jeiker
JUGADORES CONECTADOS: 2/4
ESPERANDO JUGADORES...
FALTAN: 2
```

### `actualizar_mesa_espera(self)` (Líneas 579-606)

**Propósito**: Actualizar el texto cuando se conecta/desconecta un jugador.

**Lógica**:
1. **Verificar que el menú existe** (línea 583)
2. **Generar nuevo texto** (línea 585)
3. **Actualizar el elemento de texto** (líneas 589-600):

```python
if hasattr(self.menu_mesa_espera, 'elemento_texto_espera'):
    # Método 1: Si tiene referencia guardada
    self.menu_mesa_espera.elemento_texto_espera.texto = texto_actualizado
    self.menu_mesa_espera.elemento_texto_espera.prepar_texto()  # Re-renderizar
else:
    # Método 2: Buscar en la lista de botones
    for boton in self.menu_mesa_espera.botones:
        if isinstance(boton, Elemento_texto):
            boton.texto = texto_actualizado
            boton.prepar_texto()
            break
```

**Si no existe** (líneas 602-606): Crea un nuevo menú y lo muestra.

**Cuándo se llama**: Desde código de networking cuando hay cambios en `lista_jugadores`.

---

## 📡 Menú de Selección de Salas

### `Menu_seleccion_sala(self)` (Líneas 610-672)

**Propósito**: Mostrar lista de salas disponibles en la red para unirse.

**Estructura**:
1. Título: "ELIJA LA SALA" (líneas 626-641)
2. Obtener salas (línea 644): `salas_disponibles = self.lista_elementos["salas_disponibles"]`
3. **(A)** Si hay salas: Crear botones (línea 666)
4. **(B)** Si NO hay salas: Mostrar mensaje "No hay salas disponibles" (líneas 647-663)
5. Botones de control: VOLVER, ACTUALIZAR, CONFIRMAR (línea 669)

### `crear_botones_salas(self, menu, salas)` (Líneas 673-717)

**Propósito**: Crear un radio button por cada sala disponible.

**Formato de datos de sala**:
```python
sala = {
    "nombre": "SalaDeJeiker",
    "jugadores": 2,           # Actualmente conectados
    "max_jugadores": 4,       # Máximo permitido
    # ... otros datos
}
```

**Grid de 3 columnas** (líneas 676-678):
```python
columnas = 3
espaciado_x = ANCHO_MENU * 0.05  # 5% de separación horizontal
espaciado_y = ALTO_MENU * 0.05   # 5% de separación vertical
```

**Cálculo de posición** (líneas 684-688):
```python
for i, sala in enumerate(salas):
    fila = i // columnas      # 0, 0, 0, 1, 1, 1, 2, 2, 2...
    columna = i % columnas    # 0, 1, 2, 0, 1, 2, 0, 1, 2...
    
    x_pos = espaciado_x + columna * (ancho_boton + espaciado_x)
    y_pos = ALTO_MENU * 0.22 + fila * (alto_boton + espaciado_y)
```

**Verificar si está llena** (línea 691):
```python
sala_llena = sala["jugadores"] >= sala["max_jugadores"]
```

**Texto del botón** (línea 694):
```python
texto_sala = f"{sala['nombre']}/{sala['jugadores']}/{sala['max_jugadores']}"
# Ejemplo: "SalaJeiker/2/4"
```

**Deshabilitar si está llena** (línea 715):
```python
deshabilitado = sala_llena  # No puedes unirte a sala llena
```

**Valor del radio button** (línea 714):
```python
valor = sala  # El valor es el diccionario completo de la sala
```

**Por qué?**: Al seleccionar el botón, puedes acceder a toda la información de la sala.

### `agregar_botones_control_salas(self, menu)` (Líneas 718-744)

**Propósito**: 3 botones en la parte inferior.

**Botones y acciones**:

| Botón | Acción | Descripción |
|-------|--------|-------------|
| **VOLVER** | `Mostrar_seccion(self.menu_nombre_usuario)` | Vuelve al formulario de nombre |
| **ACTUALIZAR** | `self.actualizar_lista_salas()` | Refresca la lista de salas |
| **CONFIRMAR** | `Unirse_a_sala_seleccionada(self, menu)` | Une a la sala seleccionada |

**Posicionamiento horizontal** (líneas 729-744):
```python
incremento_x = 0.05  # Comienza en 5%

for i, texto in enumerate(botones):
    x = x_total * incremento_x
    # Dibuja botón...
    incremento_x += 0.45  # Siguiente en 50% (0.05 + 0.45)
```

**Resultado**: Botones espaciados horizontalmente: 5%, 50%, 95%.

### `actualizar_lista_salas(self)` (Líneas 747-756)

**Propósito**: Refrescar la lista de salas (llamado al hacer click en ACTUALIZAR).

**Lógica**:
1. **Remover menú actual** (líneas 751-752)
2. **Crear nuevo menú** (línea 755): `self.menu_seleccion_sala = self.Menu_seleccion_sala()`
3. **Mostrarlo** (línea 756): `Mostrar_seccion(self, self.menu_seleccion_sala)`

**Por qué recrear todo?**: Más simple que actualizar cada botón individualmente.

**⚠️ Nota**: El diccionario `self.lista_elementos["salas_disponibles"]` debe ser actualizado por el código de red ANTES de llamar esto.

---

## 🚪 Función de Salida

### `salir(self)` (Líneas 760-762)

**Propósito**: Cerrar el juego limpiamente.

```python
pygame.quit()  # Cierra Pygame y libera recursos
sys.exit()     # Termina el proceso de Python
```

**Cuándo se llama**: Al hacer click en "SALIR DEL JUEGO" en el menú principal.

---

## 📚 Funciones de Organización

### `menus_condicionales(self)` (Líneas 763-773)

**Propósito**: Retornar lista de **nombres** de menús que pueden o no existir.

```python
menu_condicional = [
    "menu_mesa_espera",      # Puede no existir aún
    "menu_nombre_creador",   # Legacy? No veo dónde se crea
    "menu_nombre_usuario",   # Se crea dinámicamente
    "menu_seleccion_sala",   # Existe desde __init__
    "mesa",                  # Mesa de juego (creada al iniciar partida)
    "mesa_opciones",         # Menú de opciones en partida
    "menu_instrucciones"     # Existe desde __init__
]
```

**Por qué lista de strings?**: Se usan con `hasattr()` y `getattr()` para verificar/acceder dinámicamente.

### `menus_principales(self)` (Líneas 774-781)

**Propósito**: Retornar lista de **objetos** de menús que siempre existen.

```python
menus = [
    self.menu_seleccion_sala, 
    self.menu_instrucciones, 
    self.menu_inicio, 
    self.menu_Cantidad_Jugadores
]
```

**Diferencia con `menus_condicionales`**: Estos SIEMPRE existen (creados en `__init__`).

**Uso**: En `ejecutar_manejo_eventos()` y `ejecutar_dibujado()` para iterar sobre menús.

---

## 🎮 Sistema de Eventos

### `ejecutar_manejo_eventos(self, evento)` (Líneas 783-813)

**Propósito**: Distribuir eventos de Pygame (clicks, teclas) a todos los elementos.

**Flujo de prioridad**:

```python
# 1. PRIORIDAD MÁXIMA: Cartel de alerta
if self.cartel_alerta.manejar_evento(evento):
    return  # Si el cartel está activo, ignora todo lo demás

# 2. Botón JUGAR
self.boton_jugar.manejar_evento(evento)

# 3. Menús principales
for menu in self.menus_principales():
    menu.manejar_eventos(evento)

# 4. Menús condicionales
for menu_name in self.menus_condicionales():
    if hasattr(self, menu_name):
        getattr(self, menu_name).manejar_eventos(evento)

# 5. Menús activos de la mesa (si está en partida)
if hasattr(self, 'mesa') and self.mesa and hasattr(self.mesa, 'menus_activos'):
    for menu in self.mesa.menus_activos:
        menu.manejar_eventos(evento)

# 6. Menú de instrucciones (doble check?)
if self.menu_instrucciones in self.elementos_creados:
    self.menu_instrucciones.manejar_eventos(evento)

# 7. Detección de tecla TAB (líneas 808-813)
if evento.type == pygame.KEYDOWN:
    self.last_key_time = pygame.time.get_ticks()  # Timestamp
```

**Por qué el orden importa**: Los elementos que están "encima" visualmente deben procesar eventos primero.

**Doble procesamiento de instrucciones** (línea 805): Posible bug o redundancia.

### `ejecutar_verificacion_hovers(self, posicion_raton)` (Líneas 815-835)

**Propósito**: Actualizar estado de hover de todos los botones cuando el mouse se mueve.

**Lógica similar** a `ejecutar_manejo_eventos`:
```python
# 1. Cartel de alerta
self.cartel_alerta.verificar_hover(posicion_raton)

# 2. Botón JUGAR
self.boton_jugar.verificar_hover(posicion_raton)

# 3. Menús principales
for menu in self.menus_principales():
    menu.verificar_hovers(posicion_raton)

# 4. Menús condicionales
for menu_name in self.menus_condicionales():
    if hasattr(self, menu_name):
        getattr(self, menu_name).verificar_hovers(posicion_raton)

# 5. Menús de la mesa
if hasattr(self, 'mesa') and self.mesa:
    for menu in self.mesa.menus_activos:
        menu.verificar_hovers(posicion_raton)
```

**Efecto**: Los botones cambian de color cuando pasas el mouse sobre ellos.

### `ejecutar_dibujado(self)` (Líneas 837-865)

**Propósito**: Renderizar todos los elementos visibles en pantalla.

**Orden de dibujado** (de atrás hacia adelante):

```python
# 1. Limpiar pantalla con color de fondo
self.pantalla.fill(constantes.FONDO_VENTANA)

# 2. Botón JUGAR
self.boton_jugar.dibujar()

# 3. Menús principales
for menu in self.menus_principales():
    menu.dibujar_menu()

# 4. Menús condicionales (excepto 'mesa' si tiene submenús)
for nombre_menu in self.menus_condicionales():
    if hasattr(self, nombre_menu):
        menu = getattr(self, nombre_menu)
        
        # Skip mesa si tiene menús activos (líneas 852-853)
        if nombre_menu == "mesa" and hasattr(self.mesa, 'menus_activos'):
            continue
        
        menu.dibujar_menu()

# 5. Menús activos de la mesa (encima de todo)
if hasattr(self, 'mesa') and self.mesa:
    for menu in self.mesa.menus_activos:
        menu.dibujar_menu()

# 6. Cartel de alerta (SIEMPRE AL FINAL - máxima prioridad visual)
self.cartel_alerta.dibujar()
```

**Por qué el orden?**: Los elementos dibujados después aparecen encima de los anteriores.

**Decisión de diseño** (líneas 852-853): Si la mesa tiene menús activos (ej: menú de pausa), no dibujar la mesa completa, solo los menús.

---

## 🔄 Bucle Principal del Juego

### `Correr_juego(self)` (Líneas 866-912)

**Propósito**: El **game loop** principal que mantiene el juego corriendo.

#### Inicialización (Líneas 867-872)

```python
ejecutar = True  # Flag de control

# Cargar imágenes en threads paralelos
hilo_imagenes_cartas = threading.Thread(target=Ventana.preparar_imagenes_cartas)
hilo_imagenes_mazo = threading.Thread(target=Ventana.preparar_imagenes_mazo)
hilo_imagenes_cartas.start()
hilo_imagenes_mazo.start()
```

**Por qué threads?**: Para no congelar la ventana mientras carga 59 imágenes (54 cartas + 5 mazos).

**Efecto**: El juego arranca instantáneamente, las cartas se cargan en background.

#### Bucle Principal (Líneas 874-911)

```python
while ejecutar:
    # 1. OBTENER ESTADO DEL MOUSE
    posicion_raton = pygame.mouse.get_pos()
    
    # 2. OBTENER EVENTOS (clicks, teclas, cerrar ventana)
    eventos = pygame.event.get()
    
    # 3. ACTUALIZAR HOVERS (botones iluminándose)
    self.ejecutar_verificacion_hovers(posicion_raton)
    
    # 4. PROCESAR EVENTOS
    for evento in eventos:
        # Evento de cerrar ventana
        if evento.type == pygame.QUIT:
            controladores.Salir()
            ejecutar = False
        
        # Modificación de datos (probablemente inputs de red)
        controladores.modificacion_real_datos(self, evento, constantes)
        
        # Eventos de UI
        self.ejecutar_manejo_eventos(evento)
    
    # 5. LIMPIAR PANTALLA
    self.pantalla.fill(constantes.FONDO_VENTANA)
    
    # 6. DIBUJAR TODO
    self.ejecutar_dibujado()
    
    # 7. MOSTRAR TABLA DE PUNTUACIÓN AL PRESIONAR TAB (líneas 891-908)
    try:
        keys = pygame.key.get_pressed()
        if hasattr(self, 'mesa_juego') and self.mesa_juego:
            if keys[pygame.K_TAB]:
                # Mostrar overlay de puntuación
                self.mesa_juego.mostrar_menu_puntuacion()
            else:
                # Ocultar overlay
                self.mesa_juego.ocultar_menu_puntuacion()
            
            # Dibujar si está visible
            if (hasattr(self.mesa_juego, 'menu_puntuacion') and 
                self.mesa_juego.menu_puntuacion.visible):
                self.mesa_juego.menu_puntuacion.dibujar_menu()
    except Exception as e:
        print(f"Error al mostrar tabla de puntuación: {e}")
    
    # 8. ACTUALIZAR PANTALLA (mostrar frame)
    pygame.display.flip()
    
    # 9. CONTROLAR FPS
    self.clock.tick(constantes.FPS)  # Espera para mantener FPS constante

# SALIR DEL JUEGO
pygame.quit()
```

#### Detalles Importantes:

**Línea 883**: `controladores.modificacion_real_datos(self, evento, constantes)`
- **Qué hace**: Probablemente procesa datos que vienen de la red (mensajes del servidor)
- **Por qué importante**: Mantiene sincronizado el estado del juego con otros jugadores

**Líneas 891-908**: Feature de tabla de puntuación
- **Funcionalidad**: Mantener presionado TAB muestra puntuaciones
- **Try-except**: Para no romper el juego si hay un error en esta feature

**Línea 910**: `pygame.display.flip()`
- **Qué hace**: Actualiza la pantalla con todo lo dibujado
- **Alternativa**: `pygame.display.update()` solo actualiza partes modificadas

**Línea 911**: `self.clock.tick(constantes.FPS)`
- **Qué hace**: Pausa el tiempo necesario para mantener FPS constante
- **Ejemplo**: Si FPS=60, espera 16.67ms entre frames

---

## 🚀 Inicio del Programa (Líneas 914-915)

```python
ventana = Ventana()      # Crear instancia
ventana.Correr_juego()   # Iniciar game loop
```

**Por qué al final del archivo?**: Es la práctica estándar de Python para archivos ejecutables.

**Consecuencia**: Al ejecutar `python ventana.py`, el juego arranca inmediatamente.

---

## 📊 Resumen de Atributos de Instancia

| Atributo | Tipo | Propósito |
|----------|------|-----------|
| `pantalla` | `pygame.Surface` | Ventana del juego |
| `cartel_alerta` | `CartelAlerta` | Sistema de notificaciones |
| `lista_elementos` | `dict` | **Datos centrales de la partida** |
| `elementos_creados` | `list` | Lista de menús creados |
| `logo_rummy` | `pygame.Surface` | Logo del juego |
| `menu_instrucciones` | `Menu` | Menú "Cómo Jugar" |
| `menu_seleccion_sala` | `Menu` | Lista de salas |
| `menu_inicio` | `Menu` | Pantalla principal |
| `boton_jugar` | `Boton` | Botón grande inicial |
| `menu_Cantidad_Jugadores` | `Menu` | Selector 2-7 jugadores |
| `menu_mesa_espera` | `Menu` | Lobby de espera |
| `clock` | `pygame.time.Clock` | Controlador de FPS |
| `last_key_time` | `int` (opcional) | Timestamp de última tecla |
| `mesa` | `Mesa_interfaz` (condicional) | Mesa de juego activa |
| `mesa_juego` | `Mesa_juego` (condicional) | Lógica de la mesa |
| `menu_nombre_usuario` | `Menu` (condicional) | Formulario de nombre |

---

## 🔗 Flujos de Navegación

### Crear Sala (Creador)

```
JUGAR
  ↓
MENU INICIO → Click "CREAR SALA"
  ↓
CANTIDAD DE JUGADORES → Seleccionar (2-5) → CONFIRMAR
  ↓
NOMBRE USUARIO (creador=True) → Ingresar nombre + nombre sala → CONFIRMAR
  ↓
MESA ESPERA → Espera jugadores...
  ↓
[Cuando sala llena] → INICIA PARTIDA
```

### Unirse a Sala

```
JUGAR
  ↓
MENU INICIO → Click "UNIRSE A LA SALA"
  ↓
NOMBRE USUARIO (creador=False) → Ingresar nombre → CONFIRMAR
  ↓
SELECCIÓN SALA → Ver salas → Seleccionar → CONFIRMAR
  ↓
MESA ESPERA → Espera...
  ↓
[Cuando sala llena] → INICIA PARTIDA
```

### Instrucciones

```
JUGAR
  ↓
MENU INICIO → Click "COMO JUGAR"
  ↓
INSTRUCCIONES → VOLVER
  ↓
MENU INICIO
```

---

## ⚙️ Patrones de Diseño Identificados

### 1. **Factory Pattern**
- `boton_generico()` crea botones con configuración consistente

### 2. **Builder Pattern**
- Métodos `crear_elementos_*()` construyen menús paso a paso

### 3. **Observer Pattern** (implícito)
- `lista_elementos` actúa como modelo observado
- Menús se actualizan cuando cambian los datos

### 4. **State Pattern** (implícito)
- Diferentes menús representan diferentes estados del juego
- `elementos_creados` controla qué estado es visible

### 5. **Singleton Pattern** (clase)
- `_cartas_imagenes` y `_mazo_imagenes` son atributos de clase (compartidos)

---

## 🐛 Bugs y Mejoras Potenciales

### Bugs Identificados:

1. **Línea 110**: `preparar_imagenes_mazo()` no retorna el diccionario
2. **Línea 805**: Doble procesamiento de eventos en `menu_instrucciones`
3. **Línea 52**: `Buscar_salas` instanciado pero no guardado en atributo

### Mejoras Potenciales:

1. **Hardcoded paths** (línea 43): Usar rutas relativas o configuración
2. **Mezcla de responsabilidades**: Ventana debería delegar más lógica a controladores
3. **Menús creados pero no usados**: `menu_nombre_creador` está en lista pero no se crea
4. **Try-except genérico** (línea 906): Debería especificar el tipo de excepción
5. **Nombres inconsistentes**: `menu_Cantidad_Jugadores` usa PascalCase, otros snake_case

---

## 📈 Métricas del Código

- **Líneas totales**: 915
- **Métodos públicos**: 21
- **Menús principales**: 6
- **Patrones de diseño**: 5
- **Dependencias externas**: 3 (pygame, sys, threading)
- **Acoplamiento con `controladores`**: Alto (llamadas en múltiples lugares)

---

## 🎓 Conclusión

`ventana.py` es el **orquestador maestro** del juego Rummy500:

✅ **Bien hecho**:
- Organización clara de menús
- Sistema de eventos robusto
- Separación de creación/control de menús
- Optimización de carga de imágenes con threading
- Sistema de actualización dinámica de UI

⚠️ **Áreas de mejora**:
- Reducir acoplamiento con `controladores`
- Estandarizar nomenclatura
- Extraer constantes hardcodeadas
- Mejor manejo de errores específicos
- Documentación de flujos complejos

**Para desarrolladores nuevos**: Este archivo es el mejor punto de partida para entender cómo funciona la UI del juego. Cada menú sigue un patrón similar: `Menu_X()` → `crear_elementos_X()` → `crear_elementos_control_X()`.
