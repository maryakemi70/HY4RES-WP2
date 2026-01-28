import pandas as pd


def get_inverse_color(value):
    if value is None:
        return "#7f8c8d"  # gris neutro
    elif value < 0:
        return "#2ecc71"  # verde (mejora ambiental)
    elif value > 0:
        return "#e74c3c"  # rojo (impacto)
    else:
        return "#bdc3c7"  # gris claro

def color_net_impact(val):
    if val < 0:
        return "background-color: #2ecc71; color: white;"  # verde
    elif val > 0:
        return "background-color: #e74c3c; color: white;"  # rojo
    else:
        return "background-color: #bdc3c7; color: black;"  # gris neutro

def raw_style_impact_table(df, indicator_col="Indicator", metric=None, net_col="Net Impact"):

    numeric_cols = df.select_dtypes(include=["number"]).columns

    # ---------------------------------------------
    # FORMAT FUNCTION (ROW-AWARE)
    # ---------------------------------------------
    def make_formatter(col):
        def _fmt(x):
            if pd.isna(x):
                return x

            # find indicator for this row
            row = df[df[col] == x]
            indicator = None
            if not row.empty:
                indicator = row.iloc[0][indicator_col]

            # ONLY ADP_elements row → scientific notation
            if metric == "ADP_elements" and indicator == "ADP_elements":
                return f"{x:.1e}"

            # default format
            return f"{x:.1f}"

        return _fmt

    # Apply per-column formatter
    styler = df.style.format({
        col: make_formatter(col)
        for col in numeric_cols if col != "Date"
    })

    # ---------------------------------------------
    # COLOR NET IMPACT (NEGATIVE = GREEN)
    # ---------------------------------------------
    if net_col in df.columns:
        styler = styler.applymap(
            lambda val: f"background-color: {get_inverse_color(val)}; color: white;",
            subset=[net_col]
        )

    return styler


def style_impact_table(df, indicator_col="Indicator", scientific_all=False):
    """
    Visual formatting only:
    - Default: 1 decimal
    - ADP_elements: scientific
    - scientific_all=True → all numeric values in scientific notation
    """

    numeric_cols = df.select_dtypes(include=["number"]).columns

    if scientific_all:
        return df.style.format({col: "{:.1e}" for col in numeric_cols})

    def make_formatter(col):
        def _fmt(x):
            if pd.isna(x):
                return x

            # obtener indicador de la fila
            try:
                indicator = df.loc[df[col] == x, indicator_col].values[0]
            except Exception:
                indicator = None

            if indicator == "ADP_elements":
                return f"{x:.1e}"
            return f"{x:.1f}"

        return _fmt

    return df.style.format({col: make_formatter(col) for col in numeric_cols})


def add_pv_multiheader(df, pv_cols=("Self Consumption", "Export to Grid")):
    """
    Convierte las columnas PV a un encabezado multi-nivel:
    Nivel 0: "PV Solar Production" sobre Self Consumption y Export to Grid
    Nivel 1: nombres originales de las columnas
    """
    new_columns = []
    for col in df.columns:
        if col in pv_cols:
            new_columns.append(("                                        PV Solar Production", col))
        else:
            new_columns.append(("", col))  # resto sin agrupación

    df.columns = pd.MultiIndex.from_tuples(new_columns)
    return df



