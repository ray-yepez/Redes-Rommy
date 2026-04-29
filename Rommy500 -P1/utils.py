import socket

def getLocalIP():
    """Obtiene la IP local de la computadora"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1" #Local IP

def dprint(dic):
    """Para imprimir mas bonito un diccionario"""
    if type(dic) == dict:
        for clave, valor in dic.items():
            print(f"{str(clave).rjust(15)}: {valor}")
    else:
        return False