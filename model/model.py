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
    """
    Kelas Model yang dipergunakan untuk melakukan pengumpulan data dari tradingview menggunakan modul tvDatafeed

    Atribut
    -------
    data_konektor (TvDatafeed):
        Instance dari kelas TvDatafeed pada modul tvDatafeed

    Metode
    ------
    ambil_data_historis(simbol: str, exchange: str, interval: Interval, jumlah_bar: int) -> pd.DataFrame:
        Mengambil data historis untuk suatu simbol dalam exchange tertentu dengan jumlah bar (1 candlestick) tertentu dari tradingview
    """

    # set __init__ dengan kelas akun yg diinisiasi di undecided.py
    def __init__(self, data_konektor: TvDatafeed) -> None:
        """
        Metode inisiasi kelas Model

        Argumen
        -------
        data_konektor (TvDatafeed):
            Instance dari kelas TvDatafeed pada modul tvDatafeed

        Return
        ------
        (None)
        """
        self.data_konektor = data_konektor

    def ambil_data_historis(
        self,
        simbol: str,
        exchange: str,
        interval: Interval,
        jumlah_bar: int,
    ) -> pd.DataFrame:
        """
        Metode untuk mengambil data historis simbol dalam exchange dalam periode tertentu (jumlah_bar) dari API tradingview

        Argumen
        -------
        simbol (str):
            str simbol dari koin di tradingview
        exchange (str):
            str pasar exchange di tradingview
        interval (Interval):
            Objek Interval dari modul tvDatafeed untuk menentukan interval waktu data yang dikembalikan dari API tradingview
        jumlah_bar (int):
            int jumlah bar dengan interval waktu per bar yang ingin dikembalikan dari API tradingview

        Return
        ------
        (pd.DataFrame):
            DataFrame berisikan data historis OHLCV simbol dalam exchange
        """
        self.simbol = simbol
        self.exchange = exchange
        self.interval = interval
        self.jumlah_bar = jumlah_bar

        # Mengembalikan data historis menggunakan metode get_hist dari kelas TvDatafeed
        return self.data_konektor.get_hist(
            self.simbol, self.exchange, self.interval, self.jumlah_bar
        )
