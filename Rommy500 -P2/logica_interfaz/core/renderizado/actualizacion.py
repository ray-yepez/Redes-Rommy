"""Módulo interno para actualización de elementos visuales"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes

Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)


class ActualizacionMixin:
    """Mixin con métodos para actualización de elementos visuales"""
    
    def actualizar_mazo(self,mesa):
        if self.elementos_mesa["cantidad_cartas_mazo"]:
            # Eliminar mazo antiguo
            mazo_antiguo = self.referencia_elementos.get("elemento_mazo")
            if mazo_antiguo:
                mesa.botones.remove(mazo_antiguo)
                self.referencia_elementos["elemento_mazo"] = []
            
            # Calcular posición del mazo usando método auxiliar
            x_relativo, y_relativo, _, _ = self._calcular_posicion_mazo()
            scala = constantes.ESCALA_CARTAS
            accion = lambda: print(f'las cantidad de cartas en el mazo son: {self.elementos_mesa["cantidad_cartas_mazo"]}')
            self.mostrar_mazo(mesa, x_relativo, y_relativo, scala, accion)

    #cambio lismar
    def actualizar_elementos_jugadores(self):
        # Usamos la lista completa que sí incluye al jugador local
        for jugador in self.lista_jugadores_objetos:
            
            # 1. Validar que el panel visual exista
            if not hasattr(jugador, 'usuario') or not jugador.usuario:
                continue
                
            panel = jugador.usuario

            # 2. Buscar cuántas cartas tiene en tiempo real del diccionario del servidor
            cartas = 0
            for j_data in self.elementos_mesa.get("cantidad_manos_jugadores", []):
                if str(j_data["id"]) == str(jugador.nro_jugador):
                    cartas = j_data["cantidad_mano"]
                    break
                    
            # Mantener la misma lógica de visualización que limita las cartas físicas en pantalla
            es_local = (self.elementos_mesa["id_jugador"] == jugador.nro_jugador)
            cantidad_visual = cartas
            if cantidad_visual > 15 and not es_local:
                cantidad_visual = 14

            # 3. Inyectar los datos numéricos al panel visual
            panel.cartas = cartas
            panel.puntos = getattr(jugador, 'puntos', 0)
            
            # ─── NUEVO: AJUSTE DE CENTRADO DINÁMICO EN EL EJE DE LAS CARTAS ───
            if cantidad_visual > 0:
                dx, dy = self.calcular_desplazamiento_mano(jugador)
                
                if getattr(jugador, 'fila_cartas', 'horizontal') == 'horizontal':
                    # Si las cartas crecen horizontales (arriba/abajo), movemos panel.x a la mitad exacta de la fila
                    desfase_centro = ((cantidad_visual - 1) * dx) / 2
                    panel.x = panel.base_x + desfase_centro
                    panel.y = panel.base_y  # Mantiene su altura de diseño intacta
                else:
                    # Si crecen verticales (izquierda/derecha), movemos panel.y a la mitad de la fila
                    desfase_centro = ((cantidad_visual - 1) * dy) / 2
                    panel.y = panel.base_y + desfase_centro
                    panel.x = panel.base_x  # Mantiene su separación lateral de diseño intacta
            else:
                # Si se queda con 0 cartas por algún motivo, vuelve a su posición original estática
                panel.x = panel.base_x
                panel.y = panel.base_y
            # ──────────────────────────────────────────────────────────────────
            
            # 4. Actualizar colores del borde si es su turno
            turno_actual = self.elementos_mesa.get("jugador_mano")
            id_turno = str(turno_actual[0]) if turno_actual else "Nadie"

            if str(jugador.nro_jugador) == id_turno:
                panel.color_borde_actual = constantes.NARANJA
            else:
                panel.color_borde_actual = panel.color_dorado
    #cambio lismar      
    def actualizar_indicador_turno(self):
        self.determinar_turno()
        turno_actual = self.elementos_mesa.get("jugador_mano")
        nombre_jugador_turno = turno_actual[1] if turno_actual and len(turno_actual) > 1 else "Nadie"

        color_blanco = (255, 255, 255)

        if self.tu_turno:
            texto = f"¡ES TU TURNO! - {nombre_jugador_turno}"
        else:
            texto = f"Turno de: {nombre_jugador_turno}"

        indicador = self.referencia_elementos["indicador_turno"]

        indicador.texto = texto
        indicador.color_texto = color_blanco
        indicador.fuente = indicador.cargar_fuente(constantes.FUENTE_ESTANDAR)
        indicador.prepar_texto()

        indicador.color = None
        indicador.color_actual = None
        indicador.color_borde = None
        indicador.color_borde_actual = None
        indicador.grosor_borde = 0

        self.referencia_elementos["indicador_turno"] = indicador

    def actualizar_mano_visual(self, mesa, accion="reorganizar"):
        """
        Actualiza la mano visual de forma optimizada
        accion: "agregar_una" | "reorganizar_todo"
        """
        
        if not self.mano:
            # Limpiar si no hay cartas
            for elemento in self.referencia_elementos["elementos_mis_cartas"]:
                if elemento in mesa.botones:
                    mesa.botones.remove(elemento)
            self.referencia_elementos["elementos_mis_cartas"].clear()
            print("✅ Mano vacía - limpiada")
            return
        
        if accion == "agregar_una":
            # SOLO agregar la última carta (cuando tomas del descarte)
            self._agregar_ultima_carta(mesa)
            
        elif accion == "reorganizar_todo":
            # Reorganizar toda la mano (cuando descartas)
            self._reorganizar_toda_mano(mesa)

    def _agregar_ultima_carta(self, mesa):
        """Agrega solo la última carta de forma eficiente"""
        jugador_local = self.obtener_jugador_local()
        if not jugador_local:
            return
        
        dx, dy = self.calcular_desplazamiento_mano(jugador_local)
        
        # Calcular posición basada en la última carta existente
        for carta in self.referencia_elementos["elementos_mis_cartas"]:
            print(f"{carta.valor} tiene posicion en x: {carta.x} y: {carta.y}, prioridad: {carta.prioridad}")
        if self.referencia_elementos["elementos_mis_cartas"]:
            print(f"Agregando carta basada en la última existente {self.referencia_elementos['elementos_mis_cartas'][-1].valor}")
            ultima_carta = self.referencia_elementos["elementos_mis_cartas"][-1]
            x = ultima_carta.x + dx
            y = ultima_carta.y + dy
        else:
            # Primera carta
            x, y, dx, dy = self.determinar_ubicacion_mano(jugador_local, dx, dy)
        
        # Obtener grupo
        grupo_mano = self.obtener_grupo_cartas()
        
        # Crear y agregar solo la nueva carta
        nueva_carta = self.mano[-1]
        cart_imagen = nueva_carta.imagen_asociada(False)
        self.determinar_turno()
        
        carta_agregar = nueva_carta.Elemento_carta(
            grupo_mano, x, y, constantes.ESCALA_CARTAS, cart_imagen, deshabilitado=not self.tu_turno,mesa=self
        )
        carta_agregar.invalidar_ranuras_grupo()
        
        self.referencia_elementos["elementos_mis_cartas"].append(carta_agregar)
        mesa.botones.append(carta_agregar)
        
        print(f"✅ Carta agregada. Total: {len(self.mano)} y ademas la carta es: {grupo_mano[-1].valor}")

    def _reorganizar_toda_mano(self, mesa):
        """Reorganiza toda la mano (solo cuando es necesario)"""
        # Limpiar solo los elementos visuales
        self.reordenar_mano_visual_logica()
        
        # Guardar grupo provisional y prioridades ANTES de limpiar (de forma segura)
        grupo_provisional = []
        prioridades_guardadas = {}
        if self.referencia_elementos["elementos_mis_cartas"]:
            # Obtener el grupo de la primera carta si existe
            primera_carta = self.referencia_elementos["elementos_mis_cartas"][0]
            if hasattr(primera_carta, 'grupo') and primera_carta.grupo:
                grupo_provisional = list(primera_carta.grupo)
                # Guardar prioridades de las cartas existentes
                for carta_antigua in grupo_provisional:
                    if hasattr(carta_antigua, 'valor') and hasattr(carta_antigua, 'prioridad'):
                        prioridades_guardadas[carta_antigua.valor] = carta_antigua.prioridad
        
        # Invalidar ranuras del grupo antes de limpiar
        for elemento in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento, 'invalidar_ranuras_grupo'):
                elemento.invalidar_ranuras_grupo()
            if elemento in mesa.botones:
                mesa.botones.remove(elemento)
        
        # Limpiar referencias
        self.referencia_elementos["elementos_mis_cartas"].clear()
        
        print("Depuracio cual es mi mano para ese momento: ")
        for carta in self.mano:
            print(f"Carta en mano: {carta.__str__()}")
        
        # Recrear todas las cartas
        jugador_local = self.obtener_jugador_local()
        if not jugador_local:
            return
        
        dx, dy = self.calcular_desplazamiento_mano(jugador_local)
        x, y, dx, dy = self.determinar_ubicacion_mano(jugador_local, dx, dy)
        if len(self.mano) > 11:
            x = x*0.90
        grupo_mano = []

        # Crear nuevas cartas
        for carta in self.mano:
            cart_imagen = carta.imagen_asociada(False)
            carta_visual = carta.Elemento_carta(
                grupo_mano, x, y, constantes.ESCALA_CARTAS, cart_imagen,
                deshabilitado=not self.tu_turno, mesa=self
            )
            self.referencia_elementos["elementos_mis_cartas"].append(carta_visual)
            mesa.botones.append(carta_visual)
            x += dx
            y += dy
            
        # Restaurar prioridades si existen
        for carta_visual in self.referencia_elementos["elementos_mis_cartas"]:
            if carta_visual.valor in prioridades_guardadas:
                carta_visual.prioridad = prioridades_guardadas[carta_visual.valor]
            else:
                # Asignar prioridad basada en el índice si no existe
                indice = self.referencia_elementos["elementos_mis_cartas"].index(carta_visual)
                carta_visual.prioridad = indice

        for carta in self.referencia_elementos["elementos_mis_cartas"]:
            print(f"Carta en referencia elementos: {carta.valor} con prioridad {carta.prioridad}")
        print(f"✅ Mano reorganizada. Cartas: {len(self.mano)}")

    def actualizar_carta_descarte(self, mesa):
        """Reemplaza la carta de descarte manteniendo la MISMA posición"""
        if self.carta_descarte is None:
            try:
                mesa.imagenes.remove(self.referencia_elementos["elemento_carta_descarte"])
            except ValueError:
                pass
            return
            
        try:
            # 1. Obtener la posición ABSOLUTA actual de la carta existente
            posicion_absoluta_actual = None
            
            
            elemento_anterior = self.referencia_elementos["elemento_carta_descarte"]
            _,posicion_absoluta_actual = elemento_anterior
            posicion_relativa = (
                posicion_absoluta_actual[0] - mesa.x,  # ← RESTAR posición del menú
                posicion_absoluta_actual[1] - mesa.y   # ← para obtener relativa
            )
            # 2. Agregar nueva carta en la MISMA posición relativa
            surface_carta = self.carta_descarte.imagen_asociada(False)
            mesa.agregar_imagen(surface_carta, posicion_relativa, constantes.ESCALA_CARTAS)
            
            # 3. Guardar referencia
            self.referencia_elementos["elemento_carta_descarte"] = mesa.imagenes[-1]
            
            print(f"✅ Descarte actualizado en misma posición: {self.carta_descarte.figura}")
        except Exception as e:
            x_relativo, y_relativo, _, _ = self._calcular_posicion_mazo()
            scala = constantes.ESCALA_CARTAS
            self.mostrar_carta_descarte(mesa, x_relativo + 180, y_relativo, scala)
    def borrar_mazo_quema(self):
        print(self.elementos_mesa["cantidad_cartas_quema"])
        self.mazo_quema.cantidad_cartas = self.elementos_mesa["cantidad_cartas_quema"]
        datos = self.mazo_quema.retornar_datos() #si activan esto solo habria que volver a llamar a la funcion de actualizar_mazo_quema
        self.mesa.botones.remove(self.mazo_quema.elemento_mazo)
        self.mazo_quema = Mazo(datos["cantidad_cartas"],datos["x"],datos["y"],datos["scala"],accion=None,un_juego=datos["un_juego"])
        self.mesa.botones.append(self.mazo_quema.elemento_mazo)
        self.referencia_elementos["elemento_mazo_quema"] = self.mesa.botones[-1]
        
    def actualizar_mazo_quema(self):
        
        print(self.elementos_mesa["cantidad_cartas_quema"])
        self.carta_descarte = None
        self.mazo_quema.cantidad_cartas = self.elementos_mesa["cantidad_cartas_quema"]
        datos = self.mazo_quema.retornar_datos() #si activan esto solo habria que volver a llamar a la funcion de actualizar_mazo_quema
        self.mesa.botones.remove(self.mazo_quema.elemento_mazo)
        self.mazo_quema = Mazo(datos["cantidad_cartas"],datos["x"],datos["y"],datos["scala"],accion=None,un_juego=datos["un_juego"])
        self.mesa.botones.append(self.mazo_quema.elemento_mazo)
        self.referencia_elementos["elemento_mazo_quema"] = self.mesa.botones[-1]
    
    def actualizar_carta_quema(self,mesa):
        """Reemplaza la carta de quema manteniendo la MISMA posición"""
        mazo_temp = Mazo(0, 0, 0, 0.05, None, self.un_juego)
        ancho_mazo = mazo_temp.elemento_mazo.ancho
        alto_mazo = mazo_temp.elemento_mazo.alto
        self.mostrar_carta_quema(mesa,(constantes.ANCHO_MENU_MESA * 0.40) - ancho_mazo+310,(constantes.ALTO_MENU_MESA * 0.55) - alto_mazo,constantes.ESCALA_CARTAS)  # Actualiza self.carta_quema
        if self.carta_quema is None:
            if self.referencia_elementos["elemento_carta_quema"] in mesa.imagenes:
                mesa.imagenes.remove(self.referencia_elementos["elemento_carta_quema"])
                self.referencia_elementos["elemento_carta_quema"] = None
            return
    def actualizar_contadores_manos_jugadores(self):
        """Limpia los contadores antiguos, ahora la info está unificada en el panel principal"""
        for contador in self.referencia_elementos.get("contadores_mano_por_jugador", []):
            if hasattr(self.un_juego, 'mesa') and self.un_juego.mesa:
                if contador in self.un_juego.mesa.overlays:
                    self.un_juego.mesa.overlays.remove(contador)
                elif contador in self.un_juego.mesa.botones:
                    self.un_juego.mesa.botones.remove(contador)
        self.referencia_elementos["contadores_mano_por_jugador"].clear()

    def actualizar_manos_jugadores(self,mesa):
        #para este punto el elemento "cantidad_manos_jugadores" deberia haber sido modificado en cada pantalla
        for reverso in self.referencia_elementos["reversos_por_jugador"]:
            self.un_juego.mesa.imagenes.remove(reverso)
        self.referencia_elementos["reversos_por_jugador"].clear()

        # Actualizar contadores UNA VEZ con los valores REALES (antes del loop)
        self.actualizar_contadores_manos_jugadores()

        for jugador_list in self.elementos_mesa["cantidad_manos_jugadores"]:
            nro = jugador_list["id"]
            jugador = next(j for j in self.lista_jugadores_objetos if j.nro_jugador == nro)

            es_local = (self.elementos_mesa["id_jugador"] == jugador.nro_jugador)
            escala_jugadores = constantes.ESCALA_DEMAS_CARTAS
            
            # Limitar SOLO las cartas visibles, NO modificar el valor original
            cantidad_cartas_a_dibujar = jugador_list["cantidad_mano"]
            if cantidad_cartas_a_dibujar > 15 and not es_local:
                cantidad_cartas_a_dibujar = 14  # Solo limitar la visualización

            dx, dy = self.calcular_desplazamiento_mano(jugador)
            x, y, dx, dy = self.determinar_ubicacion_mano(jugador, dx, dy)

            escala = constantes.ESCALA_CARTAS if es_local else escala_jugadores

            if not es_local:
                # Usar cantidad_cartas_a_dibujar en lugar de jugador_list["cantidad_mano"]
                self.agregar_manos_jugadores(mesa, cantidad_cartas_a_dibujar, jugador, escala, dx, dy, x, y)
        # --- LÍNEA NUEVA QUE DEBES AGREGAR AQUÍ ---
        self.actualizar_elementos_jugadores() #cambio lismar añadida
        
             
    def actualizar_jugadas(self,mesa):
        try:
            for x in self.referencia_elementos["elementos_jugadas_jugadores"]:
                self.mesa.imagenes.remove(x)
            self.referencia_elementos["elementos_jugadas_jugadores"].clear()
        except:
            pass
        try:
            for x in self.referencia_elementos["elementos_mi_jugada"]:
                self.mesa.imagenes.remove(x)
            self.referencia_elementos["elementos_mi_jugada"].clear()
        except:
            pass
        self.mostrar_jugadas(mesa)
    
    def actualizar_estado_mano(self,accion="robar,esperar_robar"):
        if accion == "esperar_robar":
            mis_cartas = []
            for carta in self.referencia_elementos["elementos_mis_cartas"]:

                carta.deshabilitado = True
                carta.seleccionado = False
                mis_cartas.append(carta)
            self.referencia_elementos["elementos_mis_cartas"] = mis_cartas
            self.limpiar_botones(self.mesa)
        elif accion == "robar":
            # Verificar que los botones existan antes de activarlos
            if "comprar" in self.botones_accion:
                self.botones_accion["comprar"].deshabilitado = False
                self.botones_accion["comprar"].habilitar()
            if "no_comprar" in self.botones_accion:
                self.botones_accion["no_comprar"].deshabilitado = False
                self.botones_accion["no_comprar"].habilitar()
            print("logica para robar")
        if accion == "desactivar_boton":
            # Verificar que los botones existan antes de desactivarlos
            if "comprar" in self.botones_accion:
                self.botones_accion["comprar"].deshabilitado = True
                self.botones_accion["comprar"].deshabilitar()
            if "no_comprar" in self.botones_accion:
                self.botones_accion["no_comprar"].deshabilitado = True
                self.botones_accion["no_comprar"].deshabilitar()
        if accion == "activar_mano":
            mis_cartas = []
            for carta in self.referencia_elementos["elementos_mis_cartas"]:
                carta.deshabilitado = False
                carta.seleccionado = False
                mis_cartas.append(carta)
        if accion == "desactivar_mano":
            mis_cartas = []
            for carta in self.referencia_elementos["elementos_mis_cartas"]:
                carta.deshabilitado = True
                carta.seleccionado = False
                mis_cartas.append(carta)
