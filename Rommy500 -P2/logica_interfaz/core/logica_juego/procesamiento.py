"""Módulo interno para procesamiento de acciones del jugador"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)


class ProcesamientoMixin:
    """Mixin con métodos para procesamiento de acciones del jugador"""
    
    def finalizar_turno(self, mesa):
        """Finaliza el turno descartando la carta seleccionada"""
        print("✅ Turno finalizado - Esperando siguiente turno...")
        #EJECUTAR ACCIONES VERDADERAS DE REDES
        carta_descartada = None
        
        # Buscar carta seleccionada usando valor (no índice)
        for elemento_carta in self.referencia_elementos["elementos_mis_cartas"]:
            if hasattr(elemento_carta, 'seleccionado') and elemento_carta.seleccionado:
                carta_descartada = self.obtener_carta_logica_por_valor(elemento_carta.valor)
                if carta_descartada:
                    self.mano.remove(carta_descartada) #<- esto no va
                
                # Actualizar descarte
                self.carta_descarte = carta_descartada #<- esto no va
                
                self.actualizar_carta_descarte(mesa) #<- esto no va
                break
        self.actualizar_mano_visual(mesa,"reorganizar_todo")  #<- esto no va
        # Limpiar y cambiar estado
        self.limpiar_botones(mesa)
        # self.cargar_elemento_botones(mesa)
    
    def reordenar_mano_visual_logica(self):
        visual = self.referencia_elementos["elementos_mis_cartas"]
        nueva_mano = []

        for carta_visual in visual:
            for carta_dato in self.mano:
                if carta_dato.__str__() == carta_visual.valor:
                    nueva_mano.append(carta_dato)
                    break
        print("Mano original:", [carta.__str__() for carta in self.mano])
        print("Mano reordenada:", [carta.__str__() for carta in nueva_mano])
        print("Mano visual:", [carta.valor for carta in visual])

        if len(nueva_mano) != len(self.mano):
            print("⚠ Reordenamiento incompleto: no todas las cartas fueron encontradas")
            print("Mano original:", [carta.__str__() for carta in self.mano])
            print("Mano reordenada:", [carta.__str__() for carta in nueva_mano])
            # print("lo qeu debio ser la mano reordenada:",[])
        else:
            self.mano = nueva_mano
    
    def procesar_tomar_descarte(self, mesa):
        """Procesa cuando el jugador toma carta del descarte"""
        print("✅ Tomando carta del descarte...")
        # 1. Agregar carta a los datos
        # self.reordenar_mano_visual_logica()
        self.mano.append(self.carta_descarte) #->esto no es asi, reemplazar esta linea por el siguiente esquema:
        self.elementos_mesa["dato_carta_descarte"] = None
        #Para este punto la mesa_elementos(mano local, y la carta de descarte) ya deberian estar actualizadas en la mano del jugador local,

        # 2. LIMPIAR la carta de descarte (tanto datos como visual)
        self.carta_descarte = None  # <- esto no va, no es necesario ya el servidor la marco como None se supone
        
        # 3. Actualizar visualmente
        self.actualizar_mano_visual(mesa,"agregar_una") 
        self.actualizar_carta_descarte(mesa)
        
        
        if not self.elementos_mesa["jugada"] or self.elementos_mesa["jugada"] == []:
            self.crear_botones_jugar_descartar(self.mesa)
        else:
            self.crear_botones_despues_bajarse(mesa)

    def procesar_no_tomar_descarte(self):
        self.determinar_turno_robar()
        self.determinar_turno()
        if self.tu_turno and not self.turno_robar:
            self.actualizar_estado_mano(accion="esperar_robar")
        elif not self.tu_turno and self.turno_robar:
            self.actualizar_estado_mano(accion="robar")
        else:
            return

    def procesar_comprar(self, mesa,carta_del_mazo):
        print("🔄 Iniciando procesar_comprar")
        
        try:
            self.mano.append(self.carta_descarte) #->esto no es asi, reemplazar esta linea por el siguiente esquema:
            print(self.carta_descarte)
            print(carta_del_mazo)
            print("Aaaaaaaaaaaaaaa")
            #Para este punto la mesa_elementos(mano local, y la carta de descarte) ya deberian estar actualizadas en la mano del jugador local,

            # 2. LIMPIAR la carta de descarte (tanto datos como visual)
            self.carta_descarte = None  # <- esto no va, no es necesario ya el servidor la marco como None se supone
            carta = Carta(numero=carta_del_mazo["numero"], figura=carta_del_mazo["figura"])
            carta.un_juego = self.un_juego
            carta.parte_superior = self._cartas_imagenes.get(f'{carta.figura} ({carta.numero})')
            carta.parte_trasera = self._cartas_imagenes.get('Reverso')
            self.mano.append(carta)
            # 3. Actualizar visualmente
            self.actualizar_mano_visual(mesa,"reorganizar_todo") 
            self.actualizar_carta_descarte(mesa)
                
        except Exception as e:
            print(f"ERROR en procesar_comprar: {e}")
            import traceback
            traceback.print_exc()

    def procesar_tomar_mazo(self,mesa,carta_del_mazo):
        print("Carta del mazo tomada")
        try:
            carta = Carta(numero=carta_del_mazo["numero"], figura=carta_del_mazo["figura"])
            carta.un_juego = self.un_juego
            carta.parte_superior = self._cartas_imagenes.get(f'{carta.figura} ({carta.numero})')
            carta.parte_trasera = self._cartas_imagenes.get('Reverso')
            self.mano.append(carta)
            # 3. Actualizar visualmente
            self.actualizar_mano_visual(mesa,"reorganizar_todo") 
            if not self.elementos_mesa["jugada"]:
                self.crear_botones_jugar_descartar(self.mesa)
            else:
                self.crear_botones_despues_bajarse(mesa)
        except Exception as e:
                    print(f"ERROR en procesar_comprar: {e}")
                    import traceback
                    traceback.print_exc()

