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
    def __init__(self, df_tables: dict, grid_reference_impacts: dict, time_horizon_days=7, selected_date="2026-01-19"):
        self.df_tables = df_tables
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
            "<h2 style='text-align:center'>Overall Environmental Balance</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align:center'>Total {self.time_horizon_days}-day cumulative balance since {self.selected_date}</h3>",
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
        #
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
                # "Balance Impact": balance_impact
            })

        df_raw_impacts = pd.DataFrame(raw_impacts)
        df_raw_impacts['Units'] = df_raw_impacts['Indicator'].map(
            lambda x: f"{EI_METADATA.get(x, {}).get('unit', '')}"
        )

        st.markdown("<h2 style='text-align:center'>Raw Environmental Impacts</h2>", unsafe_allow_html=True)
        st.dataframe(df_raw_impacts.style.format({
            "Reference Impact (Grid-Only)": "{:.2f}",
            "Self-Consumption Impact": "{:.2f}",
            "Grid Impact": "{:.2f}",
            "Export Impact": "{:.2f}",
            # "Balance Impact": "{:.2f}"
        }))

        # Second Table: Calculation Results
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

            calculation_results.append({
                "Indicator": indicator,
                "Impact Avoided (%)": avoided_pct,
                "Net Environmental Impact (%)": net_pct,
                "Net Impact (absolute)": impact_balance
            })

        df_calculation_results = pd.DataFrame(calculation_results)
        df_calculation_results['Units'] = df_calculation_results['Indicator'].map(
            lambda x: f"{EI_METADATA.get(x, {}).get('unit', '')}"
        )

        st.markdown("<h2 style='text-align:center'>Calculation Results</h2>", unsafe_allow_html=True)
        st.dataframe(df_calculation_results.style.format({
            "Impact Avoided (%)": "{:.1f}",
            "Net Environmental Impact (%)": "{:.1f}",
            "Net Impact (absolute)": "{:.2f}"
        }))
        st.markdown("---")

        with st.expander("📘 Calculation methodology and interpretation criteria"):
            st.markdown(
                r"""
        ### Environmental Impact Avoided (%)
        
        Represents the relative environmental benefit obtained by exporting photovoltaic
        electricity to the grid, compared to a reference scenario where the same electricity
        would be supplied entirely by the conventional grid mix.
        
        $$
        \text{Impact Avoided} =
        \frac{|EI_{export}|}{EI_{grid\ only}} \times 100
        $$
        
        ---
        
        ### Net Environmental Impact (%)
        
        Represents the net environmental performance of the system after accounting for
        self-consumption, grid imports, and avoided impacts due to electricity export.
        
        $$
        \text{Net Impact} =
        \frac{EI_{balance}}{EI_{grid\ only}} \times 100
        $$
        
        ---
        
        ### Environmental Impact Balance
        
        The net environmental impact is calculated as:
        
        $$
        EI_{balance} = EI_{self} + EI_{grid} + EI_{export}
        $$
        
        where:
        
        - $EI_{self}$: Environmental impact associated with self-consumed photovoltaic electricity
        - $EI_{grid}$: Environmental impact associated with electricity imported from the grid
        - $EI_{export}$: Avoided environmental impact due to electricity exported to the grid
        - $EI_{grid\ only}$: Reference impact assuming the total electricity demand is supplied exclusively by the grid
        
        ---
        
        ### Net Impact (Absolute)
        
        Represents the total environmental impact balance in absolute terms, combining all contributions.
        
        $$
        \text{Net Impact (Absolute)} = EI_{balance}
        $$
        
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



