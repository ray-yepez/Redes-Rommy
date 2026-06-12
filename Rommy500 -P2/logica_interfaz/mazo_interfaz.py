from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
import pygame

Mazo = importar_desde_carpeta("mazo.py","Mazo")
Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")

CartelAlerta = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="CartelAlerta",
    nombre_carpeta="recursos_graficos",
)
BotonRadioImagenes = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="BotonRadioImagenes",
    nombre_carpeta="recursos_graficos",
)
constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos",
)





class Mazo_interfaz():
    def __init__(self,cantidad_cartas,x,y,scala,accion,un_juego=None):
        self.un_juego = un_juego
        self.cantidad_cartas = cantidad_cartas
        self.mazo_al_100 = self.un_juego._mazo_imagenes["mazo(1)"]
        self.mazo_al_50 = self.un_juego._mazo_imagenes["mazo(2)"]
        self.mazo_al_25 = self.un_juego._mazo_imagenes["mazo(3)"]
        self.mazo_al_5 = self.un_juego._mazo_imagenes["mazo(4)"]
        self.mazo_al_0 = self.un_juego._mazo_imagenes["mazo(5)"]
        self.x = x
        self.y = y
        self.scala = scala
        self.imagen = None
        self.prepar_imagen()
        self.elemento_mazo = None
        self.Elemento_mazo()
    def prepar_imagen(self):
        if self.cantidad_cartas >= 54:
            self.imagen = self.mazo_al_100
        elif self.cantidad_cartas >= 27 and self.cantidad_cartas < 54:
            self.imagen = self.mazo_al_50
        elif self.cantidad_cartas >= 10 and self.cantidad_cartas < 27:
            self.imagen = self.mazo_al_25
        elif self.cantidad_cartas >0 and self.cantidad_cartas <10:
            self.imagen = self.mazo_al_5
        else:
            self.imagen = self.mazo_al_0
        # self.imagen = self.mazo_al_100
    def Elemento_mazo(self):
        x = self.x
        y = self.y
        accion = lambda x: print(".")
        self.elemento_mazo = BotonRadioImagenes(
            un_juego=self.un_juego,
            imagen=self.imagen,
            scala=self.scala,
            x=x, y=y,
            radio_borde=5,
            color_borde=constantes.ELEMENTO_FONDO_TERCIARIO,
            color_borde_hover=constantes.ELEMENTO_FONDO_TERCIARIO,
            color_borde_clicado=constantes.ELEMENTO_FONDO_TERCIARIO,
            grupo=None,
            valor=None,
            deshabilitado=False,
            accion=accion,
            lift_offset=0
        )
    def Actualizar_mazo(self):
        self.prepar_imagen()
        self.elemento_mazo.scala = 0.05
        self.elemento_mazo.imagen = self.imagen
    
    def retornar_datos(self):
        return {
            "un_juego":self.un_juego,
            "cantidad_cartas": self.cantidad_cartas ,
            "x":  self.x ,
            "y":  self.y ,
            "scala" : self.scala ,
            "imagen": self.imagen ,
        }




