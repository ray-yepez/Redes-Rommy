from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

Jugador = importar_desde_carpeta(
    "jugador.py", #Archivo
    "Jugador" #Clase
    )

Elemento_texto = importar_desde_carpeta(
    "elementos_de_interfaz_de_usuario.py", #Archivo
    "Elemento_texto", #Clase
    "recursos_graficos" #Nombre de la carpeta
    )

constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos"
    )

class Jugador_interfaz(Jugador):
    def __init__(self,*args,un_juego=None,x=0,y=0,ancho=0,alto=0,**kwargs):
        self.un_juego = un_juego
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        super().__init__(*args,**kwargs)

    def elemento_usuario(self,mostrar_nombre=True, es_turno=False):
        if mostrar_nombre:
            texto = f"Jugador {self.nro_jugador}: {self.nombre_jugador}"
        else:
            texto = f"Jugador {self.nro_jugador}" 
    # DEFINIR COLORES SEGÚN TURNO
        if es_turno:
            color_borde = constantes.NARANJA  # Naranja para turno
            color_texto = constantes.COLOR_TEXTO_PRINCIPAL
        else:
            color_borde = constantes.ELEMENTO_BORDE_PRINCIPAL  # Azul normal
            color_texto = constantes.COLOR_TEXTO_PRINCIPAL
        redondeo = int(constantes.REDONDEO_NORMAL*0.50)
        usuario = Elemento_texto(
            self.un_juego,
            texto,
            self.ancho,
            self.alto,
            self.x,
            self.y,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_ESTANDAR,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=redondeo,
            color_texto=color_texto,
            color_borde=color_borde,
            grosor_borde=constantes.BORDE_INTERMEDIO,
        )
        return usuario
    