"""Módulo interno para creación y configuración de botones"""

from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Boton


class BotonTransparente(Boton):
    """Botón completamente transparente (invisible) pero funcional para clics"""
    
    def __init__(self, *args, **kwargs):
        # Establecer colores transparentes por defecto
        kwargs.setdefault('color', (100, 100, 0, 10))  # Fondo transparente
        kwargs.setdefault('color_borde', (0, 0, 0, 0))  # Borde transparente
        kwargs.setdefault('color_texto', (0, 0, 0, 0))  # Texto transparente
        kwargs.setdefault('grosor_borde', 0)  # Sin grosor de borde
        kwargs.setdefault('color_hover', (0, 0, 0, 0))  # Hover transparente
        kwargs.setdefault('color_borde_hover', (0, 0, 0, 0))  # Borde hover transparente
        kwargs.setdefault('color_borde_clicado', (0, 0, 0, 0))  # Borde clicado transparente
        
        super().__init__(*args, **kwargs)
    
    def dibujar(self):
        """No dibuja nada, hace el botón completamente invisible"""
        # Solo mantener la funcionalidad del botón sin dibujar nada visual
        # El rect sigue existiendo para detectar clics
        pass


class BotonesMixin:
    """Mixin con métodos para creación y configuración de botones"""
    
    def cargar_elemento_botones(self, mesa):
        """Crea los botones de acción según el estado del turno"""
        self.determinar_turno()
        self.botones_accion.clear()

        if self.boton_menu_opciones is None :
            self.boton_menu_opciones = self.crear_boton_menu()
            mesa.botones.append(self.boton_menu_opciones)
        
        if not self.tu_turno:
            self.crear_botones_no_turno(mesa)
        else:
            if "bajarse" in self.botones_accion and "tomar" in self.botones_accion:
                return
            else:
                self.crear_botones_inicio_turno(mesa)

    def limpiar_botones(self, mesa):
        """Elimina los botones actuales de la mesa"""
        for boton in list(self.botones_accion.values()):
            if boton in mesa.botones:
                mesa.botones.remove(boton)
        self.botones_accion.clear()

    def actualizar_botones(self):
        """Actualiza los botones según el turno del jugador"""
        self.determinar_turno()
        
        if not hasattr(self.un_juego, 'menus_activos') or not self.un_juego.menus_activos:
            return
            
        mesa = self.un_juego.menus_activos[-1]
        
        if not hasattr(mesa, 'botones'):
            mesa.botones = []
        
        self.limpiar_botones(mesa)
        
        if not self.tu_turno:
            self.crear_botones_no_turno(mesa)
        else:
            self.crear_botones_inicio_turno(mesa)

    def crear_botones_inicio_turno(self, mesa):
        """Botones iniciales cuando comienza tu turno"""
        self.limpiar_botones(mesa)
        ancho_boton1 = constantes.ELEMENTO_PEQUENO_ANCHO * 0.28
        alto_boton1 = constantes.ELEMENTO_PEQUENO_ALTO * 1.2
        ancho_boton2 = constantes.ELEMENTO_PEQUENO_ANCHO * 0.24
        alto_boton2 = constantes.ELEMENTO_PEQUENO_ALTO * 1.15
        espacio =85.5
        
        total_ancho = (ancho_boton1 * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) *0.46
        y_base = constantes.ALTO_MENU_MESA * 0.468

        opciones_tomar = [
            ("NO TOMAR", lambda: self.accion_no_tomar_descarte()),
            ("TOMAR", lambda: self.accion_tomar_carta_descarte())
        ]
        
        for i, (texto, accion) in enumerate(opciones_tomar):
            # Usar botones transparentes para NO TOMAR y TOMAR
            if i==0:
                ancho_boton = ancho_boton1
                alto_boton = alto_boton1
            else:
                ancho_boton = ancho_boton2
                alto_boton = alto_boton2
            boton = self.crear_boton_transparente(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_no_turno(self, mesa):
        """Botones para cuando NO es tu turno (compra/rechazo)"""
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        self.determinar_turno_robar()

        botones_no_turno = [
            ("COMPRAR", lambda: self.accion_comprar()),
            ("NO COMPRAR", lambda: self.accion_rechazar_carta())
        ]
        
        for i, (texto, accion) in enumerate(botones_no_turno):
            boton = self.crear_boton_generico(
                texto, 
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, not self.turno_robar
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton


    def crear_botones_despues_bajarse(self,mesa):
        self.restaurar_comportamiento_mi_mano()
        self.limpiar_botones(mesa)
        
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        opciones_tomar = [
            ("EXTENDER", lambda: self.crear_botones_extender_jug(self.mesa,opc=True)),
            ("REEMPLAZAR", lambda: self.accion_reemplazar()),
            ("DESCARTAR", lambda: self.accion_descartar())
        ]
        
        for i, (texto, accion) in enumerate(opciones_tomar):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_jugar_descartar(self, mesa):
        """Muestra el botón para descartar y el de bajarse"""
        self.limpiar_botones(mesa)
        self.restaurar_comportamiento_mi_mano()
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        botones_inicio = [
            ("BAJARSE", lambda: self.crear_botones_seleccionar_jugada(mesa)),
            ("DESCARTAR", lambda: self.accion_descartar())
        ]
        
        for i, (texto, accion) in enumerate(botones_inicio):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton
        self.accion_cancelar_jugada()

    def crear_botones_quema_mono(self, mesa):
        """Muestra el botón para descartar"""
        self.limpiar_botones(mesa)
        
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.65
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        
        x_base = (constantes.ANCHO_MENU_MESA - ancho_boton) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        boton_quemar_mono = self.crear_boton_generico(
            "SELECCIONE OTRO DESCARTE",
            x_base, y_base,
            ancho_boton, alto_boton,
            lambda: self.accion_quemar_mono(), False
        )
        mesa.botones.append(boton_quemar_mono)
        self.botones_accion["quemar_mono"] = boton_quemar_mono

    def crear_botones_despues_de_bajarse(self, mesa):
        """Muestra botones después de bajarse"""
        self.limpiar_botones(mesa)
        self.restaurar_comportamiento_mi_mano()
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.5
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho)/4 
        y_base = constantes.ALTO_MENU_MESA * 0.8

        botones_inicio = [
            ("EXTENDER", lambda: self.crear_botones_extender_jug(self.mesa)),
            ("REEMPLAZAR", lambda: self.accion_reemplazar()),
            ("DESCARTAR", lambda: self.accion_descartar()),
            ("CANCELAR", lambda: self.accion_cancelar())
        ]
        
        for i, (texto, accion) in enumerate(botones_inicio):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_seleccionar_jugada(self, mesa):
        """Permite seleccionar jugada"""
        self.limpiar_botones(mesa)
        self.modificar_comportamiento_mi_mano()
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        botones_inicio = [
            ("CONFIRMAR", lambda: self.accion_bajarse()),
            ("SELECCIONAR", lambda: self.accion_confirmar_jugada()),
            ("CANCELAR", lambda: self.accion_cancelar())
        ]
        
        for i, (texto, accion) in enumerate(botones_inicio):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_elegir_posicion_seguidilla(self, mesa):
        """Muestra el botón para elegir posicion de la seguidilla"""
        self.limpiar_botones(mesa)
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        botones_inicio = [
            ("INICIO", lambda: self.accion_posicion_seguidillas(pos="inicio")),
            ("PUNTA", lambda: self.accion_posicion_seguidillas(pos="punta"))
        ]
        
        for i, (texto, accion) in enumerate(botones_inicio):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_elegir_donde_extender(self, mesa, lug=None,ronda=None,lug2 = None):
        """Muestra el botón para elegir donde extender la jugada"""
        self.limpiar_botones(mesa)
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        if ronda == None:
            botones_inicio = [
                ("TRIO", lambda: self.accion_elegir_donde_extender(pos="trio")),
            ]
            if lug == "ambos":
                botones_inicio.append(("SEGUIDILLA", lambda: self.crear_botones_elegir_pos_seguidilla()))
            else:
                botones_inicio.append(("SEGUIDILLA", lambda: self.accion_elegir_donde_extender(pos="seguidilla", lug=lug)))
            
            for i, (texto, accion) in enumerate(botones_inicio):
                boton = self.crear_boton_generico(
                    texto,
                    x_base + (i * (ancho_boton + espacio)), y_base,
                    ancho_boton, alto_boton, accion, False
                )
                mesa.botones.append(boton)
                self.botones_accion[texto.lower().replace(" ", "_")] = boton
        if ronda == 2:
            botones_inicio = []
            if lug == "ambos":
                botones_inicio.append(("SEGUIDILLA1", lambda: self.crear_botones_elegir_pos_seguidilla(pos1="seguidilla1",ronda=2)))
            else:
                botones_inicio.append(("SEGUIDILLA1", lambda: self.accion_elegir_donde_extender(pos="seguidilla1", lug=lug)))
            
            if lug2 == "ambos":
                botones_inicio.append(("SEGUIDILLA2", lambda: self.crear_botones_elegir_pos_seguidilla(pos1="seguidilla2",ronda=2)))
            else:
                botones_inicio.append(("SEGUIDILLA2", lambda: self.accion_elegir_donde_extender(pos="seguidilla2", lug=lug2)))
            for i, (texto, accion) in enumerate(botones_inicio):
                boton = self.crear_boton_generico(
                    texto,
                    x_base + (i * (ancho_boton + espacio)), y_base,
                    ancho_boton, alto_boton, accion, False
                )
                mesa.botones.append(boton)
                self.botones_accion[texto.lower().replace(" ", "_")] = boton
    def crear_botones_elegir_pos_seguidilla(self,ronda = None,pos1 = None):
        """Elige posición de seguidilla al extender"""
        mesa = self.mesa
        self.limpiar_botones(mesa)
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        
        total_ancho = (ancho_boton * 2) + espacio
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8
        if ronda == None:
            botones_inicio = [
                ("INICIO", lambda: self.accion_elegir_donde_extender(pos="seguidilla", lug="inicio")),
                ("PUNTA", lambda: self.accion_elegir_donde_extender(pos="seguidilla", lug="final"))
            ]
        elif ronda == 2:
            botones_inicio = [
                ("INICIO", lambda: self.accion_elegir_donde_extender(pos=pos1, lug="inicio")),
                ("PUNTA", lambda: self.accion_elegir_donde_extender(pos=pos1, lug="final"))
            ]
        for i, (texto, accion) in enumerate(botones_inicio):
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton

    def crear_botones_extender_jug(self, mesa,opc = None):
        """Muestra el botón para descartar y el de bajarse"""
        self.limpiar_botones(mesa)
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.5
        espacio = 20
        jugadores = self.lista_jugadores_objetos or []
        # Solo incluir jugadores que ya se bajaron (incluyendo al jugador local)
        jugadores_validos = [j for j in jugadores if self.jugador_esta_bajado(j.nro_jugador)]
        m = len(jugadores_validos)

        total_ancho = (ancho_boton * m) + (espacio * (m - 1))
        x_base = (constantes.ANCHO_MENU_MESA - total_ancho) / 2
        y_base = constantes.ALTO_MENU_MESA * 0.8

        for i, jugador in enumerate(jugadores_validos):
            texto = f"J{jugador.nro_jugador}: {jugador.nombre_jugador}"
            accion = (lambda id_j=jugador.nro_jugador: self._accion_extender_para(id_j))
            boton = self.crear_boton_generico(
                texto,
                x_base + (i * (ancho_boton + espacio)), y_base,
                ancho_boton, alto_boton, accion, False
            )
            mesa.botones.append(boton)
            self.botones_accion[texto.lower().replace(" ", "_")] = boton
        x_cancel = x_base + (m * (ancho_boton + espacio))
        if opc:
            total_ancho = ancho_boton
            y_base = constantes.ALTO_MENU_MESA * 0.8
            boton = self.crear_boton_generico(
                "CANCELAR",
                x_cancel, y_base,
                ancho_boton, alto_boton, lambda: self.crear_botones_despues_bajarse(mesa), False
            )
            mesa.botones.append(boton)
            self.botones_accion["cancelar"] = boton
        else:
            
            boton_cancel = self.crear_boton_generico(
                "CANCELAR",
                x_cancel, y_base,
                ancho_boton, alto_boton, lambda: self.crear_botones_despues_de_bajarse(mesa), False
            )
            mesa.botones.append(boton_cancel)
            self.botones_accion["cancelar"] = boton_cancel

