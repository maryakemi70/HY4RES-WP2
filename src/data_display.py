import streamlit as st
import plotly.graph_objects as go
import io
import pandas as pd

class DataDisplay:
    """
    Handles dataframe and Plotly figure visualization with download options in Streamlit.
    Safely handles Plotly image export (requires kaleido).
    """

    def __init__(self, df: pd.DataFrame = None, plotly_fig: go.Figure = None, mode: str = "hourly"):
        """
        :param df: dataframe para exibição e download em CSV
        :param plotly_fig: figura Plotly para exibição e download (JPG/HTML)
        :param mode: modo "hourly" ou "daily" (opcional)
        """
        self.df = df
        self.fig = plotly_fig
        self.mode = mode

    # -----------------------
    # TABELA CSV
    # -----------------------
    def show_table_with_download(self, filename: str = "data.csv", height: int = 250):
        """
        Exibe um dataframe e adiciona botão para download CSV.
        """
        if self.df is None:
            st.warning("No dataframe provided.")
            return

        st.dataframe(
            self.df,
            height=height,
            use_container_width=True
        )

        csv_bytes = self.df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv"
        )

    # -----------------------
    # GRÁFICO PLOTLY
    # -----------------------
    def show_with_download(self, filename: str = "chart"):
        """
        Exibe um gráfico Plotly e adiciona botões para download em JPG e HTML.
        Somente ativa JPG se o kaleido estiver instalado.
        """
        if self.fig is None:
            st.warning("No Plotly figure provided.")
            return

        # Exibir o gráfico no Streamlit
        st.plotly_chart(self.fig, use_container_width=True)

        # HTML interativo
        html_io = io.StringIO()
        self.fig.write_html(html_io, include_plotlyjs='cdn')
        html_bytes = html_io.getvalue().encode('utf-8')
        st.download_button(
            label="📥 Download HTML (interactive chart)",
            data=html_bytes,
            file_name=f"{filename}.html",
            mime="text/html"
        )

        # JPG estático (somente se kaleido estiver instalado)
        try:
            img_bytes = self.fig.to_image(format="jpeg", scale=2)
            st.download_button(
                label="📥 Download JPG (static chart)",
                data=img_bytes,
                file_name=f"{filename}.jpg",
                mime="image/jpeg"
            )
        except ValueError:
            pass
            # st.info("📌 To enable JPG download, install the 'kaleido' package: pip install -U kaleido")
