import pandas as pd

class DataLoader:
    def __init__(self, csv_path: str, datetime_col: str):
        self.csv_path = csv_path
        self.datetime_col = datetime_col
        self.df = None

    def load(self):
        self.df = pd.read_csv(self.csv_path)
        self.df[self.datetime_col] = pd.to_datetime(self.df[self.datetime_col])
        return self.df

    def get_series(self, value_col: str, rename_to: str):
        return (
            self.df[[self.datetime_col, value_col]]
            .rename(columns={
                self.datetime_col: 'Datetime',
                value_col: rename_to
            })
        )
