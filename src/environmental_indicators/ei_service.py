import pandas as pd
import numpy as np

class EnvironmentalIndicatorsService:
    """
    Servicio para calcular indicadores ambientales diarios a partir
    del consumo diario y del mix de la red.
    Devuelve tablas listas para Streamlit.
    """

    def __init__(self, df_daily_energy: pd.DataFrame, csv_mix_grid: str):
        """
        df_daily_energy: DataFrame diario con columnas ['Datetime','SelfConsumption','GridConsumption','ExportToGrid']
        csv_mix_grid: CSV con porcentajes diarios de mix energético
        """
        self.df_daily_energy = df_daily_energy.copy()

        # --------------------------
        # Cargar CSV de mix
        # --------------------------
        df_mix = pd.read_csv(csv_mix_grid, sep=";")

        # --------------------------
        # Convertir porcentajes a float
        # --------------------------
        for col in df_mix.columns:
            if col != "Datetime":
                df_mix[col] = df_mix[col].replace("-", "0").str.replace(",", ".").astype(float)

        # --------------------------
        # Asegurarse de que 'Datetime' es datetime
        # --------------------------
        df_mix["Datetime"] = pd.to_datetime(df_mix["Datetime"], dayfirst=False)
        # Creamos columna solo con fecha
        df_mix["date"] = df_mix["Datetime"].dt.date
        self.df_mix_grid = df_mix

    def calculate_daily_EI_tables(self, indicators: list, start_date=None, days=7):
        """
        Calcula indicadores diarios y devuelve 4 tablas separadas (una por cada métrica):
        - GWP100 (kg CO2-Eq.)
        - ADP (FOSSIL FUELS) (MJ)
        - ADP (ELEMENTS) (kg Sb-Eq)
        - UDP (m3 world Eq deprived)

        start_date: fecha inicial (string 'YYYY-MM-DD' o datetime)
        days: horizonte en días
        """

        df = self.df_daily_energy.copy()
        df = df.sort_values("Datetime")

        # --------------------------
        # Filtrar por fechas
        # --------------------------
        if start_date is not None:
            df = df[df["Datetime"] >= pd.to_datetime(start_date)]
        df = df.head(days)

        # --------------------------
        # Merge diario usando solo la fecha
        # --------------------------
        df['date'] = df['Datetime'].dt.date
        df_mix = self.df_mix_grid.copy()
        df = df.merge(df_mix.drop(columns=['Datetime']), on='date', how='left')

        # --------------------------
        # Crear columnas kWh por fuente
        # --------------------------
        for ind in indicators:
            source_col = ind["energy_source"].replace("_kWh", "")
            if source_col in df.columns:
                df[ind["energy_source"]] = df["GridConsumption"] * df[source_col] / 100.0
            else:
                df[ind["energy_source"]] = 0.0  # Si no hay columna, ponemos 0

        # --------------------------
        # Inicializar diccionario de tablas
        # --------------------------
        tables = {}
        metrics_info = {
            "GWP100": "kg CO2-Eq.",
            "ADP_fossil": "MJ, net calorific value",
            "ADP_elements": "kg Sb-Eq",
            "UDP": "m3 world Eq deprived"
        }

        for metric, unit in metrics_info.items():
            table = pd.DataFrame()
            table["Date"] = df["Datetime"].dt.date

            # GridConsumption
            total_grid = sum([
                df[ind["energy_source"]] * ind.get(metric, 0)
                for ind in indicators
                if ind.get(metric) is not None
            ])

            # SelfConsumption (solo PV Solar Power)
            pv_factor = next((i[metric] for i in indicators if i["energy_source"]=="PV Solar Power_kWh"), 0)
            total_self = df["SelfConsumption"] * pv_factor

            # ExportToGrid (negativo)
            total_export = - df["ExportToGrid"] * pv_factor

            # Balance
            total_balance = total_grid + total_self + total_export

            # Guardar columnas renombradas con unidades
            table[f"Grid Consumption ({unit})"] = total_grid
            table[f"Self Consumption ({unit})"] = total_self
            table[f"Export To Grid ({unit})"] = total_export
            table[f"Balance ({unit})"] = total_balance

            tables[metric] = table

        # Eliminamos columna auxiliar 'date'
        df.drop(columns=['date'], inplace=True)

        return tables

    # Python
    def calculate_grid_reference_impacts(self, indicators: list):
        """
        Calculate the grid reference impacts assuming all energy demand is supplied by the grid.
        Returns a dictionary with impacts for each indicator.
        """
        df = self.df_daily_energy.copy()
        df['date'] = df['Datetime'].dt.date

        # Merge with grid mix data
        df = df.merge(self.df_mix_grid.drop(columns=['Datetime']), on='date', how='left')

        # Total energy demand (kWh_reference)
        df['kWh_reference'] = df['SelfConsumption'] + df['GridConsumption']

        # Initialize dictionary for grid reference impacts
        grid_reference_impacts = {metric: 0 for metric in ["GWP100", "ADP_fossil", "ADP_elements", "UDP"]}

        # Calculate impacts for each indicator
        for metric in grid_reference_impacts.keys():
            total_impact = sum([
                df['kWh_reference'] * df[ind["energy_source"].replace("_kWh", "")] / 100.0 * ind.get(metric, 0)
                for ind in indicators if ind.get(metric) is not None
            ])
            grid_reference_impacts[metric] = total_impact.sum()

        return grid_reference_impacts