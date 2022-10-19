"""
Script untuk kelas Model
Script untuk melakukan penarikan data dari API endpoint
"""

import pandas as pd

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

class Model:
    # set __init__ dengan kelas akun yg diinisiasi di undecided.py
    def __init__(self, akun):
        self.akun = akun

    # method untuk mengambil data historis
    def ambil_data_historis(self, simbol, interval_kline, tgl_awal):
        self.simbol = simbol
        self.interval_kline = interval_kline
        self.tgl_awal = tgl_awal

        # set header untuk dataframe
        self.header = [
            "Open Time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close Time",
            "Quote Asset Volume",
            "Number of Trades",
            "TB Base Volume",
            "TB Quote Volume",
            "Ignore",
        ]

        # fetch data_historis
        data_historis = self.akun.get_historical_klines(
            self.simbol, self.interval_kline, self.tgl_awal
        )
        data_historis_df = pd.DataFrame(data_historis, columns=self.header)

        # konversi datetime
        data_historis_df["Open Time"] = pd.to_datetime(
            data_historis_df["Open Time"] / 1000, unit="s"
        )
        data_historis_df["Close Time"] = pd.to_datetime(
            data_historis_df["Close Time"] / 1000, unit="s"
        )

        # konversi objek menjadi nilai numerik
        kolom_numerik = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Quote Asset Volume",
            "TB Base Volume",
            "TB Quote Volume",
        ]
        data_historis_df[kolom_numerik] = data_historis_df[kolom_numerik].apply(
            pd.to_numeric, axis=1
        )

        # return dataframe data_historis
        return data_historis_df
