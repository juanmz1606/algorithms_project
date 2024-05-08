import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from itertools import combinations
import numpy as np
import json

class EjecutarApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Bipartito", "Componentes conexas",
                                              "Estrategia 1"])
        if submenu_opcion == "Bipartito":
            self.bipartito()
        if submenu_opcion == "Componentes conexas":
            self.mostrarComponentes()
        if submenu_opcion == "Estrategia 1":    
            self.estrategia1()
                        
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
            for i, tensor in enumerate(tabla_margOriginal):
                if i == 0:
                    producto_tensorial = tensor
                else:
                    producto_tensorial = np.kron(producto_tensorial, tensor)
                    
            tensorOriginal = producto_tensorial.copy()
            
            st.write(probabilidadOriginal)
            st.write(tensorOriginal)
            
            combinaciones = self.generar_combinaciones_subgrafos(nodes,edges)
            
            tensores = []
            
            for combinacion in combinaciones:
                futuro = ""
                presente = ""
                tabla_marg = []
                for letra in combinacion[0]:
                    if "'" in letra:
                        futuro += letra
                    else:
                        presente += letra
                        
                #Evaluar subgrafo1
                probabilidad = self.generar_probabilidad(futuro, presente,estadosString,json_data)
                if probabilidad is not None:
                    for marg in probabilidad:
                        tabla_marg.append(marg)
                    
                futuro = ""
                presente = ""
                for letra in combinacion[1]: 
                    if "'" in letra:
                        
                        futuro += letra
                    else:
                        presente += letra
                        
                #Evaluar subgrafo2
                probabilidad = self.generar_probabilidad(futuro, presente,estadosString,json_data)
                if probabilidad is not None:
                    for marg in probabilidad:
                        tabla_marg.append(marg)
        
                # Calcular el producto tensorial de Kronecker para cada tensor en la lista
                for i, tensor in enumerate(tabla_marg):
                    if i == 0:
                        producto_tensorial = tensor
                    else:
                        producto_tensorial = np.kron(producto_tensorial, tensor)
                tensores.append(producto_tensorial.copy())
                
                st.write(combinacion)
                st.write(tabla_marg)
                st.write(producto_tensorial)
                
            #for tensor in tensores:
                #Aca se tiene cada tensor de cada combinacion
                #Comparar con el original para obtener cierto valor de peso
            
    def generar_probabilidad(self,futuro,presente, estadosString, json_data):
        
        estados = [int(estado) for estado in estadosString]
        
        # Separar los valores usando el caracter de comillas como delimitador
        valores_futuros_lista = futuro.split("'")

        # Eliminar elementos vacíos y espacios adicionales
        valores_futuros_lista = [valor.strip() for valor in valores_futuros_lista if valor.strip()]

        # Agregar comillas simples alrededor de cada letra
        futuro = [f"{valor}'" for valor in valores_futuros_lista]
        
        if not futuro:
            return
        
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
        
        estadoInicial = {var: (estados.pop(0) if var in presente else None) for var in variables}
        if presente == '':
            
            for tabla_name in futuro:
                tabla_marg.append(self.vacio(tabla_name))
        
        else:
            # Iterar sobre cada tabla_name en futuro y llamar a marginalizar
            for tabla_name in futuro:
                tabla_marg.append(self.marginalizar(tabla_name, presente, estadoInicial))
            
        return tabla_marg

    def obtenerComponentesConexas(self):
        nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
        for edge in st.session_state.grafo["edges"]:
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
            if subgrafo_1_sorted in combinaciones_vistas or subgrafo_2_sorted in combinaciones_vistas:
                continue

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