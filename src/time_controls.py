import streamlit as st
from PIL import Image

class TimeControlPanel:
    """
    Panel de control temporal:
    - Fecha de inicio
    - Horizonte temporal (pills)
    - Resolución temporal (segmented_control)
    - Imagen informativa a la derecha
    """
    def __init__(self, result_df, image_path="figure/Valle_Inferior.jpg", image_width=150):
        self.result_df = result_df
        self.image_path = image_path
        self.image_width = image_width

    def render(self):
        # Creamos tres columnas: fecha, controles, imagen
        col_date, col_controls, col_image = st.columns([2, 1, 0.5])

        # --- Selector de fecha ---
        with col_date:
            min_date = self.result_df['Datetime'].min().date()
            max_date = self.result_df['Datetime'].max().date()
            selected_date = st.date_input(
                "Start date",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )

        # --- Horizon y Resolution ---
        with col_controls:
            horizon_map = {"1 Day": 1, "3 Days": 3, "7 Days": 7}
            # Pills para horizonte
            time_horizon_label = st.pills(
                "Time Horizon",
                options=list(horizon_map.keys()),
                default="7 Days"
            )
            time_horizon_days = horizon_map[time_horizon_label]

            # Segmented control para resolución
            mode = st.segmented_control(
                "Time Resolution",
                options=["hourly", "daily"],
                default="hourly"
            )

        # --- Imagen ---
        with col_image:
            img = Image.open(self.image_path)
            # Redimensionamos proporcionalmente para ancho fijo
            w_percent = self.image_width / float(img.width)
            h_size = int((float(img.height) * float(w_percent)))
            img_resized = img.resize((self.image_width, h_size))
            st.image(img_resized)

        return selected_date, time_horizon_days, mode
