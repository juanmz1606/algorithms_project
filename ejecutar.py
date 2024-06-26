import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from itertools import combinations
import numpy as np
import json
import pandas as pd
import copy
from time import time
import random
from scipy.optimize import linear_sum_assignment
from functools import reduce
from collections import defaultdict


class EjecutarApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Bipartito", "Componentes conexas",
                                              "Estrategia 1","Estrategia 2","Sustentacion Parcial",
                                              "Estrategia Final"])
        if submenu_opcion == "Bipartito":
            self.bipartito()
        if submenu_opcion == "Componentes conexas":
            self.mostrarComponentes()
        if submenu_opcion == "Estrategia 1":    
            self.estrategia1()
        if submenu_opcion == "Estrategia 2":    
            self.estrategia2()
        if submenu_opcion == "Sustentacion Parcial":
            self.sustentacionParcial()
        if submenu_opcion == "Estrategia Final":
            self.estrategiaFinal()
     
    def buscar_nodo(self, label):
        for nodo in st.session_state.grafo["nodes"]:
            if nodo.label == label:
                return nodo
        return None       
            
    def estrategiaFinal(self):
        # Configuración de la interfaz de usuario
        presenteUsuario = st.sidebar.text_input("Valores presentes")
        futuroUsuarioString = st.sidebar.text_input("Valores futuros")
        estadosString = st.sidebar.text_input("Estado inicial")
        st.sidebar.markdown("#### Se moverán los nodos menores o iguales a estos parámetros")
        gradoLimite = st.sidebar.number_input("Grado", min_value=0, step=1, format="%d")
        intermediacionLimite = st.sidebar.number_input("Intermediación (betweenness)", min_value=0.0, format="%.2f")
        
        ruta_archivo = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])
        
        # Estilo del botón (sin cambios)
        st.markdown("""
            <style>
            .stButton > button {
                background-color: white;
                border: 2px solid #f44336;
                color: #f44336;
                padding: 10px 24px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                width: 100%;
            }
            .stButton > button:hover {
                background-color: #f44336;
                color: white;
            }
            .stButton {
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.sidebar.button("Ejecutar"):
            if ruta_archivo is None:
                st.sidebar.warning("No se ha cargado un archivo")
                return
            
            start_time = time()
            json_data = json.load(ruta_archivo)
        
            futuroUsuario = [f"{valor.strip()}'" for valor in futuroUsuarioString.split("'") if valor.strip()]
            
            # Crear nodos y aristas
            nodes = self.crear_nodos(presenteUsuario, futuroUsuario)
            
            tensorOriginal = self.calcular_tensor_original(futuroUsuarioString, presenteUsuario, 
                                                           estadosString, json_data)
            
            particion1, particion2 = self.particion_aleatoria(nodes)
            emd_inicial = self.evaluarEMD(particion1, particion2, estadosString, json_data, tensorOriginal)
            emd_resultado = emd_inicial
            combinacion_resultado = [particion1.copy(), particion2.copy()]

            st.markdown("### Partición inicial:")
            st.write(f"Partición 1: {', '.join(particion1)}")
            st.write(f"Partición 2: {', '.join(particion2)}")
            st.write(f"EMD inicial: {emd_inicial:.3f}")

            # Evaluar movimientos
            emd_resultado, combinacion_resultado = self.evaluar_particiones(
                particion1, particion2, estadosString, json_data, tensorOriginal, 
                emd_resultado, combinacion_resultado, nodes, gradoLimite, intermediacionLimite
            )

            st.markdown("### Mejor combinación encontrada:")
            st.write(f"Partición 1: {', '.join(combinacion_resultado[0])}")
            st.write(f"Partición 2: {', '.join(combinacion_resultado[1])}")
            st.write(f"EMD óptimo: {emd_resultado:.3f}")

            end_time = time() - start_time
            st.write(f"Tiempo total de ejecución: {end_time:.3f} segundos")
            
            # Actualizar el estado de la sesión
            self.actualizar_sesion(estadosString, presenteUsuario, futuroUsuarioString, emd_resultado, end_time)

    def crear_nodos(self, presenteUsuario, futuroUsuario):
        nodos = defaultdict(lambda: {'grado': 0, 'intermediacion': 0})
        for letra in list(presenteUsuario) + futuroUsuario:
            letra_sin_comilla = letra.strip("'")
            nodo = self.buscar_nodo(letra_sin_comilla)
            if nodo:
                nodos[letra]['grado'] = getattr(nodo, 'grado', 0)
                nodos[letra]['intermediacion'] = getattr(nodo, 'intermediacion', 0)
        return [Node(id=i+1, label=letra, **attrs) for i, (letra, attrs) in enumerate(nodos.items())]

    def calcular_tensor_original(self, futuroUsuarioString, presenteUsuario, estadosString, json_data):
        probabilidadOriginal = self.generar_probabilidad(futuroUsuarioString, presenteUsuario, estadosString, json_data)
        if probabilidadOriginal:
            return reduce(np.kron, [np.array(d["calculos"]) for d in probabilidadOriginal])
        return None

    def evaluar_particiones(self, particion1, particion2, estadosString, json_data, tensorOriginal, 
                            emd_resultado, combinacion_resultado, nodes, gradoLimite, intermediacionLimite):
        for origen, destino in [(particion1, particion2), (particion2, particion1)]:
            emd_resultado, combinacion_resultado = self.evaluar_particion(
                origen, destino, estadosString, json_data, tensorOriginal, 
                emd_resultado, combinacion_resultado, nodes, gradoLimite, intermediacionLimite
            )
        return emd_resultado, combinacion_resultado

    def actualizar_sesion(self, estadosString, presenteUsuario, futuroUsuarioString, emd_resultado, end_time):
        st.session_state.estrategiaFinal = {
            "estadoInicial": estadosString,
            "valPresente": presenteUsuario,
            "valFuturo": futuroUsuarioString,
            "valPerdida": emd_resultado,
            "tiempo": end_time
        }
            
    def evaluar_particion(self, particion_origen, particion_destino, estadosString, 
                                     json_data, tensorOriginal, emd_resultado, combinacion_resultado, 
                                     nodes, gradoLimite, intermediacionLimite):
        nodos_origen = {n.label: n for n in nodes if n.label in particion_origen}
        
        for etiqueta, nodo in nodos_origen.items():
            if nodo.grado <= gradoLimite and nodo.intermediacion <= intermediacionLimite:
                particion_origen_temp = [e for e in particion_origen if e != etiqueta]
                
                if not particion_origen_temp:
                    continue
                
                particion_destino_temp = particion_destino + [etiqueta]
                emd_nuevo = self.evaluarEMD(particion_origen_temp, particion_destino_temp, estadosString, json_data, tensorOriginal)
                
                if emd_nuevo < emd_resultado:
                    emd_resultado = emd_nuevo
                    combinacion_resultado = [particion_origen_temp.copy(), particion_destino_temp.copy()]
        
        return emd_resultado, combinacion_resultado
            
                        
    def evaluarEMD(self, particion1, particion2, estadosString, json_data, tensorOriginal):
        tabla_marg = []
        for combinacion in (particion1, particion2):
            probabilidad = self.procesar_combinacion(combinacion,estadosString,json_data)
            if probabilidad is not None:
                tabla_marg.extend(probabilidad)

        if not tabla_marg:
            return float('inf')

        tabla_marg_ordenada = sorted(tabla_marg, key=lambda x: x["letra"])
        
        producto_tensorial = self.construir_producto_tensorial(tabla_marg_ordenada)
        
        if producto_tensorial is None:
            return float('inf')
        
        return self.hamming_emd_tensorial(producto_tensorial, tensorOriginal)
    
    def procesar_combinacion(self, combinacion,estadosString,json_data):
        futuro = ''.join(letra for letra in combinacion if "'" in letra)
        presente = ''.join(letra for letra in combinacion if "'" not in letra)
        return self.generar_probabilidad(futuro, presente, estadosString, json_data)
                        
                        
    def particion_aleatoria(self, nodes):
        n = len(nodes)
        indices = random.sample(range(n), n)
        division = random.randint(1, n - 1)

        particion1 = [nodes[i].label for i in indices[:division]]
        particion2 = [nodes[i].label for i in indices[division:]]

        # Asegurar que cada partición tiene al menos un elemento
        if not particion1:
            particion1.append(particion2.pop())
        elif not particion2:
            particion2.append(particion1.pop())

        # Asegurar que cada partición tiene al menos un nodo futuro
        futuro1 = any("'" in label for label in particion1)
        futuro2 = any("'" in label for label in particion2)

        if not futuro1 or not futuro2:
            nodo_futuro = next((label for label in particion2 if "'" in label), None) if not futuro1 else next((label for label in particion1 if "'" in label), None)
            if nodo_futuro:
                if not futuro1:
                    particion1.append(particion2.pop(particion2.index(nodo_futuro)))
                else:
                    particion2.append(particion1.pop(particion1.index(nodo_futuro)))

        # Si aún hay problemas, crear una partición alternativa
        if not particion1 or not particion2 or not futuro1 or not futuro2:
            particion1 = [nodes[i].label for i in indices[::2]]
            particion2 = [nodes[i].label for i in indices[1::2]]

        return particion1, particion2   
    
    def hamming_emd_tensorial(self, producto_tensorial, tensorOriginal):
        # Aplanar los tensores
        flat1 = producto_tensorial.ravel()
        flat2 = tensorOriginal.ravel()
        
        # Asegurarse de que los tensores tienen la misma longitud
        if flat1.shape != flat2.shape:
            raise ValueError("Los tensores deben tener la misma cantidad de elementos")
        
        # Definir una función de distancia de Hamming para escalares
        def hamming_scalar(x, y):
            return 0 if x == y else 1
        
        # Calcular la matriz de distancias de Hamming
        dist_matrix = np.zeros((len(flat1), len(flat2)))
        for i in range(len(flat1)):
            for j in range(len(flat2)):
                dist_matrix[i, j] = hamming_scalar(flat1[i], flat2[j])
        
        # Resolver el problema de asignación
        row_ind, col_ind = linear_sum_assignment(dist_matrix)
        
        # Calcular la EMD
        emd_distance = np.sum(dist_matrix[row_ind, col_ind] * np.minimum(flat1[row_ind], flat2[col_ind]))
        
        return emd_distance
    
    def construir_producto_tensorial(self, tabla_marg_ordenada):
        if not tabla_marg_ordenada:
            return None
        
        tensores = [np.array(d["calculos"]) for d in tabla_marg_ordenada]
        return reduce(np.kron, tensores)  

    def sustentacionParcial(self):
        presenteUsuario = st.sidebar.text_input("Valores presentes")
        futuroUsuario = st.sidebar.text_input("Valores futuros")

        ruta_archivo = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])

        if st.sidebar.button("Ejecutar"):
            if ruta_archivo is None:
                st.sidebar.warning("No se ha cargado un archivo")
                return

            # Leer el archivo JSON
            archivo_json = json.load(ruta_archivo)

            # Identificar las letras faltantes (las que no están en presenteUsuario)
            letras_faltantes_presente = [x for x in 'ABCD' if x not in presenteUsuario]

            # Inicializar los elementos filtrados con todos los elementos del JSON
            elementos_filtrados = archivo_json

            # Filtrar por las letras faltantes en 'presente'
            for letra_faltante in letras_faltantes_presente:
                indice_letra_faltante = 'ABCD'.index(letra_faltante)
                elementos_filtrados = [
                    item for item in elementos_filtrados 
                    if item['presente'][indice_letra_faltante] == '0'
                ]

            # Mostrar los presentes ajustados
            for item in elementos_filtrados:
                nuevo_presente = ''.join([
                    item['presente'][i] for i in range(len(item['presente'])) 
                    if 'ABCD'[i] in presenteUsuario
                ])
                item['presente'] = nuevo_presente

            # Si hay valores futuros proporcionados, filtrar también en 'futuro'
            if futuroUsuario:
                
                indices_letras_faltantes_futuro = [i for i, x in enumerate('ABCD') if x in futuroUsuario]

                for item in elementos_filtrados:
                    futuros_agrupados = {}

                    # Iterar sobre los futuros y agruparlos por las letras presentes en futuroUsuario
                    for key, value in item['futuro'].items():
                        nuevo_key = ''.join([key[i] for i in indices_letras_faltantes_futuro])
                        if nuevo_key in futuros_agrupados:
                            futuros_agrupados[nuevo_key] += value
                        else:
                            futuros_agrupados[nuevo_key] = value

                    # Actualizar el campo futuro del item con los futuros agrupados
                    item['futuro'] = futuros_agrupados

            # Mostrar los elementos filtrados
            st.write("Elementos filtrados:")
            st.json(elementos_filtrados)
            
            ##Acá se pasa al formato requerido, falta sumarlo todo el un json y guardarlo en una variable global
            #self.transformar_estructura(elementos_filtrados, futuroUsuario)
            
    def transformar_estructura(self, elementos_filtrados,futuroUsuario):
        # Lista para almacenar las probabilidades transformadas
        probabilidades = []

        for item in elementos_filtrados:
            presente = item["presente"]
            futuro = item["futuro"]
            
            # Convertimos el presente en una lista de enteros
            presente_lista = [int(bit) for bit in presente]
            
            # Obtenemos las probabilidades para el futuro
            probabilidad_0 = futuro["0"]
            probabilidad_1 = futuro["1"]
            
            # Creamos la entrada en el formato deseado y la agregamos a la lista
            entrada_transformada = [presente_lista, probabilidad_0, probabilidad_1]
            probabilidades.append(entrada_transformada)
        
        # Estructura final en formato JSON
        estructura_final = {
            "nombre": futuroUsuario + "'",
            "probabilidades": probabilidades
        }
        print(estructura_final)
            
                        
    def bipartito(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo para verificar si es bipartito.")
            return
        agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
        
        if st.sidebar.button("Verificar bipartito"):
            if self.isBipartito():
                # Si no se encuentra ningún conflicto de color, el grafo es bipartito
                st.sidebar.write("El grafo es bipartito.")
            else:
                st.sidebar.write("El grafo no es bipartito.")
        
    def mostrarComponentes(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo en la aplicación.")
            return
        if self.isBipartito():
            componentes = self.obtenerComponentesConexas()
            if len(componentes) > 1:
                    # Guardar las componentes en el estado de la sesión
                    st.session_state.componentes_conexas = []
                    # Obtener y guardar los nodos y aristas de cada componente conexa en el estado de la sesión
                    for componente in componentes:
                        selected_nodes = [node for node in st.session_state.grafo["nodes"] if node.id in componente]
                        selected_edges = [edge for edge in st.session_state.grafo["edges"] if
                                        edge.source in [node.id for node in selected_nodes] and 
                                        edge.to in [node.id for node in selected_nodes]]
                        config = st.session_state.grafo["config"]  # Usar la misma configuración que el grafo original
                        # Guardar el grafo de la componente en el estado de la sesión
                        st.session_state.componentes_conexas.append((selected_nodes, selected_edges, config))
                        
                    # Verificar si se ha seleccionado una componente y mostrarla
                    if hasattr(st.session_state, 'componentes_conexas'):
                        component_names = [f"Componente {i+1}" for i in range(len(st.session_state.componentes_conexas))]
                        selected_component = st.sidebar.selectbox("Seleccione un componente", component_names)
                        index = component_names.index(selected_component)

                        selected_nodes, selected_edges, config = st.session_state.componentes_conexas[index]
                        if st.sidebar.button("Mostrar componente"):
                            # Mostrar el grafo de la componente seleccionada
                            agraph(selected_nodes, selected_edges, config)
            else:
                    agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
                    st.sidebar.write("El grafo es conexo con una sola componente.")
        else:
                st.sidebar.write("El grafo no es bipartito. No se pueden evaluar componentes.")
                
    def estrategia1(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo en la aplicación.")
            return
        presenteUsuario = st.sidebar.text_input("Valores presentes")
        futuroUsuarioString = st.sidebar.text_input("Valores futuros")
        estadosString = st.sidebar.text_input("Estado inicial")
        
        # Pedir al usuario que ingrese la ruta del archivo
        ruta_archivo = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])
        
        if ruta_archivo is not None:
            start_time = time()  # Marca el inicio del tiempo
            json_data = json.load(ruta_archivo)
        
            # Separar los valores usando el caracter de comillas como delimitador
            valores_futuros_lista = futuroUsuarioString.split("'")

            # Eliminar elementos vacíos y espacios adicionales
            valores_futuros_lista = [valor.strip() for valor in valores_futuros_lista if valor.strip()]

            # Agregar comillas simples alrededor de cada letra
            futuroUsuario = [f"{valor}'" for valor in valores_futuros_lista]
            
            nodes = []
            edges = []
            i = 0
            idOrigen = 0
            
            for letra in presenteUsuario:
                    nodes.append(Node(id=i+1,label=letra))
                    i += 1
                    idOrigen += 1
            for letra in futuroUsuario:
                    nodes.append(Node(id=i+1,label=letra))
                    i += 1
                    
            for node in nodes:
                for node2 in nodes:
                    if node.id <= idOrigen and node2.id > idOrigen:
                        edges.append(Edge(source=node.id, target=node2.id, label="", color="#000000"))
            
            tabla_margOriginal = []
            probabilidadOriginal = self.generar_probabilidad(futuroUsuarioString, presenteUsuario,
                                                            estadosString, json_data)
            if probabilidadOriginal is not None:
                    for margOriginal in probabilidadOriginal:
                        tabla_margOriginal.append(margOriginal)
                        
            # Calcular el producto tensorial de Kronecker para cada tensor en la lista
            for i, diccionario in enumerate(tabla_margOriginal):
                tensor = np.array(diccionario["calculos"])
                if i == 0:
                    producto_tensorial = tensor
                else:
                    producto_tensorial = np.kron(producto_tensorial, tensor)
                    
            tensorOriginal = producto_tensorial.copy()
            
            # Diccionario de caché para almacenar combinaciones ya evaluadas
            cache = {}
            
            combinaciones = []
            combinaTotales = self.generar_combinaciones_subgrafos(nodes, edges)
            
            tensores = []
            
            for combinacion in combinaTotales:
                futuro = ""
                presente = ""
                tabla_marg = []
                
                combinacion_str = str(combinacion)
                if combinacion_str in cache:
                    tensores.append(cache[combinacion_str])
                    combinaciones.append(combinacion)
                    continue
                
                for letra in combinacion[1]:
                    if "'" in letra:
                        futuro += letra
                    else:
                        presente += letra
                        
                # Evaluar subgrafo1
                probabilidad = self.generar_probabilidad(futuro, presente, estadosString, json_data)
                if probabilidad is None:
                    continue 
                for marg in probabilidad:
                    tabla_marg.append(marg)
                    
                futuro = ""
                presente = ""
                for letra in combinacion[0]: 
                    if "'" in letra:
                        futuro += letra
                    else:
                        presente += letra
                        
                # Evaluar subgrafo2
                probabilidad = self.generar_probabilidad(futuro, presente, estadosString, json_data)
                if probabilidad is None:
                    continue 
                for marg in probabilidad:
                    tabla_marg.append(marg)
                    
                tabla_marg_ordenada = sorted(tabla_marg, key=lambda x: x["letra"])
        
                # Calcular el producto tensorial de Kronecker para cada tensor en la lista
                for i, diccionario in enumerate(tabla_marg_ordenada):
                    tensor = np.array(diccionario["calculos"])
                    if i == 0:
                        producto_tensorial = tensor
                    else:
                        producto_tensorial = np.kron(producto_tensorial, tensor)
                
                cache[combinacion_str] = producto_tensorial.copy()
                tensores.append(producto_tensorial.copy())
                combinaciones.append(combinacion)
                
            # Calcular la distancia de Wasserstein (EMD) entre cada tensor y el tensor original
            lista_emd = []
            for i, tensor in enumerate(tensores):
                emd_distance = self.hamming_emd_tensorial(tensor, tensorOriginal)
                lista_emd.append(emd_distance)
                
            lista_emd = np.array(lista_emd)

            # Encuentra el índice de la menor pérdida
            indice_menor_perdida = np.argmin(lista_emd)
            menor_perdida = lista_emd[indice_menor_perdida]

            # La combinación correspondiente a la menor pérdida
            combinacion_menor_perdida = combinaciones[indice_menor_perdida]
            tensor_menor_perdida = tensores[indice_menor_perdida]
            
            # Suponiendo que 'tensor_menor_perdida' y 'tensorOriginal' son arrays de numpy
            tensor_menor_perdida = np.array(tensor_menor_perdida)
            tensorOriginal = np.array(tensorOriginal)
            
            tensores_concatenados = np.vstack((tensor_menor_perdida, tensorOriginal))

            
            df_tensores  = pd.DataFrame(tensores_concatenados)

            # Estilo CSS
            st.markdown(
                """
                <style>
                    .title {
                        font-family: 'Georgia', serif;
                        font-size: 42px;
                        color: #333333;
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    .subtitle {
                        font-family: 'Helvetica Neue', sans-serif;
                        font-size: 24px;
                        color: #666666;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }
                    .content {
                        font-family: 'Helvetica Neue', sans-serif;
                        font-size: 16px;
                        color: #666666;
                        padding: 10px;
                        background-color: #f5f5f5;
                        border-radius: 5px;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Título principal
            st.markdown("<div class='title'>Resultados del análisis</div>", unsafe_allow_html=True)

            # Subtítulos y contenido
            st.markdown("<div class='subtitle'>Corte del sistema con menor pérdida:</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='content'>{combinacion_menor_perdida}</div>", unsafe_allow_html=True)

            st.markdown("<div class='subtitle'>Tensor correspondiente vs Tensor original:</div>", 
                        unsafe_allow_html=True)
            st.text(df_tensores.to_string(index=False, header=False))

            st.markdown("<div class='subtitle'>Total de pérdida del sistema con el corte:</div>", unsafe_allow_html=True)
            st.write(f"Pérdida total: {menor_perdida:.3f}")
            
            end_time = time()  # Marca el final del tiempo
            total_time = end_time - start_time  # Calcula el tiempo total
            st.write(f"Tiempo total de ejecución: {total_time:.3f} segundos")         
            
            st.session_state.estrategia1["estadoInicial"] = estadosString
            st.session_state.estrategia1["valPresente"] = presenteUsuario
            st.session_state.estrategia1["valFuturo"] = futuroUsuarioString
            st.session_state.estrategia1["valPerdida"] = menor_perdida
            st.session_state.estrategia1["tiempo"] = total_time

    
            
            
    def estrategia2(self):
        #if st.session_state.grafo["nodes"] is None:
        #    st.sidebar.warning("No se tiene un grafo en la aplicación.")
        #    return
        if self.isBipartito():
            
            presenteUsuario = st.sidebar.text_input("Valores presentes")
            futuroUsuarioString = st.sidebar.text_input("Valores futuros")
            estadosString = st.sidebar.text_input("Estado inicial")
            
            st.session_state.estrategia2["estadoInicial"] = estadosString
            st.session_state.estrategia2["valPresente"] = presenteUsuario
            st.session_state.estrategia2["valFuturo"] = futuroUsuarioString
            #futuroOriginal = ""
            #presenteOriginal = ""
            tabla_margOriginal = []
        
            # Pedir al usuario que ingrese la ruta del archivo
            ruta_archivo = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])
            
            if ruta_archivo is not None:
                
                start_time = time()  # Marca el inicio del tiempo
                
                json_data = json.load(ruta_archivo)
                
                valores_futuros_lista = futuroUsuarioString.split("'")

                # Eliminar elementos vacíos y espacios adicionales
                valores_futuros_lista = [valor.strip() for valor in valores_futuros_lista if valor.strip()]

                # Agregar comillas simples alrededor de cada letra
                futuroUsuario = [f"{valor}'" for valor in valores_futuros_lista]
                
                
                
                ##ORIGINAL
                #for node in st.session_state.grafo["nodes"]:
                #    if "'" in node.label:
                #        futuroOriginal += node.label
                #    else:
                #        presenteOriginal += node.label
                
                nodes = []
                edges = []
                i = 0
                idOrigen = 0
                
                for letra in presenteUsuario:
                        nodes.append(Node(id=i+1,size=float(10),label=letra,shape="circle"))
                        i += 1
                        idOrigen += 1
                for letra in futuroUsuario:
                        nodes.append(Node(id=i+1,size=float(10),label=letra,shape="circle"))
                        i += 1
                        
                for node in nodes:
                    for node2 in nodes:
                        if node.id <= idOrigen and node2.id > idOrigen:
                            edges.append(Edge(source=node.id, target=node2.id, label="", color="#000000"))
                            
                #Salvar el grafo original
                config = Config(width=600, height=450, directed=True, physics=True, hierarchical=False)
                    
                st.session_state.grafo = {"nodes":nodes,
                                        "edges":edges,
                                        "config": config}    
                
                st.session_state.grafo_temporal = copy.deepcopy(st.session_state.grafo)
                   
                probabilidadOriginal = self.generar_probabilidad(futuroUsuarioString, presenteUsuario,
                                                                    estadosString,json_data)
                if probabilidadOriginal is not None:
                        for margOriginal in probabilidadOriginal:
                            tabla_margOriginal.append(margOriginal)
                
                            
                #Calcular el producto tensorial de Kronecker para cada tensor en la lista
                for i, diccionario in enumerate(tabla_margOriginal):
                    tensor = np.array(diccionario["calculos"])
                    if i == 0:
                        producto_tensorial = tensor
                    else:
                        producto_tensorial = np.kron(producto_tensorial, tensor)
                        
                tensorOriginal = producto_tensorial.copy()
                
                
                aristasEliminadas = []
                
                copyEdges = st.session_state.grafo["edges"][:]
                
                for edge in copyEdges:
                    presenteId = edge.source
                    futuroId = edge.to
                    
                    for node in st.session_state.grafo["nodes"]:
                        if node.id == presenteId:
                            presente = node.label
                            presente = presenteUsuario.replace(presente, "")
                            
                    for node in st.session_state.grafo["nodes"]:
                        if node.id == futuroId:
                            futuro = node.label
                            futuroSinDestino = futuroUsuarioString.replace(futuro, "")
                    
                    tabla_marg = []
                    
                    probabilidad = self.generar_probabilidad(futuro, presente,estadosString,json_data)
                    for marg in probabilidad:
                        tabla_marg.append(marg)
                        
                    probabilidadSinDestino = self.generar_probabilidad(futuroSinDestino, presenteUsuario,
                                                             estadosString,json_data)   
                    for marg in probabilidadSinDestino:
                        tabla_marg.append(marg) 
                    
                    tabla_marg_ordenada = sorted(tabla_marg, key=lambda x: x["letra"])
                        
                    for i, diccionario in enumerate(tabla_marg_ordenada):
                        tensor = np.array(diccionario["calculos"])
                        if i == 0:
                            producto_tensorial = tensor
                        else:
                            producto_tensorial = np.kron(producto_tensorial, tensor)
                            
                    tensor = producto_tensorial.copy()
                    
                    #emd_distance = wasserstein_distance(np.arange(tensor.size), np.arange(tensorOriginal.size),
                    #                                    u_weights=tensor, v_weights=tensorOriginal)
                    
                    emd_distance = self.hamming_emd_tensorial(tensor, tensorOriginal)
                    
                    edge.label = emd_distance
                    
                    # Suponiendo que 'tensor_menor_perdida' y 'tensorOriginal' son arrays de numpy
                    tensor = np.array(tensor)
                    tensorOriginal = np.array(tensorOriginal)
                    
                    # Asegurarse de que las dimensiones coinciden para la concatenación
                    if tensor.shape != tensorOriginal.shape:
                        # Redimensionar 'tensor' para que coincida con 'tensorOriginal'
                        tensor = np.resize(tensor, tensorOriginal.shape)
                    
                    tensores_concatenados = np.vstack((tensor, tensorOriginal))
                    
                    df_tensores  = pd.DataFrame(tensores_concatenados)
                    
                    # st.text(df_tensores.to_string(index=False, header=False))
                    
                    # st.write("Origen: ",edge.source," Destino: ",edge.to, 
                    #                       " Pérdida: ", edge.label)
                    # st.write("--------------------------------------------------------")
                    
                    if emd_distance == 0:
                        aristasEliminadas.append(copy.deepcopy(edge))
                        st.session_state.grafo["edges"].remove(edge)
                        componentes = []        
                        componentes = self.obtenerComponentesConexas()
                        if len(componentes) > 1:
                            for node_id in componentes[1]:
                                for node in st.session_state.grafo["nodes"]:
                                    if node.id == node_id:
                                        node.color = "#FF0000"  # Cambiar el color del nodo
                            end_time = time()  # Marca el final del tiempo
                            total_time = end_time - start_time  # Calcula el tiempo total 
                            self.finEstrategia2(aristasEliminadas,total_time)
                            aristasEliminadas = []
                            return
                       
                componentes = [] 
                
                while len(componentes) <= 1:
                    min_valor = float('inf')  # Inicializar el mínimo con un valor alto
                    edge_con_min_valor = None  # Inicializar el borde con el valor mínimo como None

                    # Iterar sobre los bordes y encontrar el mínimo valor de edge.label
                    for edge in st.session_state.grafo["edges"]:
                        if edge.label < min_valor:  # Verificar si es menor que el mínimo actual
                            min_valor = edge.label
                            edge_con_min_valor = edge
    
                    aristasEliminadas.append(copy.deepcopy(edge_con_min_valor))        
                    st.session_state.grafo["edges"].remove(edge_con_min_valor)
                    componentes = self.obtenerComponentesConexas() 
                
                
                for node_id in componentes[1]:
                    for node in st.session_state.grafo["nodes"]:
                        if node.id == node_id:
                            node.color = "#FF0000"  # Cambiar el color del nodo
                 
                end_time = time()  # Marca el final del tiempo
                total_time = end_time - start_time  # Calcula el tiempo total    
                self.finEstrategia2(aristasEliminadas,total_time)
                aristasEliminadas = []
                
                return

    def finEstrategia2(self,aristasEliminadas, total_time):
        totalPerdida = 0
        
        #SE VUELVE STRING PARA LA VISUALIZACION EL EMD
        for edge in st.session_state.grafo["edges"]:
            edge.label = str(edge.label)
        
        st.subheader("Se eliminaron las siguientes aristas")
        
        for aristaElim in aristasEliminadas:
            origen = ""
            destino = ""
            for node in st.session_state.grafo["nodes"]:
                        if node.id == aristaElim.source:
                            origen = node.label
                        if node.id == aristaElim.to:
                            destino = node.label
                            
            totalPerdida = totalPerdida + float(aristaElim.label)
            aristaElim.dashes = True
            aristaElim.label = str(aristaElim.label)
            aristaElim.color = "#FF0000"
            st.session_state.grafo["edges"].append(aristaElim)
            
            st.write("Origen: ",origen," - Destino: ",destino, 
                        " - Pérdida: ", aristaElim.label)
            
        st.subheader("Se encontró una partición en el grafo")
        agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                st.session_state.grafo["config"])
        
        st.write(f"La perdida total en el corte es de: {totalPerdida}")    
        st.write(f"Tiempo total de ejecución: {total_time:.3f} segundos")
        
        st.session_state.estrategia2["valPerdida"] = totalPerdida
        st.session_state.estrategia2["tiempo"] = total_time
        
        st.session_state.grafo = copy.deepcopy(st.session_state.grafo_temporal)
        return

            
    def generar_probabilidad(self,futuro,presente, estadosString, json_data):

        estados = [int(estado) for estado in estadosString]
        
        
        # Separar los valores usando el caracter de comillas como delimitador
        valores_futuros_lista = futuro.split("'")

        # Eliminar elementos vacíos y espacios adicionales
        valores_futuros_lista = [valor.strip() for valor in valores_futuros_lista if valor.strip()]

        # Agregar comillas simples alrededor de cada letra
        futuro = [f"{valor}'" for valor in valores_futuros_lista]
        
        #if not futuro:
        #    return None
        
        for dato in json_data:
            st.session_state.tablas_prob[dato["nombre"]] = dato["probabilidades"]
            
        variables = ""
        destinos = []
        tabla_marg = []
        
        for edge in st.session_state.grafo["edges"]:
            destinos.append(edge.to)
            
        for node in st.session_state.grafo["nodes"]:
            if node.id not in destinos:
                variables += node.label
        #st.write(estados)
        # Asegurarse de que las variables están en orden alfabético
        variables = ''.join(sorted(variables))

        # Crear un diccionario para mapear variables a sus estados
        estadoInicial = {}
        for var in variables:
            if var in presente:
                # Obtener la posición alfabética de la variable
                posicion = variables.index(var)
                # Asignar el estado basado en la posición
                estadoInicial[var] = estados[posicion]
            else:
                estadoInicial[var] = None
        #st.write(estadoInicial)
        

        if presente == '':
            
            for tabla_name in futuro:
                marg = {}
                tabla_name_sin_comilla = tabla_name.replace("'", "")
                marg["letra"] = tabla_name_sin_comilla
                marg["calculos"] = self.vacio(tabla_name)
                tabla_marg.append(marg)
        
        else:
            # Iterar sobre cada tabla_name en futuro y llamar a marginalizar
            for tabla_name in futuro:
                marg = {}
                tabla_name_sin_comilla = tabla_name.replace("'", "")
                marg["letra"] = tabla_name_sin_comilla
                marg["calculos"] = self.marginalizar(tabla_name, presente, estadoInicial)
                tabla_marg.append(marg)
                
        return tabla_marg


    def obtenerComponentesConexas(self):
        nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
        for edge in st.session_state.grafo["edges"]:
            if edge.source in nodes and edge.to in nodes:
                nodes[edge.source].append(edge.to)
                nodes[edge.to].append(edge.source)

        visited = set()
        components = []
        for node_id in nodes:
            if node_id not in visited:
                component = set()
                self.dfs(node_id, nodes, visited, component)
                components.append(component)
        return components

    def dfs(self, node, nodes, visited, component):
        visited.add(node)
        component.add(node)
        for neighbor in nodes[node]:
            if neighbor not in visited:
                self.dfs(neighbor, nodes, visited, component)

    def isBipartito(self):
        nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
        for edge in st.session_state.grafo["edges"]:
            if edge.source in nodes and edge.to in nodes:
                nodes[edge.source].append(edge.to)
                nodes[edge.to].append(edge.source)

        # Algoritmo de BFS para verificar si el grafo es bipartito
        
            color = {}  # Un diccionario para mantener los colores de los nodos
            for node_id in nodes:
                color[node_id] = None  

            for node_id in nodes:  
                if color[node_id] is None:  # Si el nodo no ha sido coloreado
                    color[node_id] = 0  # Asignar un color al nodo (0 o 1)
                    queue = [node_id]  # Inicializar una cola con el nodo actual
                    while queue:  # Mientras la cola no esté vacía
                        u = queue.pop(0)  # Extraer el primer nodo de la cola
                        for v in nodes[u]:  # Iterar sobre todos los nodos adyacentes al nodo u
                            if color[v] is None:  # Si el nodo adyacente no ha sido coloreado
                                color[v] = 1 - color[u]  # Asignar un color diferente al nodo adyacente
                                queue.append(v)  # Agregar el nodo adyacente a la cola
                            elif color[v] == color[u]:  # Si el nodo adyacente tiene el mismo color que u
                                # Si se encuentra un conflicto de color, el grafo no es bipartito
                                return False
        return True
    
    def generar_combinaciones_subgrafos(self,nodes,edges):
        # Mapear los identificadores de los nodos a sus labels
        node_labels = {node.id: node.label for node in nodes}

        # Generar todas las combinaciones posibles de nodos
        combinaciones = []
        for r in range(1, len(nodes) // 2 + 1):
            for subgrafo_nodos in combinations(nodes, r):
                subgrafo_nodos_set = set(node.id for node in subgrafo_nodos)
                otros_nodos_set = {node.id for node in nodes} - subgrafo_nodos_set
                subgrafo_aristas = [(edge.source, edge.to, edge.label) for edge in edges if edge.source in subgrafo_nodos_set and edge.to in subgrafo_nodos_set]
                otros_nodos_aristas = [(edge.source, edge.to, edge.label) for edge in edges if edge.source in otros_nodos_set and edge.to in otros_nodos_set]
                aristas_restantes = [(edge.source, edge.to, edge.label) for edge in edges if edge.source not in subgrafo_nodos_set and edge.to not in subgrafo_nodos_set]
                combinaciones.append((subgrafo_nodos_set, subgrafo_aristas, otros_nodos_set, otros_nodos_aristas, aristas_restantes))

        # Almacenar las combinaciones en la estructura de datos deseada
        combinaciones_finales = []
        combinaciones_vistas = set()  # Para almacenar los subgrafos ya vistos

        for combinacion in combinaciones:
            subgrafo_1 = [node_labels[nodo_id] for nodo_id in combinacion[0]]
            subgrafo_2 = [node_labels[nodo_id] for nodo_id in combinacion[2]]

            # Convertir los subgrafos a listas ordenadas para comparación
            subgrafo_1_sorted = tuple(sorted(subgrafo_1))
            subgrafo_2_sorted = tuple(sorted(subgrafo_2))

            # Si alguno de los subgrafos ya ha sido visto, continuar con la siguiente iteración
            #if subgrafo_1_sorted in combinaciones_vistas or subgrafo_2_sorted in combinaciones_vistas:
            #    continue

            # Verificar que tanto las aristas del primer subgrafo como las del segundo subgrafo no estén vacías
            if not combinacion[1] and not combinacion[3]:
                continue

            # Si no ha sido vista, agregarla al conjunto de subgrafos vistos y a la lista de combinaciones finales
            combinaciones_vistas.add(subgrafo_1_sorted)
            combinaciones_vistas.add(subgrafo_2_sorted)
            combinaciones_finales.append((subgrafo_1_sorted, subgrafo_2_sorted))
        return combinaciones_finales
        
    def vacio(self,presenteVacio):
        tabla_original = st.session_state.tablas_prob[presenteVacio]
        sumaFilaCero = 0
        sumaFilaUno = 0
        tabla_vacio = []
        i = 0
        
        for fila in tabla_original:
            sumaFilaCero += fila[1]
            sumaFilaUno += fila[2]
            i += 1
            
        tabla_vacio = (sumaFilaCero / i, sumaFilaUno / i)
        return tabla_vacio
        
    def marginalizar(self, tabla_name, presente, estadoInicial):
        tabla_original = st.session_state.tablas_prob[tabla_name]
        indices_presente = [ord(var) - ord('A') for var in presente]
        suma_penultimos_valores = 0
        suma_ultimos_valores = 0
        contador_filas = 0  # Nueva variable para contar las filas
        for fila in tabla_original:
            condicion_cumplida = True
            for i in range(len(presente)):
                if estadoInicial[presente[i]] is not None and fila[0][indices_presente[i]] != estadoInicial[presente[i]]:
                    condicion_cumplida = False
                    break

            if condicion_cumplida:
                tupla1 = fila[0]
                penultimo_valor = fila[1]
                ultimo_valor = fila[2]
                suma_penultimos_valores += penultimo_valor
                suma_ultimos_valores += ultimo_valor
                contador_filas += 1  # Incrementar el contador de filas

        if tabla_original:
            resultado1 = suma_penultimos_valores / contador_filas  # Dividir por el contador de filas
            resultado2 = suma_ultimos_valores / contador_filas  # Dividir por el contador de filas
            return resultado1, resultado2
        
    