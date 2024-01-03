from pathlib import Path
import pandas as pd


class Zones:
    def __init__(self) -> None:
        self.table = None

    def load(self):
        self.table = pd.read_csv(Path(__file__).parent / "zones.csv")
        return self
