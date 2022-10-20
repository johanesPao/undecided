"""
Script untuk kelas Model
Script untuk melakukan penarikan data dari API endpoint
"""

import pandas as pd
from tvDatafeed import Interval, TvDatafeed

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Model:
    # set __init__ dengan kelas akun yg diinisiasi di undecided.py
    def __init__(self, data_konektor: TvDatafeed) -> None:
        self.data_konektor = data_konektor

        # mapping interval tvDatafeed

    # method untuk mengambil data historis
    def ambil_data_historis(
        self,
        simbol: str,
        exchange: str,
        interval: Interval,
        jumlah_bar: int,
    ) -> pd.DataFrame:
        self.simbol = simbol
        self.exchange = exchange
        self.interval = interval
        self.jumlah_bar = jumlah_bar

        # return data_historis
        return self.data_konektor.get_hist(
            self.simbol, self.exchange, self.interval, self.jumlah_bar
        )
