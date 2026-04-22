from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
import pygame

Cartas = importar_desde_carpeta(
    nombre_archivo= "cartas.py",
    nombre_clase= "Cartas")
BotonRadioImagenes = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonRadioImagenes","recursos_graficos")


class Cartas_interfaz(Cartas):
    def __init__(self, *args, un_juego = None,ruta_imagen=None,reverso=False,**kwargs):
        # Pasar todos los argumentos posicionales y nombrados al padre
        super().__init__(*args, **kwargs)
        self.un_juego = un_juego
        self.ruta_imagen = ruta_imagen
        # self.grupo = grupo
        self.parte_superior = pygame.image.load(self.ruta_imagen) if ruta_imagen is not None else None
        self.parte_trasera = None
        self.reverso = reverso
    def Elemento_carta(self, grupo, x, y, scala, imagen,mesa, deshabilitado=False):
        carta = BotonRadioImagenes(
            un_juego=self.un_juego,
            imagen=imagen,
            scala=scala,
            x=x, y=y,
            radio_borde=5,
            color_borde=(0, 0, 0),
            color_borde_hover=(255, 0, 0),
            color_borde_clicado=(0, 255, 0),
            grupo=grupo,
            valor=self.__str__(),
            deshabilitado=deshabilitado,
            accion=None,
            lift_offset=20,
            mesa=mesa
        )
        for i, c in enumerate(grupo):
            c.prioridad = i

        print(f"Carta creada: {self.__str__()} en posición ({x}, {y}) con escala {scala} y prioridad {carta.prioridad}")
        return carta

    def imagen_asociada(self,reverso=False):
        if reverso:
            return self.parte_trasera
        return self.parte_superior

    def to_dict(self):
        return {
            "numero": self.numero,
            "figura": self.figura,
            "ruta_imagen": self.ruta_imagen,
            "reverso": self.reverso
        }