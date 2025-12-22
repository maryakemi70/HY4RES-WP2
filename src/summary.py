import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import plotly.express as px

class EnergySummary:
    """
    Displays an interactive energy distribution summary
    using a donut chart and individual cards for each category,
    including total demand and total PV production.
    """

    def __init__(self, df, mode='hourly', title="Energy Summary", time_horizon_days=7, selected_date="2020-01-01"):
        """
        df : pd.DataFrame
            Must contain columns: ['Demand', 'Production', 'SelfConsumption', 'GridConsumption', 'ExportToGrid']
        mode : str
            'hourly' or 'daily' (just for display in the title)
        title : str
            Title for the summary section
        """
        self.df = df.copy()
        self.mode = mode
        self.title = title
        self.time_horizon_days = time_horizon_days
        self.selected_date = selected_date

        # Elegant color palette
        self.colors_distribution = ['#6AA84F', '#D22C41', '#2078FF']  # Self, Grid, Export
        self.colors_overview = ['#AA4BFF', '#FF8D4B']  # Demand, PV Production
        self.text_overview = ['white', 'white']

        # Map coordinates
        self.latitude = 37.56153
        self.longitude = -5.815673

    def show_summary(self):
        # --- Title ---
        st.markdown(f"<h2 style='text-align:center'>{self.title} LALALALALALAL</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='text-align:center'>{self.time_horizon_days }-day ahead cumulative total from {self.selected_date} </h3>",
            unsafe_allow_html=True
        )

        # --- Totals ---
        total_self = self.df['SelfConsumption'].sum()
        total_grid = self.df['GridConsumption'].sum()
        total_export = self.df['ExportToGrid'].sum()
        total_energy = total_self + total_grid + total_export
        total_demand = self.df['Demand'].sum()
        total_production = self.df['Production'].sum()

        percentages = [total_self / total_energy * 100,
                       total_grid / total_energy * 100,
                       total_export / total_energy * 100]
        values = [total_self, total_grid, total_export]
        labels = ['Self-Consumption 🔄', 'Grid Consumption ⬅️', 'Export to Grid ➡️']

        # --- Columns: Donut + Map ---
        col1, col2 = st.columns([2, 1])

        # Donut chart
        with col1:
            fig = go.Figure(go.Pie(
                labels=[f"{label} [{p:.1f}%]" for label, p in zip(labels, percentages)],
                values=values,
                hole=0.5,
                marker_colors=self.colors_distribution,
                textinfo='label+percent',
                textfont_size=18
            ))
            st.plotly_chart(fig, use_container_width=True)

        # Map using Plotly
        with col2:
            map_fig = px.scatter_mapbox(
                lat=[self.latitude],
                lon=[self.longitude],
                zoom=4,  # aumentar zoom inicial
                height=450
            )
            # Añadir marcador
            map_fig.add_trace(go.Scattermapbox(
                lat=[self.latitude],
                lon=[self.longitude],
                mode='markers+text',
                marker=go.scattermapbox.Marker(size=14, color='red', allowoverlap=True),
                text=["📍 Valle Inferior del Guadalquivir Irrigation District"],
                textposition="top right",
                name="Valle Inferior del Guadalquivir Irrigation District",
                showlegend=False
            ))

            map_fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            st.plotly_chart(map_fig, use_container_width=True)

        # ----------------------
        # Cards for distribution
        # ----------------------
        st.markdown("### Detailed Energy Distribution")
        col1, col2, col3 = st.columns(3)
        for col, label, value, perc, color in zip(
                [col1, col2, col3], labels, values, percentages, self.colors_distribution
        ):
            col.markdown(
                f"""
                 <div style="background-color:{color};padding:15px;border-radius:10px;text-align:center;color:white">
                     <h4>{label}</h4>
                     <p style="font-size:22px;font-weight:bold">{value:.2f} kWh</p>
                     <p style="font-size:18px">{perc:.1f}% of total</p>
                 </div>
                 """,
                unsafe_allow_html=True
            )

        # ----------------------
        # Cards for total Demand and Production
        # ----------------------
        st.markdown("### Total Energy Overview")
        col1, col2 = st.columns(2)
        overview_info = [
            ("Total Energy Demand ⚡", total_demand, self.colors_overview[0], self.text_overview[0]),
            ("Total PV Production ☀️", total_production, self.colors_overview[1], self.text_overview[1])
        ]
        for col, (label, value, bg_color, text_color) in zip([col1, col2], overview_info):
            col.markdown(
                f"""
                 <div style="background-color:{bg_color};padding:15px;border-radius:10px;text-align:center;color:{text_color};border:1px solid #ccc">
                     <h4 style="color:{text_color}">{label}</h4>
                     <p style="font-size:22px;font-weight:bold">{value:.2f} kWh</p>
                 </div>
                 """,
                unsafe_allow_html=True

            )
