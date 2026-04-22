"""Módulo interno para carga de elementos visuales"""


class CargaVisualesMixin:
    """Mixin con métodos para carga de elementos visuales"""
    
    def cargar_elementos_jugadas(self):
        for lista_cartas in self.jugadas_jugadores.values():
            for cart in lista_cartas:
                cart.un_juego = self.un_juego
                cart.parte_superior = self._cartas_imagenes.get(f'{cart.figura} ({cart.numero})')
                cart.parte_trasera = self._cartas_imagenes.get('Reverso')
    
    def cargar_elemento_mi_jugada(self):
        for cart in self.jugada:
            cart.un_juego = self.un_juego
            cart.parte_superior = self._cartas_imagenes.get(f'{cart.figura} ({cart.numero})')
            cart.parte_trasera = self._cartas_imagenes.get('Reverso')

    def cargar_elemento_mi_mano(self):
        """Carga los elementos visuales de la mano local"""
        for cart in self.mano:
            cart.un_juego = self.un_juego
            cart.parte_superior = self._cartas_imagenes.get(f'{cart.figura} ({cart.numero})')
            cart.parte_trasera = self._cartas_imagenes.get('Reverso')

    def cargar_elemento_carta_descarte(self):
        """Carga los elementos visuales de la carta de descarte"""
        if self.carta_descarte is None:
            return
        self.carta_descarte.un_juego = self.un_juego
        self.carta_descarte.parte_superior = self._cartas_imagenes.get(f'{self.carta_descarte.figura} ({self.carta_descarte.numero})')
        self.carta_descarte.parte_trasera = self._cartas_imagenes.get('Reverso')
    
    def cargar_elemento_carta_quema(self):
        """Carga los elementos visuales de la carta de quema"""
        if self.carta_quema is None:
            return
        self.carta_quema.un_juego = self.un_juego
        self.carta_quema.parte_superior = self._cartas_imagenes.get(f'{self.carta_quema.figura} ({self.carta_quema.numero})')
        self.carta_quema.parte_trasera = self._cartas_imagenes.get('Reverso')

    def cargar_elementos_jugadores(self, mesa, posiciones, ancho_jugador, alto_jugador):
        """Carga los elementos visuales de todos los jugadores"""
        for jugador in self.lista_jugadores_objetos: 
            indice_jugador = jugador.nro_jugador - 1
            direccion, alineacion = posiciones[indice_jugador]
            
            # Usar método reutilizable
            jugador = self.configurar_posicion_jugador(jugador, direccion, alineacion, ancho_jugador, alto_jugador)
            jugador.un_juego = self.un_juego
            
            turno = self.elementos_mesa["jugador_mano"][0] == jugador.nro_jugador
            jugador.usuario = jugador.elemento_usuario(True,turno)
            
            if jugador.nro_jugador != self.elementos_mesa["id_jugador"]:
                self.referencia_elementos["elemento_jugadores"].append(jugador.usuario)
                self.jugadores.append(jugador)
                mesa.botones.append(jugador.usuario)

