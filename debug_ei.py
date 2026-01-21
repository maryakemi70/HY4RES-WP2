import pandas as pd
from pathlib import Path
from src.environmental_indicators.ei_service import EnvironmentalIndicatorsService
from src.data_loader import DataLoader

# ----------------------------------------
# 1️⃣ Cargar CSV de energía diaria
# ----------------------------------------
csv_path = Path(r"C:\Users\Win\PycharmProjects\IntegrationOfModels\Streamlit\data\true_data.csv")

loader = DataLoader(str(csv_path), datetime_col="Datetime")
df_daily_energy = loader.load()

print("=== Step 1: CSV cargado ===")
print(df_daily_energy.head())
print(df_daily_energy.columns)
print(df_daily_energy.dtypes)

# ----------------------------------------
# 2️⃣ Extraer columnas necesarias
# ----------------------------------------
df_daily_energy = loader.get_series(value_col="Energy Consumption kWh", rename_to="GridConsumption")
# Simular SelfConsumption y ExportToGrid si no existen
if "SelfConsumption" not in df_daily_energy.columns:
    df_daily_energy["SelfConsumption"] = 0.0
if "ExportToGrid" not in df_daily_energy.columns:
    df_daily_energy["ExportToGrid"] = 0.0

print("=== Step 2: Series preparada ===")
print(df_daily_energy.head())

# ----------------------------------------
# 3️⃣ Convertir 'Datetime' a datetime (redundante pero seguro)
# ----------------------------------------
df_daily_energy["Datetime"] = pd.to_datetime(df_daily_energy["Datetime"])
print("=== Step 3: 'Datetime' convertido ===")
print(df_daily_energy.head())

# ----------------------------------------
# 4️⃣ Inicializar EI Service
# ----------------------------------------
csv_mix_grid = Path(r"C:\Users\Win\PycharmProjects\IntegrationOfModels\Streamlit\data\percentage_mix_grid_unified.csv")
ei_service = EnvironmentalIndicatorsService(df_daily_energy, str(csv_mix_grid))
print("=== Step 4: EI Service inicializado ===")

# ----------------------------------------
# 5️⃣ Mostrar mix de la red cargado
# ----------------------------------------
print("=== Step 5: Mix de la red ===")
print(ei_service.df_mix_grid.head())
print(ei_service.df_mix_grid.dtypes)

# ----------------------------------------
# 6️⃣ Calcular indicadores
# ----------------------------------------
indicators = [
    {"energy_source": "Hydropower_kWh", "GWP100": 0.004345569, "ADP_fossil": 0.041796964, "ADP_elements": 1.92e-08, "UDP": 0.002012897},
    {"energy_source": "Nuclear_kWh", "GWP100": 0.006867669, "ADP_fossil": 13.22250307, "ADP_elements": 1.22e-07, "UDP": 0.132012697},
    {"energy_source": "Coal_kWh", "GWP100": 1.162411024, "ADP_fossil": 11.50390196, "ADP_elements": 2.53e-07, "UDP": 0.080646243},
]

# ----------------------------------------
# 7️⃣ Calcular tablas
# ----------------------------------------
tables = ei_service.calculate_daily_EI_tables(
    indicators=indicators,
    start_date="2020-01-01",
    days=7
)

# ----------------------------------------
# 8️⃣ Mostrar tablas generadas
# ----------------------------------------
for metric, table in tables.items():
    print(f"\n=== Tabla {metric} ===")
    print(table.head())
    print(table.columns)
