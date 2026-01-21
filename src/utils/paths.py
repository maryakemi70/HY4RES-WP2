import os

def get_streamlit_root():
    """Devuelve la carpeta raíz de Streamlit dentro del proyecto."""
    return os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    """Devuelve la carpeta de datos dentro de Streamlit"""
    return os.path.join(get_streamlit_root(), "..", "data")

def get_true_data_csv():
    """CSV de demanda y producción"""
    return os.path.join(get_data_dir(), "true_data.csv")

def get_daily_ei_csv():
    """CSV donde guardar el EI diario"""
    return os.path.join(get_data_dir(), "daily-_EI.csv")
