import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
demand_path = os.path.join(BASE_DIR, 'data', 'true_data.csv')
production_path = os.path.join(BASE_DIR, 'data', 'true_data.csv')

# ---------- Load data ----------
demand = pd.read_csv(demand_path)
production = pd.read_csv(production_path)

demand['Datetime'] = pd.to_datetime(demand['Datetime'])
production['Datetime'] = pd.to_datetime(production['Datetime'])

demand = demand[['Datetime', 'Energy Consumption kWh']]
production = production[['Datetime', 'Producción Planta']]

demand = demand.rename(columns={'Energy Consumption kWh': 'Demand'})
production = production.rename(columns={'Producción Planta': 'Production'})

# ---------- Merge ----------
df = demand.merge(production, on='Datetime', how='inner')
df = df.sort_values('Datetime')

df['Surplus'] = df['Production'] - df['Demand']

def validate_dataframe(df):
    try:
        # Ensure 'Datetime' column is in datetime format
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        if df['Datetime'].isnull().any():
            raise ValueError("The 'Datetime' column contains invalid datetime values.")

        # Check for missing values in critical columns
        if df[['Datetime', 'Surplus', 'Demand', 'Production']].isnull().any().any():
            raise ValueError("There are missing values in one or more critical columns: 'Datetime', 'Surplus', 'Demand', 'Production'.")

        # Check for duplicate or unsorted 'Datetime' values
        if not df['Datetime'].is_monotonic_increasing:
            raise ValueError("The 'Datetime' column is not sorted in ascending order or contains duplicates.")

        print("All checks passed. The DataFrame is valid.")
    except Exception as e:
        print(f"Validation error: {e}")

# Validate the DataFrame
validate_dataframe(df)

# # ---------- Plot ----------
# plt.figure(figsize=(14, 5))
#
# # Positive surplus (green)
# plt.plot(
#     df['Datetime'],
#     df['Surplus'].where(df['Surplus'] >= 0),
#     color='green',
#     label='Surplus (Production > Demand)'
# )
#
# # Negative surplus (red)
# plt.plot(
#     df['Datetime'],
#     df['Surplus'].where(df['Surplus'] < 0),
#     color='red',
#     label='Deficit (Production < Demand)'
# )
#
# # Zero line
# plt.axhline(0, color='black', linewidth=0.8)
#
# plt.title('Energy Surplus (+) and Deficit (−)')
# plt.xlabel('Datetime')
# plt.ylabel('Energy [kWh]')
# plt.legend()
# plt.tight_layout()
# plt.show()
