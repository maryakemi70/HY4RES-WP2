import pandas as pd

class SurplusCalculator:
    def __init__(self, demand_df, production_df):
        self.demand_df = demand_df
        self.production_df = production_df
        self.result = None

    def calculate(self):
        """Merge de demanda y producción y cálculo de SelfConsumption, GridConsumption y ExportToGrid"""
        df = self.demand_df.merge(
            self.production_df,
            on='Datetime',
            how='inner'
        )

        # Asegurarse que Datetime es tipo datetime
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df = df.sort_values('Datetime').reset_index(drop=True)

        # Energía de autoconsumo: la menor entre producción y demanda
        df['SelfConsumption'] = df[['Production', 'Demand']].min(axis=1)

        # Energía consumida de la red: cuando la demanda supera la producción
        df['GridConsumption'] = df.apply(
            lambda row: max(row['Demand'] - row['Production'], 0), axis=1
        )

        # Energía vertida a la red: cuando la producción supera la demanda
        df['ExportToGrid'] = df.apply(
            lambda row: max(row['Production'] - row['Demand'], 0), axis=1
        )

        self.result = df
        return df

    def get_last_hours_from(self, start_date: str, hours: int = 168):
        """Devuelve las horas a partir de start_date"""
        if self.result is None:
            raise ValueError("Call calculate() first.")
        start_dt = pd.to_datetime(start_date)
        df_filtered = self.result[self.result['Datetime'] >= start_dt].copy()
        return df_filtered.head(hours)

    def get_daily_aggregated_from(self, start_date: str, days: int = 7, export_csv: str = None):
        """Devuelve los días agregados a partir de start_date"""
        if self.result is None:
            raise ValueError("Call calculate() first.")
        start_dt = pd.to_datetime(start_date)
        df_filtered = self.result[self.result['Datetime'] >= start_dt].copy()

        # Columnas a sumar
        cols_to_sum = ['Demand', 'Production', 'SelfConsumption', 'GridConsumption', 'ExportToGrid']

        # Agrupar por día
        df_filtered['Date'] = df_filtered['Datetime'].dt.date
        df_daily = df_filtered.groupby('Date')[cols_to_sum].sum().reset_index()
        df_daily['Datetime'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.head(days)
        df_daily = df_daily[['Datetime', 'Demand', 'Production', 'SelfConsumption', 'GridConsumption', 'ExportToGrid']]

        if export_csv:
            df_daily.to_csv(export_csv, index=False)
            print(f"Daily aggregated data exported to {export_csv}")

        return df_daily

    def get_last_hours(self, hours: int = 168):
        """Devuelve las últimas `hours` del DataFrame calculado"""
        if self.result is None:
            raise ValueError("Call calculate() first.")
        return self.result.tail(hours).copy()

    def get_daily_aggregated(self, hours: int = 168, export_csv: str = None):
        if self.result is None:
            raise ValueError("Call calculate() first.")

        # Tomar últimas 'hours' horas
        df_last_hours = self.result.tail(hours).copy()

        # Columnas a sumar
        cols_to_sum = ['Demand', 'Production', 'SelfConsumption', 'GridConsumption', 'ExportToGrid']

        # Agrupar por día y sumar
        df_last_hours['Date'] = df_last_hours['Datetime'].dt.date
        df_daily = df_last_hours.groupby('Date')[cols_to_sum].sum().reset_index()
        df_daily['Datetime'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.tail(7)  # últimos 7 días

        # Reordenar columnas según el orden deseado
        df_daily = df_daily[['Datetime', 'Demand', 'Production', 'SelfConsumption', 'GridConsumption', 'ExportToGrid']]

        # Exportar a CSV si se indica
        if export_csv:
            df_daily.to_csv(export_csv, index=False)
            print(f"Daily aggregated data exported to {export_csv}")

        return df_daily

