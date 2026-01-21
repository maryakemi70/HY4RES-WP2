from pathlib import Path
import pandas as pd

from src.data_loader import DataLoader
from src.surplus_calculator import SurplusCalculator
from src.environmental_indicators.ei_service import EnvironmentalIndicatorsService


class EnergyDataService:
    """
    Servicio centralizado de carga, cálculo y agregación de datos energéticos.
    """

    def __init__(self):
        # Streamlit/src/services -> Streamlit/src -> Streamlit
        self.streamlit_root = Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.streamlit_root / "data"

        # CSVs
        self.demand_path = self.data_dir / "true_data.csv"
        self.production_path = self.data_dir / "true_data.csv"
        self.grid_mix_path = self.data_dir / "percentage_mix_grid_unified.csv"

        # DataFrames base
        self.demand_df = None
        self.production_df = None

        # Cálculos
        self.surplus_calculator = None
        self.df_daily_full = None  # 👈 CLAVE: diario completo (2020–2023)

        self._loaded = False

    # --------------------------------------------------
    # Carga de datos
    # --------------------------------------------------
    def load_data(self):
        if not self.demand_path.exists():
            raise FileNotFoundError(f"No se encontró el CSV de demanda en: {self.demand_path}")
        if not self.production_path.exists():
            raise FileNotFoundError(f"No se encontró el CSV de producción en: {self.production_path}")

        # Demanda
        demand_loader = DataLoader(str(self.demand_path), datetime_col="Datetime")
        demand_loader.load()
        self.demand_df = demand_loader.get_series(
            value_col="Energy Consumption kWh",
            rename_to="Demand"
        )

        # Producción
        prod_loader = DataLoader(str(self.production_path), datetime_col="Datetime")
        prod_loader.load()
        self.production_df = prod_loader.get_series(
            value_col="Producción Planta",
            rename_to="Production"
        )

        self._loaded = True

    # --------------------------------------------------
    # Surplus
    # --------------------------------------------------
    def get_surplus_calculator(self) -> SurplusCalculator:
        """
        Devuelve el SurplusCalculator ya calculado.
        """
        if not self._loaded:
            self.load_data()

        if self.surplus_calculator is None:
            self.surplus_calculator = SurplusCalculator(
                self.demand_df,
                self.production_df
            )
            self.surplus_calculator.calculate()

            # 🔑 Guardamos el DAILY COMPLETO una sola vez
            self.df_daily_full = self.surplus_calculator.get_daily_aggregated_from(
                start_date=str(self.surplus_calculator.result["Datetime"].min().date()),
                days=100_000
            )

        return self.surplus_calculator

    # --------------------------------------------------
    # DAILY COMPLETO (para TimeControlPanel)
    # --------------------------------------------------
    def get_daily_full(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame diario COMPLETO (sin filtros).
        """
        if self.df_daily_full is None:
            self.get_surplus_calculator()
        return self.df_daily_full.copy()

    # --------------------------------------------------
    # DAILY FILTRADO (Energy Surplus / EI)
    # --------------------------------------------------
    def get_daily_filtered(self, start_date, days: int) -> pd.DataFrame:
        """
        Devuelve datos diarios filtrados por fecha y horizonte.
        """
        df = self.get_daily_full()
        df = df[df["Datetime"].dt.date >= start_date].copy()
        return df.head(days)

    # --------------------------------------------------
    # Environmental Indicators
    # --------------------------------------------------
    def get_environmental_service(
        self,
        start_date,
        days: int
    ) -> EnvironmentalIndicatorsService:
        """
        Devuelve el servicio de indicadores ambientales
        SOLO con los días seleccionados en la UI.
        """
        df_daily_filtered = self.get_daily_filtered(
            start_date=start_date,
            days=days
        )

        return EnvironmentalIndicatorsService(
            df_daily_energy=df_daily_filtered,
            grid_mix_path=self.grid_mix_path
        )

    # --------------------------------------------------
    # Agregaciones (mensual / anual)
    # --------------------------------------------------
    def get_aggregated_surplus(self, start_date=None, period="D") -> pd.DataFrame:
        """
        Devuelve surplus agregado por día / mes / año.

        period:
            "D" = diario
            "M" = mensual
            "Y" = anual
        """
        df_daily = self.get_daily_full()

        if start_date is not None:
            df_daily = df_daily[df_daily["Datetime"].dt.date >= start_date]

        df_daily = df_daily.set_index("Datetime")

        if period.upper() in ["M", "Y"]:
            df_resampled = df_daily.resample(period).sum()
            return df_resampled.reset_index()

        # Diario
        return df_daily.reset_index()
