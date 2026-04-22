"""Módulo interno para acciones de red (envío al servidor)"""


class AccionesRedMixin:
    """Mixin con métodos para acciones de red (envío al servidor)"""
    
    def accion_confirmar_jugada(self):
        accion = "validar_seleccion"
        cartas = []
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_logica = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_logica:
                    cartas.append(carta_logica)
                elemento_carta.deseleccionar()
                elemento_carta.deshabilitado = True
        print(f"longitud cartas del trio: {len(cartas)}")
        cartas_a_enviar = []
        datos_del_trio = {}
        for carta in cartas:
            datos_del_trio[carta.__str__()] = carta.to_dict()
            cartas_a_enviar.append(carta.to_dict())
        print(datos_del_trio)
        datos = {"datos_cartas":cartas_a_enviar}
        self.instacia_conexion.enviar_accion(accion, datos)

    def accion_tomar_carta_descarte(self):
        print("✅ Confirmado: Tomar carta del descarte")
        accion = "Tomar_Carta_Descarte"
        self.instacia_conexion.enviar_accion(accion, datos=None)

    def accion_rechazar_carta(self):
        accion = "No_tomar_descarte"
        self.instacia_conexion.enviar_accion(accion)

    def accion_tomar_mazo(self):
        print("Tomando carta del mazo")
        accion = "Tomar_carta_mazo"
        self.instacia_conexion.enviar_accion(accion)
        

    def accion_descartar(self):
        accion = "Descarte_Carta"
        carta_descartada = None
        # Buscar la carta seleccionada usando el valor (no el índice) para evitar
        # problemas cuando el usuario ha reorganizado las cartas visualmente
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_descartada = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_descartada:
                    break
        datos = {
            "carta_descartada": carta_descartada.to_dict() if carta_descartada else None
        }
        self.instacia_conexion.enviar_accion(accion, datos)

    def accion_no_tomar_descarte(self):
        accion = "No_tomar_descarte"
        self.instacia_conexion.enviar_accion(accion)
        print("hola")

    def accion_comprar(self):
        accion = "comprar"
        self.instacia_conexion.enviar_accion(accion)

    def accion_quemar_mono(self):
        accion = "mono_quemado"
        carta_descartada = None
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_descartada = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_descartada:
                    break
        datos = {
            "carta_descartada": carta_descartada.to_dict() if carta_descartada else None
        }
        self.instacia_conexion.enviar_accion(accion,datos)
    
    def accion_cancelar_jugada(self):
        accion = "Cancelar_jugada"
        self.instacia_conexion.enviar_accion(accion)

    def accion_reemplazar(self):
        accion = "reemplazar"
        carta_descartada = None
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_descartada = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_descartada:
                    break
        datos = {
            "carta_descartada": carta_descartada.to_dict() if carta_descartada else None
        }

        self.instacia_conexion.enviar_accion(accion,datos)
        print("www.botonreemplazar.com")

    def accion_cancelar(self):
        """Cancela la jugada actual"""
        accion = "cancelar_jugada"
        print("cancelando")
        self.instacia_conexion.enviar_accion(accion)

    def accion_bajarse(self):
        """Acción para bajarse"""
        accion = "bajarse"
        self.instacia_conexion.enviar_accion(accion)

    def accion_posicion_seguidillas(self, pos):
        """Envía posición elegida"""
        if pos == "inicio":
            datos = {"posicion_elegida": "inicio"}
        elif pos == "punta":
            datos = {"posicion_elegida": "punta"}
        accion = "elegir_posicion_seguidilla"
        self.instacia_conexion.enviar_accion(accion, datos)

    def accion_elegir_donde_extender(self, pos, lug=None,):
        """Envía dónde extender"""
        accion = "elecion_donde_extender"
        datos = {
            "donde_extender": pos,
            "posicion_seguidilla": lug
        }
        self.instacia_conexion.enviar_accion(accion, datos)

    def _accion_extender_para(self, id_jugador):
        """Recopila las cartas seleccionadas y llama a accion_extender_en con el id indicado."""
        cartas_del_trio = []
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_logica = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_logica:
                    cartas_del_trio.append(carta_logica)
                elemento_carta.deseleccionar()
                elemento_carta.deshabilitado = True
        print(f"longitud cartas del trio: {len(cartas_del_trio)}")
        cartas_a_enviar = []
        datos_del_trio = {}
        for carta in cartas_del_trio:
            datos_del_trio[carta.__str__()] = carta.to_dict()
            cartas_a_enviar.append(carta.to_dict())
        print(datos_del_trio)
        self.accion_extender_en(id_jugador, cartas_a_enviar)

    def accion_extender_en(self,id,cartas_expandir):
        accion = "extender_en"
        datos = {
            "id_jugador": id,
            "cartas_expandir" : cartas_expandir
        }
        self.instacia_conexion.enviar_accion(accion,datos)

