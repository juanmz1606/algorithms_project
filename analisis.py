import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class AnalisisApp:
    def __init__(self):
        pass

    def menu(self):
        if st.sidebar.button("Realizar Análisis"):
            if st.session_state.estrategia1["estadoInicial"] is None:
                st.sidebar.warning("Debe de ejecutar la estrategia 1 para realizar el análisis")
                return
            if st.session_state.estrategia2["estadoInicial"] is None:
                st.sidebar.warning("Debe de ejecutar la estrategia 2 para realizar el análisis")
                return

            # Suponiendo que los datos están en las variables proporcionadas
            datos = {
                'Estrategia': ['Estrategia 1', 'Estrategia 2'],
                'Estado Inicial': [st.session_state.estrategia1["estadoInicial"], st.session_state.estrategia2["estadoInicial"]],
                'Presentes': [st.session_state.estrategia1["valPresente"], st.session_state.estrategia2["valPresente"]],
                'Futuros': [st.session_state.estrategia1["valFuturo"], st.session_state.estrategia2["valFuturo"]],
                'Pérdida': [st.session_state.estrategia1["valPerdida"], st.session_state.estrategia2["valPerdida"]],
                'Tiempo': [f"{st.session_state.estrategia1['tiempo']:.3f}", f"{st.session_state.estrategia2['tiempo']:.3f}"]
            }

            # Convertir los datos en un DataFrame de pandas
            df = pd.DataFrame(datos)

            # Crear una figura y un eje con una mayor resolución
            fig, ax = plt.subplots(figsize=(8, 4), dpi=200)

            # Ocultar el eje
            ax.axis('tight')
            ax.axis('off')

            # Crear la tabla
            table = ax.table(cellText=df.values,
                             colLabels=df.columns,
                             cellLoc='center',
                             loc='center')

            # Estilizar la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.1, 1.1)  # Ajustar el escalado para hacer las columnas más anchas

            # Colorear las celdas de las categorías
            colors = plt.cm.BuPu(np.full(len(df.columns), 0.1))
            for i, key in enumerate(datos.keys()):
                cell = table[0, i]
                cell.set_fontsize(10)
                cell.set_text_props(weight='bold', color='black')
                cell.set_facecolor(colors[i])

            st.title("Análisis Comparativo de Estrategias")
            st.pyplot(fig)