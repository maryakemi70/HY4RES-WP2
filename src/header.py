import streamlit as st
from PIL import Image

class DashboardHeader:
    """
    Header con texto centrado y imagen a la derecha
    """

    def __init__(self,
                 title_main: str = "INTELLIGENT RENEWABLE ENERGY MANAGEMENT",
                 title_sub: str = "Valle Inferior del Guadalquivir Irrigation District"):  # ancho máximo de la imagen
        self.title_main = title_main
        self.title_sub = title_sub

    def render(self):
        st.markdown(
            f"<h2 style='text-align: center; font-weight: 600;'>{self.title_main}</h2>"
            f"<h3 style='text-align: center; font-weight: 600;'>{self.title_sub}</h3>",
            unsafe_allow_html=True
        )



# class DashboardHeader:
#     """
#     Clase para mostrar el encabezado del dashboard con:
#     - Imagen izquierda
#     - Texto centrado
#     - Tres imágenes en la columna derecha
#     """
#
#     def __init__(self,
#                  img_left_path: str,
#                  img_right1_path: str,
#                  img_right2_path: str,
#                  img_right3_path: str,
#                  img_right4_path: str,
#                  title_main: str = "Intelligent RE Management", # "7-days ahead Energy Surplus",
#                  title_sub: str = "Valle Inferior del Guadalquivir Irrigation District"):
#         # Cargar imágenes
#         self.img_left = Image.open(img_left_path)
#         self.img_right1 = Image.open(img_right1_path)
#         self.img_right2 = Image.open(img_right2_path)
#         self.img_right3 = Image.open(img_right3_path)
#         self.img_right4 = Image.open(img_right4_path)
#
#         # Textos
#         self.title_main = title_main
#         self.title_sub = title_sub
#
#         # Inyectar CSS para centrar verticalmente
#         st.markdown(
#             """
#             <style>
#             .vertical-center {
#                 display: flex;
#                 align-items: center; /* centra verticalmente */
#                 justify-content: center; /* centra horizontalmente */
#                 height: 100px; /* altura del contenedor, ajustar según necesidad */
#             }
#             </style>
#             """,
#             unsafe_allow_html=True
#         )
#
#     def render(self):
#         """Renderiza el header completo en Streamlit"""
#
#         # Crear tres columnas principales
#         col1, col2, col3, col4 = st.columns([1, 4.5, 1, 1])
#
#         # Columna izquierda: imagen centrada
#         with col1:
#             st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
#             st.image(self.img_left, width=350)
#             st.markdown("</div>", unsafe_allow_html=True)
#
#         # Columna central: texto centrado
#         with col2:
#             st.markdown(
#                 f"<h2 style='text-align: center; font-weight: 600;'>{self.title_main}</h2>",
#                 unsafe_allow_html=True
#             )
#             st.markdown(
#                 f"<h3 style='text-align: center; font-weight: 600;'>{self.title_sub}</h3>",
#                 unsafe_allow_html=True
#             )
#
#         # Columna derecha: tres imágenes
#         with col3:
#             # Primera imagen (fila 1)
#             st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
#             st.image(self.img_right2, width=300)
#             st.markdown("</div>", unsafe_allow_html=True)
#
#             # Segunda imagen (fila 2)
#             st.markdown("<div style='text-align: center; margin-bottomp: 5px;'>", unsafe_allow_html=True)
#             st.image(self.img_right4, width=180)
#             st.markdown("</div>", unsafe_allow_html=True)
#
#
#         with col4:
#             subcol1, subcol2 = st.columns([1.2, 0.8])
#             # Tercera imagen
#             with subcol1:
#                 st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
#                 st.image(self.img_right1, width=100)
#                 st.markdown("</div>", unsafe_allow_html=True)
#
#             with subcol2:
#                 st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
#                 st.image(self.img_right3, width=100)
#                 st.markdown("</div>", unsafe_allow_html=True)