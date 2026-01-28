import os
import plotly.express as px
import pandas as pd
import streamlit as st
import matplotlib
import plotly.subplots as sp
from pathlib import Path

matplotlib.use('Agg')  # backend no interactivo
from PIL import Image
from src.header import DashboardHeader
from src.data_loader import DataLoader
from src.surplus_calculator import SurplusCalculator
from src.plotter import LastDateEnergyPlotter
from src.summary import EnergySummary
from src.data_display import DataDisplay
from src.time_controls import TimeControlPanel
from src.sidebar import Sidebar
from src.environmental_indicators.ei_service import EnvironmentalIndicatorsService
from src.services.energy_data_service import EnergyDataService
from src.environmental_indicators.ei_summary import ImpactAssessment, EI_METADATA
from src.utils.formating import style_impact_table, color_net_impact, add_pv_multiheader
from deep_translator import GoogleTranslator
from src.intro_page import IntroPage
from deep_translator import GoogleTranslator

# Translate function
@st.cache_data(show_spinner=False)
def t(text: str) -> str:
    lang = st.session_state.get("lang", "English")
    LANGS = {
        "English": "en",
        "Spanish": "es",
        "Portuguese": "pt",
        "French": "fr"
    }
    target = LANGS.get(lang, "en")

    if target == "en" or not isinstance(text, str):
        return text

    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except:
        return text


# Configuración de la página
st.set_page_config(
    page_title="HY4RES - VIGID",
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


@st.cache_data(show_spinner=False)
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    return GoogleTranslator(source="auto", target=target_lang).translate(text)

# ======================================
# Column name mapping for UI (Streamlit)
# ======================================
COLUMN_RENAME_MAP = {
    "SelfConsumption": "Self Consumption",
    "ImportfromGrid": "Import from Grid",
    "ExportToGrid": "Export to Grid",
    "Demand": "Demand",
    "Production": "Production",
    "Datetime": "Date"
}

def rename_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Rename internal column names for Streamlit display only."""
    return df.rename(columns=COLUMN_RENAME_MAP)


class EnergySurplusApp:

    def __init__(self):
        # Servicio centralizado de datos
        self.energy_data_service = EnergyDataService()

    def run(self):
        # --------------------------
        # Handle pending navigation
        # --------------------------
        if "pending_page" in st.session_state:
            st.session_state.page_selector = st.session_state.pending_page
            del st.session_state.pending_page

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
        if page == "Introduction":
            self.page_intro()
        elif page == "Energy Performance":
            self.page_energy_surplus()
        elif page == "Life Cycle Impact":
            self.page_environmental_indicators()
        elif page == "Optimization":
            self.page_optimization()

        # ==========================
        # FOOTER — ALWAYS AT BOTTOM
        # ==========================
        st.markdown("---")
        col_logo, col_text = st.columns([3, 7])

        with col_logo:
            st.image("figure/Interreg-HY4RES-transparent.png", width=1600)

        with col_text:
            st.markdown(
                """
                <div style="font-size:15px; line-height:1.6; color:#6c757d;">
                    This research platform was supported and funded by 
                    <strong>HY4RES – Hybrid Solutions for Renewable Energy Systems: 
                    Achieving Net-Zero Atlantic Area Energy Consumers and Communities</strong> 
                    (grant number <strong>EAPA_0001/2022</strong>), under the Interreg Atlantic Area Programme, 
                    co-funded by the European Union.
                </div>

                <div style="font-size:15px; line-height:1.55; color:#8a8a8a; margin-top:8px;">
                    The information and views set out on this website are those of the author(s) 
                    and do not necessarily reflect the official opinion of the European Union. 
                    Neither the European Union institutions and bodies nor any person acting on their behalf 
                    may be held responsible for the use which may be made of the information contained therein.
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------
    # Introduction Page
    # --------------------------
    def page_intro(self):
        """Render the introduction page by calling the IntroPage class."""
        intro = IntroPage()
        intro.render()

    # --------------------------
    # Energy Surplus Page
    # --------------------------
    def page_energy_surplus(self):
        # ======================================================
        # Obtener surplus desde el servicio compartido
        # ======================================================
        surplus = self.energy_data_service.get_surplus_calculator()
        result_df = surplus.result.copy()

        # ======================================================
        # Tabla diaria inicial
        # ======================================================
        df_daily_full = self.energy_data_service.get_daily_full()
        min_date = result_df['Datetime'].min().date()
        max_date = result_df['Datetime'].max().date()

        # ======================================================
        # Controles temporales
        # ======================================================
        # time_controls = TimeControlPanel(df_daily_full)
        # selected_date, time_horizon_days, mode = time_controls.render()
        selected_date = st.session_state.selected_date
        time_horizon_days = st.session_state.time_horizon_days
        mode = st.session_state.time_resolution

        if mode == 'hourly':
            hours = time_horizon_days * 24
            df_plot = surplus.get_last_hours_from(
                selected_date,
                hours=hours
            )
        else:
            df_plot = surplus.get_daily_aggregated_from(
                selected_date,
                days=time_horizon_days
            )

        table_df = rename_for_display(df_plot.copy())

        # ======================================================
        # Resumen energético (pie charts)
        # ======================================================
        summary = EnergySummary(
            df=df_plot,
            mode=mode,
            title="ENERGY PERFORMANCE SUMMARY",
            time_horizon_days=time_horizon_days,
            selected_date=selected_date
        )
        summary.show_summary()

        st.markdown("---")

        # ======================================================
        # Título
        # ======================================================
        st.markdown(
            "<h2 style='text-align:center'>ENERGY SURPLUS</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h3 style='text-align:center'>{mode} forecast from "
            f"{selected_date} up to {time_horizon_days}-day ahead</h3>",
            unsafe_allow_html=True
        )

        # ======================================================
        # Tabla + descarga CSV con encabezado PV Solar Production
        # ======================================================
        # Crear MultiHeader PV Solar Production
        df_multiheader = add_pv_multiheader(table_df.copy())

        # Crear DataDisplay con el DataFrame modificado
        table_display = DataDisplay(
            df=df_multiheader,
            mode=mode
        )

        # Mostrar tabla con descarga CSV
        table_display.show_table_with_download(
            filename=f"energy_surplus_{mode}.csv",
            height=220
        )

        # ======================================================
        # Selector de trazas
        # ======================================================
        options_internal = [
            'SelfConsumption',
            'ImportfromGrid',
            'ExportToGrid',
            'Demand',
            'Production'
        ]

        options_display = [COLUMN_RENAME_MAP.get(o, o) for o in options_internal]

        selected_display = st.multiselect(
            "Select which energy traces to display:",
            options=options_display,
            default=options_display
        )

        # Convert back to internal names
        selected_options = [
            k for k, v in COLUMN_RENAME_MAP.items()
            if v in selected_display
        ]

        # ======================================================
        # Gráfico combinado
        # ======================================================
        plotter = LastDateEnergyPlotter(
            df_plot,
            mode=mode
        )

        if selected_options:
            combined_fig = plotter.plot_combined_with_selection(
                selected_options
            )
            st.plotly_chart(
                combined_fig,
                use_container_width=True
            )
        else:
            st.info("Select at least one trace to display.")

        # ======================================================
        # Gráficos individuales
        # ======================================================
        figs = plotter.plot_all()

        col1, col2 = st.columns(2)

        with col1:
            DataDisplay(
                plotly_fig=figs['DemandVsProduction']
            ).show_with_download(
                filename="energy_demand_vs_production"
            )

            DataDisplay(
                plotly_fig=figs['ExportToGrid']
            ).show_with_download(
                filename="export_to_grid"
            )

        with col2:
            DataDisplay(
                plotly_fig=figs['SelfConsumption']
            ).show_with_download(
                filename="self_consumption"
            )

            DataDisplay(
                plotly_fig=figs['ImportfromGrid']
            ).show_with_download(
                filename="import_from_grid"
            )

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
        # st.header("Environmental Indicators (Daily)")

        # 1️⃣ Obtener rango de fechas y horizonte desde el panel
        daily_full = self.energy_data_service.get_daily_full()
        selected_date = st.session_state.selected_date
        time_horizon_days = st.session_state.time_horizon_days

        # Force daily for LCI
        mode = "daily"
        st.session_state.time_resolution = mode

        # time_controls = TimeControlPanel(daily_full, force_daily=True)  # 🔹 Forzamos daily
        # selected_date, time_horizon_days, _ = time_controls.render()

        df_daily_energy = self.energy_data_service.get_daily_filtered(
            start_date=selected_date,
            days=time_horizon_days
        )

        # 2️⃣ Inicializar EI service con los días seleccionados
        ei_service = EnvironmentalIndicatorsService(
            df_daily_energy=df_daily_energy,
            csv_mix_grid=str(self.energy_data_service.grid_mix_path)
        )

        # Calcular tablas
        indicators = [
            {"energy_source": "Hydropower_kWh", "GWP100": 0.004345569, "ADP_fossil": 0.041796964,
             "ADP_elements": 1.92e-08, "UDP": 0.002012897},
            {"energy_source": "Nuclear_kWh", "GWP100": 0.006867669, "ADP_fossil": 13.22250307, "ADP_elements": 1.22e-07,
             "UDP": 0.132012697},
            {"energy_source": "Coal_kWh", "GWP100": 1.162411024, "ADP_fossil": 11.50390196, "ADP_elements": 2.53e-07,
             "UDP": 0.080646243},
            {"energy_source": "Combined Cycle_kWh", "GWP100": 0.542820929, "ADP_fossil": 8.762179906,
             "ADP_elements": 3.96e-07, "UDP": 0.038174794},
            {"energy_source": "Wind Power_kWh", "GWP100": 0.014954465, "ADP_fossil": 0.189552053,
             "ADP_elements": 4.37e-07, "UDP": 0.006437735},
            {"energy_source": "PV Solar Power_kWh", "GWP100": 0.04708697, "ADP_fossil": 0.675875675,
             "ADP_elements": 3.07E-07, "UDP": 0.009741405},
            {"energy_source": "Thermal Solar Power_kWh", "GWP100": 0.053462332, "ADP_fossil": 0.7623678,
             "ADP_elements": 4.51E-07, "UDP": 0.010223263},
            {"energy_source": "Cogeneration_kWh", "GWP100": 0.05309101, "ADP_fossil": 0.62826523674379,
             "ADP_elements": 1.55E-07, "UDP": 0.050522554206717},
            {"energy_source": "Fuel + Gas_kWh", "GWP100": 0.922840552, "ADP_fossil": 10.92181924,
             "ADP_elements": 1.85E-07, "UDP": 0.054939536},
        ]
        tables = ei_service.calculate_daily_EI_tables(indicators=indicators,
                                                      start_date=selected_date,
                                                      days=time_horizon_days)

        st.markdown("<h1 style='text-align:center'>Life Cycle Impact (LCI)</h1>",
                    unsafe_allow_html=True)
        # st.markdown("---")

        # ==================================================
        # GOAL AND SCOPE
        # ==================================================
        with st.expander("Phase 1) Goal & Scope - ISO 14040 Principles & Framework", expanded=False):
            st.markdown(
                "<h1 style='text-align:center'>Goal & Scope - ISO 14040 Principles & Framework</h1>",
                unsafe_allow_html=True
            )

            # Goal
            st.markdown("<h2>Goal</h2>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="
                    background-color:#2f3e46;
                    padding:18px;
                    border-radius:14px;
                    color:white;
                    box-shadow:0 4px 10px rgba(0,0,0,0.18);
                    line-height:1.6
                ">
                The goal of this LCA study is to provide competent authorities of the 
                <strong>Comunidad de Regantes del Valle Inferior del Guadalquivir (Seville, Spain)</strong> 
                with information on the environmental impacts associated with electricity generation 
                and consumption in the study area.  
        
                This includes:
                <ul>
                    <li>Photovoltaic solar energy for self-consumption (6,000 kWp plant)</li>
                    <li>Export of surplus electricity to the grid</li>
                    <li>Electricity consumption from the conventional grid</li>
                </ul>
        
                The results may be used in comparative assertions regarding the environmental 
                performance of different energy scenarios, intended for public disclosure.  
        
                The primary objective is to support decision-making for optimizing the local energy system, 
                where environmental impacts are one of the decision criteria.
                </div>
                """,
                unsafe_allow_html=True
            )

            # --------------------------------------------------
            # Scope
            # --------------------------------------------------
            st.markdown("<h2>Scope</h2>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="
                    background-color:#3d5a80;
                    padding:18px;
                    border-radius:14px;
                    color:white;
                    box-shadow:0 4px 10px rgba(0,0,0,0.18);
                    line-height:1.6
                ">
                <strong style="font-size:20px">Product system:</strong> 6,000 kWp photovoltaic solar plant in the 
                Comunidad de Regantes del Valle Inferior del Guadalquivir (Seville, Spain).<br><br>
        
                <div style="margin:0; padding:0;">
                  <strong style="font-size:20px; display:block; margin-bottom:0;">Functions of the system:</strong>
                  <ul style="list-style-position: inside; margin:0; padding:0;">
                    <li style="margin:0; padding:0;">Provide electricity for self-consumption</li>
                    <li style="margin:0; padding:0;">Export surplus electricity to the grid</li>
                    <li style="margin:0; padding:0;">Supply electricity from the conventional grid when needed</li>
                  </ul>
                </div><br>
        
                <strong style="font-size:20px">Functional unit:</strong> 1 kWh of electricity delivered to the system.<br>
        
                <strong style="font-size:20px">System boundary:</strong> Cradle-to-use, operational phase only (self-consumption, export, grid usage).<br>
        
                <div style="margin:0; padding:0;">
                  <strong style="font-size:20px; display:block; margin-bottom:0;">Impact categories:</strong>
                  <ul style="list-style-position: inside; margin:0; padding:0;">
                    <li>Global Warming Potential (GWP100)</li>
                    <li>Abiotic Depletion Potential - Fossil Fuels (ADP_fossil)</li>
                    <li>Abiotic Depletion Potential - Elements (ADP_elements)</li>
                    <li>User Deprivation Potential (UDP)</li>
                </ul>
                </div><br>
                
                <strong style="font-size:20px">Methodology:</strong> Environmental Footprint (EF v3.1) with Ecoinvent v3.11 database.<br>
        
                <strong style="font-size:20px">Data requirements:</strong> Hourly electricity generation and consumption data converted to daily totals. For grid electricity, the daily contribution of each energy source was derived from the Red Eléctrica de España data.<br>
        
                <strong style="font-size:20px">Assumptions & Limitations:</strong> Only the operational phase is analyzed (daily, 3-day, or 7-day periods); upstream and end-of-life stages are excluded; data are representative of the system and study area.<br>
        
                </div>
                """,
                unsafe_allow_html=True
            )
        # st.markdown("---")

        # ==================================================
        # LIFE CYCLE INVENTORY ANALYSIS (LCI)
        # ==================================================
        with st.expander("Phase 2) Life Cycle Inventory (LCI) Analysis - ISO 14040 Principles & Framework", expanded=False):
            st.markdown(
                "<h1 style='text-align:center'>Life Cycle Inventory (LCI) Analysis - ISO 14040 Principles & Framework</h1>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="
                    background-color:#2f3e46;
                    padding:20px;
                    border-radius:14px;
                    color:white;
                    box-shadow:0 4px 10px rgba(0,0,0,0.18);
                    line-height:1.6
                ">
                
                  <div style="margin:0; padding:0;">
                  <strong style="font-size:20px; display:block; margin-bottom:0;">Impact Categories:</strong>
                  <ul style="list-style-position: inside; margin:0; padding:0;">
                      <li style="margin:0; padding:0;">Global Warming Potential (GWP100): Contribution to climate change (kg CO2-Eq).</li>
                      <li style="margin:0; padding:0;">Abiotic Depletion Potential - Fossil Fuels (ADP\_fossil): Depletion of fossil resources (MJ).</li>
                      <li style="margin:0; padding:0;">Abiotic Depletion Potential - Elements (ADP\_elements): Scarcity of critical minerals (kg Sb-Eq).</li>
                      <li style="margin:0; padding:0;">User Deprivation Potential (UDP): Freshwater consumption (m³ world Eq deprived).</li>
                  </ul>
                  </div><br>
        
                  <div style="margin:0; padding:0;">
                  <strong style="font-size:20px; display:block; margin-bottom:0;">Methodology:</strong>
                  <ul style="list-style-position: inside; margin:0; padding:0;">
                      <li style="margin:0; padding:0;">Environmental Footprint (EF v3.1) with Ecoinvent v3.11 database.</li>
                      <li style="margin:0; padding:0;">Daily grid mix fractions derived from Red Eléctrica de España data.</li>
                  </ul>
                  </div><br>
        
                  <div style="margin:0; padding:0;">
                  <strong style="font-size:20px; display:block; margin-bottom:0;">Interpretation:</strong>
                  <ul style="list-style-position: inside; margin:0; padding:0;">
                      <li style="margin:0; padding:0;">Values greater than 100% indicate avoided impacts exceed generated impacts.</li>
                      <li style="margin:0; padding:0;">Negative values represent a net environmental benefit.</li>
                      <li style="margin:0; padding:0;">Reference scenario (Grid-only): All electricity demand is supplied exclusively by the electrical grid.
                        This scenario represents the baseline environmental impact (100%) used
                        for normalization.</li>
                      <li style="margin:0; padding:0;">Self Consumption: Environmental impact associated with on-site photovoltaic electricity
                generation that is directly consumed by the system.</li>
                      <li style="margin:0; padding:0;">Import from Grid: Residual environmental impact caused when on-site solar generation is
                insufficient and electricity must be imported from the grid.</li>
                      <li style="margin:0; padding:0;">Export to Grid (Environmental Savings): Avoided environmental impact due to surplus photovoltaic electricity
                exported to the grid, displacing conventional electricity generation.
                This value represents an environmental benefit.</li>
                      <li style="margin:0; padding:0;">Net Environmental Impact: The overall environmental footprint of the system, accounting for both
                consumed impacts and avoided impacts. Values below 100% indicate an
                improvement compared to the grid-only reference scenario.</li>
                      
                  </ul>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # --------------------------------------------------
            # BUTTON TO VIEW LCIA RESULTS
            # --------------------------------------------------
            st.markdown(
                """
                <style>
                .lcia-button > button {
                    background-color: #71C8FF;  /* solid blue */
                    color: white;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 18px;
                    padding: 14px 32px;
                    border-radius: 12px;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.25);
                    cursor: pointer;
                    border: none;
                    transition: all 0.25s ease-in-out;
                }
        
                .lcia-button > button:hover {
                    background-color: #71C8FF;  /* lighter blue on hover */
                    transform: translateY(-2px);
                    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div style="text-align: center; margin: 20px 0;" class="lcia-button">
                """,
                unsafe_allow_html=True
            )
            if st.button(t("🔎 VIEW LIFE CYCLE IMPACT ASSESSMENT RESULTS")):
                st.session_state.pending_page = "Impact Assessment"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        # st.markdown("---")

        # ==================================================
        # IMPACT ASSESSMENT DASHBOARD
        # ==================================================
        with st.expander("Phase 3) Impact Assessment - ISO 14040 Principles & Framework", expanded=False):
            st.markdown(
                f"<h1 style='text-align:center'>Impact Assessment - ISO 14040 Principles & Framework</h1>",
                unsafe_allow_html=True
            )
            # --------------------------------------------------
            # DETAILED DAILY TABLES
            # --------------------------------------------------
            metrics_info = {
                "GWP100": "kg CO2-Eq.",
                "ADP_fossil": "MJ, net calorific value",
                "ADP_elements": "kg Sb-Eq",
                "UDP": "m3 world Eq deprived"
            }

            titles = {
                "GWP100": "Climate Change: Global Warming Potential (GWP100)",
                "ADP_fossil": "Energy resources, Non-renewable: Abiotic Depletion Potential (Fossil Fuels)",
                "ADP_elements": "Material resources, Metals/minerals: Abiotic Depletion Potential (Elements)",
                "UDP": "Water use: User Deprivation Potential (UDP)"
            }
            # st.header("Detailed Daily Environmental Indicator Results")
            for metric, table in tables.items():
                title = titles.get(metric, metric)
                unit = metrics_info.get(metric, "")

                # Mostrar título centrado
                st.markdown(
                    f"<h3 style='text-align:center'>{title} – {unit}</h3>",
                    unsafe_allow_html=True
                )

                # --------------------------
                # Crear MultiIndex si existen columnas PV
                # --------------------------
                pv_cols = {"Self Consumption", "Export to Grid"}
                if pv_cols.issubset(table.columns):
                    table = add_pv_multiheader(table.copy())  # ahora fila superior PV Solar Production
                # --------------------------
                # Crear Styler
                # --------------------------
                styler = table.style

                # Centrar headers de todos los niveles
                styler = styler.set_table_styles([
                    {"selector": "th.col_heading.level0", "props": [("text-align", "center")]},
                    {"selector": "th.col_heading.level1", "props": [("text-align", "center")]}
                ])

                # --------------------------
                # Formato de números
                # --------------------------
                # Detect last column (Net Impact)
                net_col = table.columns[-1]

                # Detectar columnas numéricas para formatear
                if isinstance(table.columns, pd.MultiIndex):
                    # Nivel 1 contiene los nombres originales
                    numeric_cols = [col for col in table.select_dtypes(include="number").columns]
                else:
                    numeric_cols = [col for col in table.select_dtypes(include="number").columns if col != "Date"]

                # Aplicar formato
                if metric == "ADP_elements":
                    styled_table = styler.format({col: "{:.1e}" for col in numeric_cols})
                else:
                    styled_table = styler.format({col: "{:.1f}" for col in numeric_cols})

                # --------------------------
                # Colorear Net Impact
                # --------------------------
                # Para MultiIndex usamos solo el segundo nivel del Net Impact
                if isinstance(table.columns, pd.MultiIndex):
                    net_col_multi = [col for col in table.columns if col[1] == "Net Impact"]
                    if net_col_multi:
                        styler = styler.applymap(color_net_impact, subset=net_col_multi)
                else:
                    styler = styler.applymap(color_net_impact, subset=[net_col])

                # --------------------------
                # Mostrar en Streamlit
                # --------------------------
                st.dataframe(styler, hide_index=True)

            # Calculate grid reference impacts
            grid_reference_impacts = ei_service.calculate_grid_reference_impacts(indicators=indicators)

            # Pass grid_reference_impacts to ImpactAssessment
            dashboard = ImpactAssessment(
                df_tables=tables,  # Tables of environmental indicators
                energy_tables=df_daily_energy,  # Energy tables
                grid_reference_impacts=grid_reference_impacts,  # Pass the calculated impacts
                time_horizon_days=time_horizon_days,
                selected_date=selected_date
            )
            dashboard.show_dashboard()
        # st.markdown("---")

        # ==================================================
        # FINAL INTERPRETATION BLOCK (GLOBAL & CONCEPTUAL)
        # ==================================================
        df_raw_impacts = dashboard.df_raw_impacts
        df_calculation_results = dashboard.df_calculation_results

        with st.expander(
                "Phase 4) Interpretation of Results - ISO 14044 Requirements & Guidelines",
                expanded=True
        ):
            st.markdown(
                "<h1 style='text-align:center'>Interpretation of Results - ISO 14044 Requirements & Guidelines</h1>",
                unsafe_allow_html=True
            )

            # --------------------------------------------------
            # Generar texto corrido de interpretación usando los DataFrames
            # --------------------------------------------------
            interpretation_text = f"""
            <div style="
                background-color:#2f3e46;
                padding:20px;
                border-radius:16px;
                color:white;
                box-shadow:0 4px 10px rgba(0,0,0,0.18);
                line-height:1.6;
                font-size:18px;
            ">
            <strong>Analysis period:</strong> {st.session_state.time_horizon_days} days, starting from <strong>{st.session_state.selected_date}</strong>. 
            Negative net impact values indicate an <strong style="color:#6AA84F;">environmental benefit</strong>, meaning that photovoltaic (PV) electricity exported to the grid helps reduce overall environmental burden.<br><br>
            """

            for _, row in df_raw_impacts.iterrows():
                indicator_name = row["Indicator"]

                # Buscar unidad en EI_METADATA
                meta = next((v for k, v in EI_METADATA.items() if v["name"] == indicator_name), None)
                unit = meta["unit"] if meta else row.get("Units", "")

                self_val = row.get("Self Consumption", 0)
                export_val = row.get("Export to Grid", 0)
                grid_val = row.get("Import from Grid", 0)
                net_val = row.get("Net Impact", 0)
                reference_val = row.get("Reference Impact (Grid-Only)", 0)

                calc_row = df_calculation_results[
                    df_calculation_results["Indicator"] == indicator_name
                    ]

                avoided_pct = calc_row["Relative Environmental Avoided of PV Grid Export (%)"].values[
                    0] if not calc_row.empty else 0
                net_pct = calc_row["Net Environmental Impact (%)"].values[0] if not calc_row.empty else 0

                # Colores según signo (beneficio vs impacto)
                # Función color valores normales
                def color_val(val):
                    color = "#6AA84F" if val < 0 else "#D22C41"
                    return f"<span style='color:{color}; font-weight:bold'>{val:.2f}</span>"

                # Export siempre verde
                def color_export(val):
                    return f"<span style='color:#6AA84F; font-weight:bold'>{val:.2f}</span>"

                # Color Avoided Impact (%) — beneficio si > 0
                def color_avoided_pct(val):
                    color = "#6AA84F" if val > 0 else "#D22C41"
                    return f"<span style='color:{color}; font-weight:bold'>{val:.1f}%</span>"

                # Color Net Impact (%) — beneficio si <100 o <0
                def color_net_pct(val):
                    if val < 0:
                        color = "#6AA84F"  # beneficio neto fuerte
                    elif val <= 100:
                        color = "#6AA84F"  # mejor que solo red
                    else:
                        color = "#D22C41"  # peor que solo red
                    return f"<span style='color:{color}; font-weight:bold'>{val:.1f}%</span>"

                interpretation_text += (
                    f"<div style='margin-left:18px; margin-bottom:10px;'>"
                    f"- <strong>{indicator_name}</strong>: "
                    f"Total self-consumed PV impact = {color_val(self_val)} {unit}, "
                    f"exported PV impact = {color_export(export_val)} {unit}, "
                    f"imported from grid = {color_val(grid_val)} {unit}, "
                    f"resulting in a net environmental impact of {color_val(net_val)} {unit} "
                    f"compared to a grid-only reference impact of {color_val(reference_val)} {unit}. "
                    f"This corresponds to {color_avoided_pct(avoided_pct)} "
                    f"<strong>Relative Environmental Avoided of PV Grid Export (%)</strong>, meaning the environmental impact avoided thanks to PV export, "
                    f"and {color_net_pct(net_pct)} "
                    f"<strong>Net Environmental Impact (%)</strong>, representing the total system impact relative to the conventional grid scenario.<br>"
                    f"</div>"
                )

            interpretation_text += (
                "<br><strong>Interpretation for general audiences:</strong> "
                "Percentage values above 0% indicate environmental savings. "
                "Values above 100% mean the PV system avoids more environmental impact than the grid would have produced. "
                "A negative Net Environmental Impact (%) means the solar installation delivers a net environmental benefit by offsetting more impact than it generates."
                "</div>"
            )

            st.markdown(interpretation_text, unsafe_allow_html=True)

        # st.markdown("---")



# --------------------------
# Run App
# --------------------------

if __name__ == "__main__":
    app = EnergySurplusApp()
    app.run()

    # streamlit cache clear
    # cd C:\Users\Win\PycharmProjects\IntegrationOfModels\Streamlit
    # streamlit run app.py

