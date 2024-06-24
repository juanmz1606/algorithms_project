import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from itertools import combinations
import numpy as np
import json
from scipy.stats import wasserstein_distance
import pandas as pd
import copy
from time import time
import random

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
            
            
    def estrategiaFinal(self):
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
            
            #st.write("Tensor original")
            #st.write(probabilidadOriginal)
            #st.write(tensorOriginal)
            
            # Evaluar una partición aleatoria
            particion1, particion2 = self.particion_aleatoria(nodes)
            
            for combinacion in [particion1, particion2]:
                futuro = ""
                presente = ""
                tabla_marg = []
                for letra in combinacion:
                    if "'" in letra:
                        futuro += letra
                    else:
                        presente += letra
                        
                st.sidebar.warning(f"Presente: {presente}, Futuro: {futuro}")
                
                # Evaluar subgrafo
                probabilidad = self.generar_probabilidad(futuro, presente, estadosString, json_data)
                if probabilidad is None:
                    continue 
                for marg in probabilidad:
                    tabla_marg.append(marg)
                    
                tabla_marg_ordenada = sorted(tabla_marg, key=lambda x: x["letra"])
                
                st.write(combinacion)
                st.write(tabla_marg_ordenada)
            
    def particion_aleatoria(self,nodes):
        n = len(nodes)
        indices = list(range(n))
        random.shuffle(indices)
        mitad = n // 2

        particion1 = [nodes[i].label for i in indices[:mitad]]
        particion2 = [nodes[i].label for i in indices[mitad:]]

        # Verificar que ninguna partición esté vacía
        if not particion1:
            particion1.append(particion2.pop())
        if not particion2:
            particion2.append(particion1.pop())

        # Verificar que cada partición tiene al menos un nodo futuro
        if not any("'" in label for label in particion1):
            for i in range(len(particion2)):
                if "'" in particion2[i]:
                    particion1.append(particion2.pop(i))
                    break

        if not any("'" in label for label in particion2):
            for i in range(len(particion1)):
                if "'" in particion1[i]:
                    particion2.append(particion1.pop(i))
                    break

        # Verificar que ninguna partición esté vacía después del ajuste
        if not particion1 or not particion2:
            particion1, particion2 = [], []
            for i, index in enumerate(indices):
                if i % 2 == 0:
                    particion1.append(nodes[index].label)
                else:
                    particion2.append(nodes[index].label)

        return particion1, particion2       

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
            
            #st.write("Tensor original")
            #st.write(probabilidadOriginal)
            #st.write(tensorOriginal)
            
            combinaciones = []
            combinaTotales = self.generar_combinaciones_subgrafos(nodes,edges)
            
            tensores = []
            
            for combinacion in combinaTotales:
                futuro = ""
                presente = ""
                tabla_marg = []
                for letra in combinacion[1]:
                    if "'" in letra:
                        futuro += letra
                    else:
                        presente += letra
                        
                #Evaluar subgrafo1
                probabilidad = self.generar_probabilidad(futuro, presente,estadosString,json_data)
                if probabilidad is None:
                    continue 
                for marg in probabilidad:
                    tabla_marg.append(marg)
                    #tabla_marg.insert(0,marg)
                    
                futuro = ""
                presente = ""
                for letra in combinacion[0]: 
                    if "'" in letra:
                        
                        futuro += letra
                    else:
                        presente += letra
                        
                #Evaluar subgrafo2
                probabilidad = self.generar_probabilidad(futuro, presente,estadosString,json_data)
                if probabilidad is None:
                    continue 
                for marg in probabilidad:
                    tabla_marg.append(marg)
                    #tabla_marg.insert(0,marg)
                    
                tabla_marg_ordenada = sorted(tabla_marg, key=lambda x: x["letra"])
        
                # Calcular el producto tensorial de Kronecker para cada tensor en la lista
                for i, diccionario in enumerate(tabla_marg_ordenada):
                    # Acceder a los cálculos almacenados en el diccionario
                    tensor = np.array(diccionario["calculos"])
                    if i == 0:
                        producto_tensorial = tensor
                    else:
                        producto_tensorial = np.kron(producto_tensorial, tensor)
                #st.write(f"Tensor: {producto_tensorial}")
                # Añadir una copia del producto tensorial a la lista de tensores
                tensores.append(producto_tensorial.copy())
                combinaciones.append(combinacion)
                #st.write(combinacion)
                #st.write(tabla_marg_ordenada)
                #st.write(producto_tensorial)
            # Calcular la distancia de Wasserstein (EMD) entre cada tensor y el tensor original
            lista_emd = []
            #st.write(tensores)
            for i, tensor in enumerate(tensores):
                emd_distance = wasserstein_distance(np.arange(tensor.size), np.arange(tensorOriginal.size),
                                                    u_weights=tensor, v_weights=tensorOriginal)
                lista_emd.append(emd_distance)
                #st.write(f"Combinación: {combinaciones[i]}")
                #st.write(f"Tensor: {tensor}")
                #st.write(f"Distancia de Wasserstein (EMD) entre tensor y tensorOriginal: {emd_distance}")

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
            st.write(f"Pérdida total: {menor_perdida:.2f}")
            
            end_time = time()  # Marca el final del tiempo
            total_time = end_time - start_time  # Calcula el tiempo total
            st.write(f"Tiempo total de ejecución: {total_time:.2f} segundos")         
            
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
                    
                    emd_distance = wasserstein_distance(np.arange(tensor.size), np.arange(tensorOriginal.size),
                                                        u_weights=tensor, v_weights=tensorOriginal)
                    
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
                    
                    #st.text(df_tensores.to_string(index=False, header=False))
                    
                    #st.write("Origen: ",edge.source," Destino: ",edge.to, 
                    #                      " Pérdida: ", edge.label)
                    #st.write("--------------------------------------------------------")
                    
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
        st.write(f"Tiempo total de ejecución: {total_time:.2f} segundos")
        
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