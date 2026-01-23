import numpy as np
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

EI_METADATA = {
    "GWP100": {
        "title": "Global Warming Potential (GWP100)",
        "impact_category": "Climate Change",
        "unit": "kg CO₂-Eq",
        "description": (
            "Measures the contribution to climate change by quantifying "
            "greenhouse gas emissions over a 100-year horizon, expressed as "
            "CO₂ equivalents."
        )
    },
    "ADP_fossil": {
        "title": "Abiotic Depletion Potential – Fossil Fuels",
        "impact_category": "Energy resources: non-renewable",
        "unit": "MJ (net calorific value)",
        "description": (
            "Represents the depletion of non-renewable fossil energy resources "
            "caused by energy consumption."
        )
    },
    "ADP_elements": {
        "title": "Abiotic Depletion Potential – Elements",
        "impact_category": "Material resources: metals/minerals",
        "unit": "kg Sb-Eq",
        "description": (
            "Quantifies the depletion of mineral and metal resources based on "
            "their ultimate reserves. Values are typically very small but "
            "environmentally significant."
        )
    },
    "UDP": {
        "title": "User Deprivation Potential (UDP)",
        "impact_category": "Water use",
        "unit": "m³ world Eq deprived",
        "description": (
            "Measures freshwater consumption weighted by regional water scarcity, "
            "reflecting potential deprivation of water users worldwide."
        )
    }
}

class ImpactAssessment:
    def __init__(self, df_tables: dict, energy_tables: dict, grid_reference_impacts: dict, time_horizon_days=7, selected_date="2026-01-19"):
        self.df_tables = df_tables
        self.df_daily_energy = energy_tables
        self.grid_reference_impacts = grid_reference_impacts  # Initialize grid_reference_impacts
        self.time_horizon_days = time_horizon_days
        self.selected_date = selected_date
        self.colors = {
            "Self": "#6AA84F",
            "Grid": "#D22C41",
            "Export": "#2078FF",
            "Balance": "#AA4BFF"
        }

    def show_dashboard(self):

        # ==================================================
        # 1. OVERALL ENVIRONMENTAL BALANCE
        # ==================================================
        st.markdown(
            "<h2 style='text-align:center'>Overall Environmental Total</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align:center'>Total {self.time_horizon_days}-day cumulative since {self.selected_date}</h3>",
            unsafe_allow_html=True
        )

        balances, indicator_names, units = [], [], []

        # --- Calculamos balance total por indicador ---
        for name, table in self.df_tables.items():
            col_balance = table.columns[4]
            unit = col_balance.split("(")[-1].replace(")", "")
            balance_total = table.iloc[:, 4].sum()
            balances.append(balance_total)
            indicator_names.append(name)
            units.append(unit)

        # --- Barra global por indicador ---
        fig = go.Figure(go.Bar(
            x=indicator_names,
            y=balances,
            marker_color=self.colors["Balance"]
        ))
        fig.update_layout(
            yaxis_title="Value",
            xaxis_title="Environmental Indicator",
            template="plotly_white"
        )

        col_chart, col_info = st.columns([3, 1])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)

            cols = st.columns(len(indicator_names))
            for col, name, value, unit in zip(cols, indicator_names, balances, units):
                formatted = f"{value:.2e}" if abs(value) < 0.01 else f"{value:.2f}"
                col.markdown(
                    f"""
                    <div style="background-color:{self.colors['Balance']};
                                padding:14px;
                                border-radius:12px;
                                text-align:center;
                                color:white">
                        <strong>{name}</strong><br>
                        <span style="font-size:22px;font-weight:bold">{formatted}</span><br>
                        <small>{unit}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_info:
            st.markdown("<h3 style='text-align:center'>Model Information</h3>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="background-color:#2f3e46;
                            padding:18px;
                            border-radius:14px;
                            color:white">
                <strong>Method:</strong> EF v3.1<br><br>
                <strong>Database:</strong> Ecoinvent v3.11<br><br>
                <strong>Functional Unit:</strong><br>
                1 kWh of electricity generated
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==================================================
        # 3. SUMMARY (INDICATOR SELECTION BELOW TITLE)
        # ==================================================
        st.markdown("")
        st.markdown(f"<h2 style='text-align:center'>Detailed Environmental Indicator Results</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='text-align:center'>{self.time_horizon_days}-day cumulative total from {self.selected_date}</h3>",
            unsafe_allow_html=True
        )
        selected_indicator = st.selectbox(
            "Select environmental indicator",
            list(self.df_tables.keys())
        )

        summary = Summary(
            {selected_indicator: self.df_tables[selected_indicator]},
            self.time_horizon_days,
            self.selected_date
        )
        summary.show_summary()

        # ==================================================
        # First Table: Raw Impacts
        raw_impacts = []
        for indicator, table in self.df_tables.items():
            self_impact = table.iloc[:, 2].sum()
            grid_impact = table.iloc[:, 1].sum()
            export_impact = table.iloc[:, 3].sum()
            balance_impact = self_impact + grid_impact + export_impact
            reference_impact = self.grid_reference_impacts.get(indicator, 0)

            raw_impacts.append({
                "Indicator": indicator,
                "Reference Impact (Grid-Only)": reference_impact,
                "Self-Consumption Impact": self_impact,
                "Grid Impact": grid_impact,
                "Export Impact": export_impact,
                "Total Impact": balance_impact
            })

        df_raw_impacts = pd.DataFrame(raw_impacts)
        df_raw_impacts['Units'] = df_raw_impacts['Indicator'].map(
            lambda x: f"{EI_METADATA.get(x, {}).get('unit', '')}")

        st.markdown("<h2 style='text-align:center'>Raw Environmental Impacts</h2>", unsafe_allow_html=True)
        st.dataframe(df_raw_impacts.style.format({
            "Reference Impact (Grid-Only)": "{:.2f}",
            "Self-Consumption Impact": "{:.2f}",
            "Grid Impact": "{:.2f}",
            "Export Impact": "{:.2f}",
            "Total Impact": "{:.2f}"
        }))

        # ==================================================
        # Second Table: Ratio based on 1 kWh
        # Fix Datetime column name if needed
        self.df_daily_energy.columns = self.df_daily_energy.columns.str.strip()

        if "Datetime" not in self.df_daily_energy.columns:
            raise KeyError("'Datetime' column not found in df_daily_energy")

        # Prepare energy data
        energy_data = self.df_daily_energy[[
            "Datetime", "SelfConsumption", "GridConsumption", "ExportToGrid"
        ]].copy()

        energy_data = energy_data.rename(columns={"Datetime": "Date"})
        energy_data["Date"] = pd.to_datetime(energy_data["Date"], errors="coerce")
        energy_data = energy_data.dropna(subset=["Date"])

        # Calcular totales de kWh para cada caso
        total_self = energy_data["SelfConsumption"].sum()
        total_grid = energy_data["GridConsumption"].sum()
        total_export = energy_data["ExportToGrid"].sum()

        impact_ratios = []
        # Iterate over environmental indicator tables
        for indicator, table in self.df_tables.items():

            # Ensure Date exists
            if "Date" not in table.columns:
                table = table.reset_index()

            table["Date"] = pd.to_datetime(table["Date"], errors="coerce")
            table = table.dropna(subset=["Date"])

            # Extraer los impactos totales directamente de la tabla
            total_self_impact = table.iloc[:, 2].sum()  # Columna de SelfConsumption Impact
            total_grid_impact = table.iloc[:, 1].sum()  # Columna de GridConsumption Impact
            total_export_impact = table.iloc[:, 3].sum()  # Columna de ExportToGrid Impact

            # Calcular los factores dividiendo el impacto total entre la energía total consumida
            self_factor = total_self_impact / total_self if total_self > 0 else np.nan
            grid_factor = total_grid_impact / total_grid if total_grid > 0 else np.nan
            export_factor = total_export_impact / total_export if total_export > 0 else np.nan

            # Almacenar los factores en la lista
            impact_ratios.append({
                "Indicator": indicator,
                "Self Impact per kWh": self_factor,
                "Grid Impact per kWh": grid_factor,
                "Export Impact per kWh": export_factor,
            })

        # Crear un DataFrame con los factores de impacto
        df_impact_ratios = pd.DataFrame(impact_ratios)

        # Agregar la columna 'Unit' con la unidad de cada indicador
        df_impact_ratios['Unit'] = df_impact_ratios['Indicator'].map(
            lambda x: f"{EI_METADATA.get(x, {}).get('unit', '')} / 1 kWh"
        )

        # Identificar la fila de 'ADP_elements'
        adp_elements_mask = df_impact_ratios['Indicator'] == 'ADP_elements'

        # Guardar los valores originales de 'ADP_elements' para formatearlos después
        adp_elements_values = df_impact_ratios.loc[adp_elements_mask, [
            'Self Impact per kWh', 'Grid Impact per kWh', 'Export Impact per kWh'
        ]].copy()

        # Mostrar la tabla con los valores formateados de 'ADP_elements'
        st.markdown("<h2 style='text-align:center'>Impact Factors per 1 kWh</h2>", unsafe_allow_html=True)

        # Formatear las demás filas con un máximo de 10 decimales
        df_impact_ratios.loc[~adp_elements_mask, [
            'Self Impact per kWh', 'Grid Impact per kWh', 'Export Impact per kWh'
        ]] = df_impact_ratios.loc[~adp_elements_mask, [
            'Self Impact per kWh', 'Grid Impact per kWh', 'Export Impact per kWh'
        ]].astype(float).applymap(lambda x: round(x, 7))

        # Aplicar el formato general al resto del DataFrame
        st.dataframe(
            df_impact_ratios.style.format({
                "Self Impact per kWh": "{:.6f}",
                "Grid Impact per kWh": "{:.6f}",
                "Export Impact per kWh": "{:.6f}"}))

        # Formatear los valores de 'ADP_elements' en notación científica
        df_impact_ratios.loc[adp_elements_mask, [
            'Self Impact per kWh', 'Grid Impact per kWh', 'Export Impact per kWh'
        ]] = adp_elements_values.astype(float).applymap(lambda x: f"{x:.2e}")

        # ==================================================
        # Third Table: Calculation Results
        calculation_results = []
        for indicator, table in self.df_tables.items():
            impact_reference = self.grid_reference_impacts.get(indicator, 0)
            impact_balance = table.iloc[:, 4].sum()

            avoided_pct = (
                abs(table.iloc[:, 3].sum()) / impact_reference * 100
                if impact_reference != 0 else 0
            )
            net_pct = (
                impact_balance / impact_reference * 100
                if impact_reference != 0 else 0
            )
            net_pct_num = (
                impact_reference - impact_balance
                if impact_reference != 0 else 0
            )

            calculation_results.append({
                "Indicator": indicator,
                "Relative Environmental Avoided of PV Grid Export (%)": avoided_pct,
                "Net Environmental Impact (%)": net_pct,
                f"Net Environmental Impact Avoided (PV Installation)": net_pct_num
            })

        df_calculation_results = pd.DataFrame(calculation_results)
        df_calculation_results['Units'] = df_calculation_results['Indicator'].map(
            lambda x: f"{EI_METADATA.get(x, {}).get('unit', '')}")

        st.markdown("<h2 style='text-align:center'>Results Comparative calculations with the Reference Impact</h2>", unsafe_allow_html=True)
        st.dataframe(df_calculation_results.style.format({
            "Relative Environmental Avoided of PV Grid Export (%)": "{:.1f}",
            "Net Environmental Impact (%)": "{:.1f}",
            "Net Environmental Impact Avoided (PV Installation)": "{:.2f}"
        }))
        # st.write("### Notes on Interpretation")
        st.markdown(r"""
            - Percentages **greater than 100 %** indicate that the system avoids more environmental impact than it generates under the grid-only reference scenario.
            - Negative values of **Net Environmental Impact** indicate a **net environmental benefit**.
            - These indicators are **interpretative metrics** and are therefore presented within the **Interpretation phase**, in accordance with ISO 14040 and ISO 14044.
                            """
            )

        with st.expander("📘 Calculation methodology and interpretation criteria"):
            st.markdown(
                r"""
        ### Relative Environmental Avoided of PV Grid Export (%)
        
        Represents the relative environmental benefit obtained by exporting photovoltaic
        electricity to the grid, compared to a reference scenario where the same electricity
        would be supplied entirely by the conventional grid mix.
        
        $$
        \text{Impact Avoided of PV Grid Export} =
        \frac{|EI_{export}|}{EI_{grid\ only}} \times 100
        $$
        
        ---
        
        ### Net Environmental Impact (%)
        
        Represents the net environmental performance of the system after accounting for
        self-consumption, grid imports, and avoided impacts due to electricity export.
        
        $$
        \text{Net Impact} =
        \frac{EI_{total}}{EI_{grid\ only}} \times 100
        $$
        
        ---
        
        ### Net Environmental Impact Avoided (PV Installation)
        
        Represents the total environmental impact avoided through the installation of the PV solar plant.
        
        $$
        \text{Net Impact Avoided (PV Installation)} = EI_{grid\ only} - EI_{total}
        $$
        
        ---
        
        ### Environmental Impact Total
        
        The net environmental impact is calculated as:
        
        $$
        EI_{total} = EI_{self} + EI_{grid} - EI_{export}
        $$
        
        where:
        
        - $EI_{self}$: Environmental impact associated with self-consumed photovoltaic electricity
        - $EI_{grid}$: Environmental impact associated with electricity imported from the grid
        - $EI_{export}$: Avoided environmental impact due to electricity exported to the grid
        - $EI_{grid\ only}$: Reference impact assuming the total electricity demand is supplied exclusively by the grid
        
        ---
        
        ### Environmental Impact of Grid-Only Scenario ($EI_{grid\ only}$)
        
        Represents the environmental impact assuming the total electricity demand is supplied exclusively by the grid.
        
        $$
        EI_{grid\ only} = \sum \left( kWh_{reference} \times \frac{Mix_{source}}{100} \times EF_{source} \right)
        $$
        
        where:
        
        - $kWh_{reference}$: Total electricity demand (self-consumption + grid consumption)
        - $Mix_{source}$: Percentage contribution of each energy source in the grid mix
        - $EF_{source}$: Environmental factor for each energy source (e.g., $kg\ CO_2\text{-}Eq/kWh$)
        
        ---
        
        ### Notes on Interpretation
        
        - Percentages **greater than 100 %** indicate that the system avoids more environmental
          impact than it generates under the grid-only reference scenario.
        - Negative values of **Net Environmental Impact** indicate a **net environmental benefit**.
        - These indicators are **interpretative metrics** and are therefore presented within
          the **Interpretation phase**, in accordance with ISO 14040 and ISO 14044.
                """
            )

        st.markdown("---")

        # Mostrar los valores totales en la interfaz
        st.markdown("<h2 style='text-align:center'>***** DEBUG *****</h2>", unsafe_allow_html=True)
        st.write("Total SelfConsumption (kWh):", total_self)
        st.write("Total GridConsumption (kWh):", total_grid)
        st.write("Total ExportToGrid (kWh):", total_export)
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
        st.write("Indicators:", indicators)


class Summary:
    """
    Summary visual para todos los Indicadores Ambientales (EI):
    - Totales acumulados por tipo de consumo (Self, Grid, Export)
    - Export se muestra como ahorro (verde) para facilitar interpretación
    - Unidades incluidas junto a los valores
    """

    def __init__(self, df_tables: dict, time_horizon_days=7, selected_date="2026-01-19"):
        self.df_tables = df_tables
        self.time_horizon_days = time_horizon_days
        self.selected_date = selected_date

        # Colores adaptados a la interpretación
        self.colors = {
            "Self": "#6AA84F",     # Solar propio
            "Grid": "#D22C41",     # Red
            "Export": "#2078FF",   # Ahorro
            "Balance": "#AA4BFF"   # Balance neto
        }

        # Explicaciones de cada indicador
        self.explanations = {
            "GWP100": "Impact Category: Climate Change -> Global Warming Potential (GWP100). Contribución al cambio climático en kg CO2-Eq/kWh generado.",
            "ADP_fossil": "Impact Category: Energy resources: non-renewable -> Abiotic Depletion Potential (Fossil Fuels). Mide agotamiento de recursos fósiles (MJ net calorific value).",
            "ADP_elements": "Impact Category: Elements -> Abiotic Depletion Potential (Elements). Escasez de elementos minerales críticos (kg Sb-Eq).",
            "UDP": "Impact Category: Land & Water -> Use of freshwater (UDP). Consumo de agua dulce mundial equivalente (m3 world Eq deprived)."
        }

    def show_summary(self):
        for indicator_name, table in self.df_tables.items():
            # Extraer las unidades desde los nombres de columna
            col_self = table.columns[2]  # Self Consumption (unit)
            col_grid = table.columns[1]  # Grid Consumption (unit)
            col_export = table.columns[3]  # Export To Grid (unit)
            col_balance = table.columns[4]  # Balance (unit)

            unit_self = col_self.split('(')[-1].replace(')', '')
            unit_grid = col_grid.split('(')[-1].replace(')', '')
            unit_export = col_export.split('(')[-1].replace(')', '')
            unit_balance = col_balance.split('(')[-1].replace(')', '')

            # Totales acumulados
            total_self = table.iloc[:, 2].sum()
            total_grid = table.iloc[:, 1].sum()
            total_export = table.iloc[:, 3].sum() * -1  # Invertimos signo para mostrar como ahorro
            total_balance = total_self + total_grid - total_export  # Balance neto considerando ahorro

            # Labels y valores
            labels = ['Self Consumption 🔄', 'Grid Consumption ⬅️', 'Export to Grid ➡️']
            values = {
                "Self Consumption": total_self,  # positivo
                "Grid Consumption": total_grid,  # positivo
                "Export to Grid": -abs(total_export),  # negativo real
                "Net Balance": total_balance  # puede ser + o -
            }


            # --- Layout con dos columnas: gráfico + explicaciones ---
            col_chart, col_info = st.columns([3, 1])
            metadata = EI_METADATA.get(indicator_name, {})

            # --- Gráfico Donut y Cards ---
            with col_chart:
                st.markdown(
                    f"<h3 style='text-align:center'>Contribution Analysis</h3>",
                    unsafe_allow_html=True
                )

                categories = [
                    "Self Consumption",
                    "Grid Consumption",
                    "Export to Grid",
                    "Net Balance"
                ]

                values = [
                    total_self,
                    total_grid,
                    -abs(total_export),  # NEGATIVO
                    total_balance
                ]

                colors = [
                    self.colors["Self"],
                    self.colors["Grid"],
                    self.colors["Export"],
                    self.colors["Balance"]
                ]

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=["Self Consumption", "Grid Consumption", "Export to Grid", "Net Balance"],
                    y=[total_self, total_grid, -abs(total_export), total_balance],
                    marker_color=[
                        self.colors["Self"],
                        self.colors["Grid"],
                        self.colors["Export"],
                        self.colors["Balance"]
                    ],
                    text=[
                        f"{total_self:.2f}",
                        f"{total_grid:.2f}",
                        f"{-abs(total_export):.2f}",
                        f"{total_balance:.2f}"
                    ],
                    textposition="auto",
                    textfont=dict(
                        size=18,
                        color="white"
                    )
                ))

                fig.update_layout(
                    height=600,
                    margin=dict(l=90, r=40, t=90, b=90),
                    yaxis=dict(
                        title=f"{indicator_name} ({unit_balance})",
                        zeroline=True,
                        zerolinewidth=2,
                        zerolinecolor='black',
                        automargin=True
                    ),
                    xaxis=dict(
                        automargin=True
                    ),
                    font=dict(size=15),
                    title=dict(
                        text=f"{indicator_name} – Life Cycle Impact Assessment Results",
                        x=0.5,
                        font=dict(size=20)
                    )
                )

                # Línea de referencia en cero (MUY IMPORTANTE)
                fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")

                st.plotly_chart(
                    fig,
                    config={"responsive": True}
                )

            # --- Información a la derecha ---
            with col_info:
                st.markdown(
                    "<h3 style='text-align:center'>Indicator Information</h3>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div style="
                        background-color:#2f3e46;
                        padding:16px;
                        border-radius:12px;
                        color:white;
                        box-shadow:0 4px 8px rgba(0,0,0,0.15)
                    ">

                    <strong style="font-size:18px">
                        {metadata.get('title', '')}
                    </strong><br><br>

                    <strong>Impact Category:</strong><br>
                    {metadata.get('impact_category', '')}<br><br>

                    <strong>Indicator Unit:</strong><br>
                    {metadata.get('unit', '')}<br><br>

                    <strong>Description:</strong><br>
                    {metadata.get('description', '')}

                    </div>
                    """,
                    unsafe_allow_html=True
                )



