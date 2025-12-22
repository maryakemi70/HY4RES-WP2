import os
import streamlit as st
import matplotlib
import plotly.subplots as sp
matplotlib.use('Agg')  # backend no interactivo, perfecto para Streamlit
from PIL import Image
from src.header import DashboardHeader
from src.data_loader import DataLoader
from src.surplus_calculator import SurplusCalculator
from src.plotter import LastDateEnergyPlotter
from src.summary import EnergySummary
from src.data_display import DataDisplay
from src.time_controls import TimeControlPanel
from src.sidebar import Sidebar

# Configuración de la página
st.set_page_config(
    page_title="HY4RES - VIGID Energy Surplus",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background: #f0f4f8;
        color: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True
)

class EnergySurplusApp:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.demand_path = os.path.join(base_dir, 'data', 'true_data.csv')
        self.production_path = os.path.join(base_dir, 'data', 'true_data.csv')

    def run(self):
        # --------------------------
        # Header
        # --------------------------
        header = DashboardHeader()
        header.render()


        # --------------------------
        # Sidebar
        # --------------------------
        sidebar = Sidebar(
            title="HY4RES",
            logo_path="figure/HY4RES_Logo.png",
            img_logo1_path="figure/logo_UCO.jpg",
            img_logo2_path="figure/New_logo_HD.jpg",
            img_logo3_path="figure/Trinity-Main-Logo.jpg"
        )

        page = sidebar.render()

        # --------------------------
        # Page logic
        # --------------------------
        if page == "Energy Surplus":
            self.page_energy_surplus()
        elif page == "Optimization":
            self.page_optimization()
        elif page == "Environmental Indicators":
            self.page_environmental_indicators()

    # --------------------------
    # Energy Surplus Page
    # --------------------------
    def page_energy_surplus(self):
        # Load demand and production data
        demand_loader = DataLoader(self.demand_path, datetime_col='Datetime')
        demand_loader.load()
        demand_df = demand_loader.get_series(value_col='Energy Consumption kWh', rename_to='Demand')

        prod_loader = DataLoader(self.production_path, datetime_col='Datetime')
        prod_loader.load()
        prod_df = prod_loader.get_series(value_col='Producción Planta', rename_to='Production')

        # Calculate surplus
        calculator = SurplusCalculator(demand_df, prod_df)
        result_df = calculator.calculate()
        min_date = result_df['Datetime'].min().date()
        max_date = result_df['Datetime'].max().date()
        # --------------------------
        # Time controls
        # --------------------------
        time_controls = TimeControlPanel(result_df)
        selected_date, time_horizon_days, mode = time_controls.render()

        # Luego lo usas con tu SurplusCalculator:
        if mode == 'hourly':
            hours = time_horizon_days * 24
            df_plot = calculator.get_last_hours_from(selected_date, hours=hours)
        else:
            df_plot = calculator.get_daily_aggregated_from(selected_date, days=time_horizon_days)
        table_df = df_plot.copy()

        # --------------------------
        # Summary section (pie charts)
        # --------------------------
        summary = EnergySummary(df_plot, mode, title=f"SUMMARY", time_horizon_days=time_horizon_days, selected_date=selected_date)
        summary.show_summary()
        st.markdown("---")

        # Plots
        plotter = LastDateEnergyPlotter(df_plot, mode=mode)

        # Multiselect para que el usuario elija qué mostrar
        st.markdown(
            f"<h2 style='text-align:center'>ENERGY SURPLUS</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align:center'>{mode} forecast from {selected_date} up to {time_horizon_days}-day ahead</h32>",
            unsafe_allow_html=True
        )


        # Table with CSV download
        table_display = DataDisplay(df=table_df, mode=mode)
        table_display.show_table_with_download(
            filename=f"energy_surplus_{mode}.csv",
            height=200
        )

        options = ['SelfConsumption', 'GridConsumption', 'ExportToGrid', 'Demand', 'Production']
        selected_options = st.multiselect(
            "Select which energy traces to display:",
            options=options,
            default=options  # por defecto se muestran todas
        )

        # Graficar solo los seleccionados
        if selected_options:
            combined_fig = plotter.plot_combined_with_selection(selected_options)
            st.plotly_chart(combined_fig, use_container_width=True)
        else:
            st.info("Select at least one trace to display.")

        figs = plotter.plot_all()
        col1, col2 = st.columns(2)
        with col1:
            DataDisplay(plotly_fig=figs['DemandVsProduction']).show_with_download(filename="energy_demand")
            DataDisplay(plotly_fig=figs['ExportToGrid']).show_with_download(filename="export_to_grid")
        with col2:
            DataDisplay(plotly_fig=figs['SelfConsumption']).show_with_download(filename="self_consumption")
            DataDisplay(plotly_fig=figs['GridConsumption']).show_with_download(filename="grid_consumption")

    # --------------------------
    # Optimization Page
    # --------------------------
    def page_optimization(self):
        st.header("Optimization")
        st.info("En proceso...")

    # --------------------------
    # Environmental Indicators Page
    # --------------------------
    def page_environmental_indicators(self):
        st.header("Environmental Indicators")
        st.info("En proceso...")


# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app = EnergySurplusApp()
    app.run()

    # streamlit cache clear
    # cd C:\Users\Win\PycharmProjects\IntegrationOfModels\Streamlit
    # streamlit run app.py

import os
import streamlit as st
import matplotlib
import plotly.subplots as sp
matplotlib.use('Agg')  # backend no interactivo, perfecto para Streamlit
from PIL import Image
from src.header import DashboardHeader
from src.data_loader import DataLoader
from src.surplus_calculator import SurplusCalculator
from src.plotter import LastDateEnergyPlotter
from src.summary import EnergySummary
from src.data_display import DataDisplay
from src.time_controls import TimeControlPanel
from src.sidebar import Sidebar

# Configuración de la página
st.set_page_config(
    page_title="HY4RES - VIGID Energy Surplus",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background: #f0f4f8;
        color: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True
)

class EnergySurplusApp:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.demand_path = os.path.join(base_dir, 'data', 'true_data.csv')
        self.production_path = os.path.join(base_dir, 'data', 'true_data.csv')

    def run(self):
        # --------------------------
        # Header
        # --------------------------
        header = DashboardHeader()
        header.render()


        # --------------------------
        # Sidebar
        # --------------------------
        sidebar = Sidebar(
            title="HY4RES",
            logo_path="figure/HY4RES_Logo.png",
            img_logo1_path="figure/logo_UCO.jpg",
            img_logo2_path="figure/New_logo_HD.jpg",
            img_logo3_path="figure/Trinity-Main-Logo.jpg"
        )

        page = sidebar.render()

        # --------------------------
        # Page logic
        # --------------------------
        if page == "Energy Surplus":
            self.page_energy_surplus()
        elif page == "Optimization":
            self.page_optimization()
        elif page == "Environmental Indicators":
            self.page_environmental_indicators()

    # --------------------------
    # Energy Surplus Page
    # --------------------------
    def page_energy_surplus(self):
        # Load demand and production data
        demand_loader = DataLoader(self.demand_path, datetime_col='Datetime')
        demand_loader.load()
        demand_df = demand_loader.get_series(value_col='Energy Consumption kWh', rename_to='Demand')

        prod_loader = DataLoader(self.production_path, datetime_col='Datetime')
        prod_loader.load()
        prod_df = prod_loader.get_series(value_col='Producción Planta', rename_to='Production')

        # Calculate surplus
        calculator = SurplusCalculator(demand_df, prod_df)
        result_df = calculator.calculate()
        min_date = result_df['Datetime'].min().date()
        max_date = result_df['Datetime'].max().date()
        # --------------------------
        # Time controls
        # --------------------------
        time_controls = TimeControlPanel(result_df)
        selected_date, time_horizon_days, mode = time_controls.render()

        # Luego lo usas con tu SurplusCalculator:
        if mode == 'hourly':
            hours = time_horizon_days * 24
            df_plot = calculator.get_last_hours_from(selected_date, hours=hours)
        else:
            df_plot = calculator.get_daily_aggregated_from(selected_date, days=time_horizon_days)
        table_df = df_plot.copy()

        # --------------------------
        # Summary section (pie charts)
        # --------------------------
        summary = EnergySummary(df_plot, mode, title=f"ENERGY SUMMARY", time_horizon_days=time_horizon_days, selected_date=selected_date)
        summary.show_summary()
        st.markdown("---")

        # Plots
        plotter = LastDateEnergyPlotter(df_plot, mode=mode)

        # Multiselect para que el usuario elija qué mostrar
        st.markdown(
            f"<h2 style='text-align:center'>ENERGY SURPLUS</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align:center'>{mode} forecast from {selected_date} up to {time_horizon_days}-day ahead</h32>",
            unsafe_allow_html=True
        )


        # Table with CSV download
        table_display = DataDisplay(df=table_df, mode=mode)
        table_display.show_table_with_download(
            filename=f"energy_surplus_{mode}.csv",
            height=200
        )

        options = ['SelfConsumption', 'GridConsumption', 'ExportToGrid', 'Demand', 'Production']
        selected_options = st.multiselect(
            "Select which energy traces to display:",
            options=options,
            default=options  # por defecto se muestran todas
        )

        # Graficar solo los seleccionados
        if selected_options:
            combined_fig = plotter.plot_combined_with_selection(selected_options)
            st.plotly_chart(combined_fig, use_container_width=True)
        else:
            st.info("Select at least one trace to display.")

        figs = plotter.plot_all()
        col1, col2 = st.columns(2)
        with col1:
            DataDisplay(plotly_fig=figs['DemandVsProduction']).show_with_download(filename="energy_demand")
            DataDisplay(plotly_fig=figs['ExportToGrid']).show_with_download(filename="export_to_grid")
        with col2:
            DataDisplay(plotly_fig=figs['SelfConsumption']).show_with_download(filename="self_consumption")
            DataDisplay(plotly_fig=figs['GridConsumption']).show_with_download(filename="grid_consumption")

    # --------------------------
    # Optimization Page
    # --------------------------
    def page_optimization(self):
        st.header("Optimization")
        st.info("En proceso...")

    # --------------------------
    # Environmental Indicators Page
    # --------------------------
    def page_environmental_indicators(self):
        st.header("Environmental Indicators")
        st.info("En proceso...")


# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app = EnergySurplusApp()
    app.run()

    # streamlit cache clear
    # cd C:\Users\Win\PycharmProjects\IntegrationOfModels\Streamlit
    # streamlit run app.py

