class Cartas:
    valores = {"joker": 0, "a": 1, "j": 11, "q": 12, "k": 13}
    mazo = 54

    def __init__(self, numero, figura):
        self.numero = numero
        self.figura = figura

    def __str__(self):
        return f'{self.numero} de {self.figura}'

    def valor_numerico(self):
        
        if str(self.numero).lower() == 'joker':
            return 0
        if str(self.numero).isdigit():
            return int(self.numero)
        return Cartas.valores[str(self.numero).lower()]

#==========Inicio Jesua===========
    def valor_puntaje(self):
        """Devuelve los puntos que suma la carta al final de la ronda según Rummy 500."""
        num = self.numero
        try:
            num_str = str(num)
        except Exception:
            return 0

        if num_str.lower() == 'joker':
            return 25
        if num_str == 'A':
            return 15
        if num_str in ['10', 'J', 'Q', 'K']:
            return 10
        if num_str in ['2','3','4','5','6','7','8','9']:
            return 5
        return 0
#==========Fin Jesua===========
