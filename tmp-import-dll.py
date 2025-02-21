import ctypes

# Charger la DLL
chemin_dll = "./UHFReader288.dll"  # Chemin relatif ou absolu de la DLL
reader = ctypes.CDLL(chemin_dll)

# Déclaration des types d'arguments et du retour de la fonction
# int AutoOpenComPort(int* port, BYTE* address, BYTE baud, int* FrmHandle);
reader.AutoOpenComPort.argtypes = [
    ctypes.POINTER(ctypes.c_int),       # int* port
    ctypes.POINTER(ctypes.c_ubyte),    # BYTE* address
    ctypes.c_ubyte,                    # BYTE baud
    ctypes.POINTER(ctypes.c_int)       # int* FrmHandle
]
reader.AutoOpenComPort.restype = ctypes.c_int  # La fonction retourne un int

# Préparer les arguments
port = ctypes.c_int(0)       # Port initialisé à 0
address = ctypes.c_ubyte(255)  # Adresse de diffusion (broadcasting address)
baud = ctypes.c_ubyte(0)     # Baud rate (19200 ici)
FrmHandle = ctypes.c_int(-1) # Frame handle, initialisé à -1

# Appeler la fonction
fCmdRet = reader.AutoOpenComPort(
    ctypes.byref(port),      # Passer un pointeur vers port
    ctypes.byref(address),   # Passer un pointeur vers address
    baud,                    # Passer directement la valeur de baud
    ctypes.byref(FrmHandle)  # Passer un pointeur vers FrmHandle
)

# Afficher les résultats
print(f"Return code: {hex(fCmdRet)}")
print(f"Port: {port.value}")
print(f"Frame Handle: {FrmHandle.value}")

