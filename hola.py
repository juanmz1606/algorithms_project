def leer_datos_archivo(filename):
    with open(filename, 'r') as file:
        datos = []
        for line in file:
            line = line.strip().strip('[],')
            line = line.replace(' ', '')  # Eliminar todos los espacios en blanco
            if line:  # Asegurarse de que la línea no esté vacía después del procesamiento
                datos.append([int(x) for x in line.split(',')])
    return datos

def generar_combinaciones_alternadas(n):
    combinaciones = []
    for i in range(2 ** n):
        bin_str = format(i, f'0{n}b')
        alternada = [int(bin_str[-j-1]) for j in range(n)]  # Invertir el orden de los bits
        combinaciones.append(tuple(alternada))
    return combinaciones

# Leer los datos del archivo
datos = leer_datos_archivo('datos.txt')

# Generar las combinaciones alternadas para 8 nodos
combinaciones = generar_combinaciones_alternadas(8)

# Crear la estructura completa con los datos del archivo
estructura_final = []
for comb, dato in zip(combinaciones, datos):
    estructura_final.append([comb, dato[0], 1-dato[0]])  # Usar el valor correspondiente del archivo

# Mostrar la estructura final obtenida
for lista in estructura_final:
    print(lista, end=",\n")
