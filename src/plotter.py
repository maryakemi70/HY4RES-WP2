import matplotlib
matplotlib.use("TkAgg")  # o "TkAgg", depende de tu sistema
import pandas as pd
import plotly.graph_objects as go

class LastDateEnergyPlotter:
    def __init__(self, df, mode='hourly'):
        self.mode = mode
        self.df = df.copy()

        # Ajuste de período
        if mode == 'hourly':
            self.df = self.df.tail(168)
        else:
            df_last168 = self.df.tail(168).copy()
            df_last168['Date'] = df_last168['Datetime'].dt.date
            cols_to_sum = ['SelfConsumption', 'ImportfromGrid', 'ExportToGrid', 'Demand', 'Production']
            df_daily = df_last168.groupby('Date')[cols_to_sum].sum().reset_index()
            df_daily['Datetime'] = pd.to_datetime(df_daily['Date'])
            df_daily.drop(columns='Date', inplace=True)
            self.df = df_daily.tail(7)

        # Limites de Y (para hover / referencia)
        self.ymin = 0
        self.ymax = self.df[['SelfConsumption', 'ImportfromGrid', 'ExportToGrid', 'Demand', 'Production']].max().max() * 1.1

        # Garantir tipos corretos e ordenação
        self._sanitize_dataframe()

    def _sanitize_dataframe(self):
        """Garante datetime, float e ordenação"""
        cols_numeric = ['SelfConsumption', 'ImportfromGrid', 'ExportToGrid', 'Demand', 'Production']
        self.df['Datetime'] = pd.to_datetime(self.df['Datetime'], errors='coerce')
        self.df.dropna(subset=['Datetime'], inplace=True)

        for c in cols_numeric:
            self.df[c] = pd.to_numeric(self.df[c], errors='coerce')

        self.df.dropna(subset=cols_numeric, inplace=True)
        self.df.sort_values('Datetime', inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    def _plot_line(self, y_col, name, color):
        """Plot simples de linha (hourly ou daily)"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.df['Datetime'].to_list(),
            y=self.df[y_col].to_list(),
            mode='lines+markers',
            name=name,
            line=dict(color=color),
            hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh"
        ))

        fig.update_layout(
            title=f"{name} Over Time",
            xaxis_title="Datetime",
            yaxis_title="Energy [kWh]",
            yaxis=dict(range=[self.ymin, self.ymax]),
            hoverlabel=dict(font_size=16)
        )

        fig.update_xaxes(type='date')
        return fig

    def _plot_bar(self, y_col, name, color, bottom_col=None):
        """Plot de barras independiente (daily), siempre empieza en 0"""
        fig = go.Figure()

        y_values = self.df[y_col].to_list()

        # Ignorar bottom_col si queremos gráfica independiente
        fig.add_trace(go.Bar(
            x=self.df['Datetime'].to_list(),
            y=y_values,
            name=name,
            marker_color=color,
            hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh"
        ))

        fig.update_layout(
            title=f"{name} Over Time",
            xaxis_title="Datetime",
            yaxis_title="Energy [kWh]",
            yaxis=dict(range=[0, max(y_values) * 1.1]),  # Siempre empieza en 0
            hoverlabel=dict(font_size=16)
        )

        fig.update_xaxes(type='date')
        return fig

    def plot_self_consumption(self):
        if self.mode == 'hourly':
            return self._plot_line('SelfConsumption', 'Self-Consumption (kWh)', 'green')
        else:
            return self._plot_bar('SelfConsumption', 'Self-Consumption (kWh)', 'green')

    def plot_grid_consumption(self):
        if self.mode == 'hourly':
            return self._plot_line('ImportfromGrid', 'Import from Grid (kWh)', '#D22C41')
        else:
            return self._plot_bar('ImportfromGrid', 'Import from Grid (kWh)', '#D22C41')

    def plot_export_to_grid(self):
        if self.mode == 'hourly':
            return self._plot_line('ExportToGrid', 'Export to Grid (kWh)', '#2078FF')
        else:
            return self._plot_bar('ExportToGrid', 'Export to Grid (kWh)', '#2078FF', bottom_col='SelfConsumption')

    def plot_demand_vs_production(self):
        """Plot de Demand vs Production com linhas"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.df['Datetime'].to_list(),
            y=self.df['Demand'].to_list(),
            mode='lines+markers',
            name='Demand (kWh)',
            line=dict(color='#AA4BFF'),
            hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh"
        ))

        fig.add_trace(go.Scatter(
            x=self.df['Datetime'].to_list(),
            y=self.df['Production'].to_list(),
            mode='lines+markers',
            name='PV Production (kWh)',
            line=dict(color='#FF8D4B'),
            hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh"
        ))

        fig.update_layout(
            title="Demand vs PV Production",
            xaxis_title="Datetime",
            yaxis_title="Energy [kWh]",
            yaxis=dict(range=[self.ymin, self.ymax]),
            hoverlabel=dict(font_size=16)
        )
        fig.update_xaxes(type='date')
        return fig

    def plot_all(self):
        return {
            'SelfConsumption': self.plot_self_consumption(),
            'ImportfromGrid': self.plot_grid_consumption(),
            'ExportToGrid': self.plot_export_to_grid(),
            'DemandVsProduction': self.plot_demand_vs_production()
        }

    def plot_combined_with_selection(self, selected_options):
        """
        Crea una gráfica combinada con los trazos seleccionados por el usuario.

        Parameters:
        -----------
        selected_options : list
            Lista de claves que el usuario desea visualizar. Posibles claves:
            ['SelfConsumption', 'GridConsumption', 'ExportToGrid', 'Demand', 'Production']
        """
        fig = go.Figure()

        # Mapear nombres a datos y colores
        trace_map = {
            'SelfConsumption': ('SelfConsumption', 'green'),
            'ImportfromGrid': ('ImportfromGrid', '#D22C41'),
            'ExportToGrid': ('ExportToGrid', '#2078FF'),
            'Demand': ('Demand', '#AA4BFF'),
            'Production': ('Production', '#FF8D4B')
        }

        for key in selected_options:
            if key in trace_map:
                col_name, color = trace_map[key]
                fig.add_trace(go.Scatter(
                    x=self.df['Datetime'].to_list(),
                    y=self.df[col_name].to_list(),
                    mode='lines+markers',
                    name=f"{key} (kWh)",
                    line=dict(color=color)
                ))

        fig.update_layout(
            xaxis_title="Datetime",
            yaxis_title="Energy [kWh]",
            hovermode="x unified",
            height=600
        )

        return fig

    def plot_combined_interactive(self):
        """
        Crea una gráfica interactiva combinada donde se puede elegir qué visualizar:
        SelfConsumption, GridConsumption, ExportToGrid, Demand y Production
        mediante botones (updatemenus) usando visible=True/False.
        """
        fig = go.Figure()

        # Añadir todos los trazos
        traces = {
            'SelfConsumption': go.Scatter(
                x=self.df['Datetime'].to_list(), y=self.df['SelfConsumption'].to_list(),
                mode='lines+markers', name='SelfConsumption (kWh)',
                line=dict(color='green')
            ),
            'ImportfromGrid': go.Scatter(
                x=self.df['Datetime'].to_list(), y=self.df['ImportfromGrid'].to_list(),
                mode='lines+markers', name='Import from Grid (kWh)',
                line=dict(color='red')
            ),
            'ExportToGrid': go.Scatter(
                x=self.df['Datetime'].to_list(), y=self.df['ExportToGrid'].to_list(),
                mode='lines+markers', name='ExportToGrid (kWh)',
                line=dict(color='white')
            ),
            'Demand': go.Scatter(
                x=self.df['Datetime'].to_list(), y=self.df['Demand'].to_list(),
                mode='lines+markers', name='Demand (kWh)',
                line=dict(color='#AA4BFF')
            ),
            'Production': go.Scatter(
                x=self.df['Datetime'].to_list(), y=self.df['Production'].to_list(),
                mode='lines+markers', name='PV Production (kWh)',
                line=dict(color='#FF8D4B')
            )
        }

        # Agregar todos los trazos a la figura, inicialmente visibles
        for trace in traces.values():
            fig.add_trace(trace)

        # Crear botones para seleccionar trazos
        buttons = []
        for key in traces.keys():
            visibility = [False] * len(traces)
            idx = list(traces.keys()).index(key)
            visibility[idx] = True
            buttons.append(dict(
                label=key,
                method="update",
                args=[{"visible": visibility},
                      {"title": f"{key} Over Time"}]
            ))

        # Botón para mostrar todos
        buttons.append(dict(
            label="All",
            method="update",
            args=[{"visible": [True] * len(traces)},
                  {"title": "All Energy Traces"}]
        ))

        fig.update_layout(
            updatemenus=[dict(
                active=len(buttons) - 1,  # Por defecto "All"
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top"
            )],
            title="All Energy Traces",
            xaxis_title="Datetime",
            yaxis_title="Energy [kWh]",
            hovermode="x unified",
            height=600
        )

        return fig



