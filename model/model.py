"""
Script untuk kelas Model
Script untuk melakukan penarikan data dari API endpoint
"""
from typing import Literal

import pandas as pd
from binance import Client

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Model:
    # set __init__ dengan kelas akun yg diinisiasi di undecided.py
    def __init__(self, exchange: Client) -> None:
        self.exchange = exchange

    # method untuk mengambil data historis
    def ambil_data_historis(
        self,
        simbol: str,
        interval_kline: Literal[
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ],
        jenis_pasar: Literal["SPOT", "FUTURES"],
        tgl_awal: str,
    ) -> pd.DataFrame:
        self.simbol = simbol
        self.interval_kline = interval_kline
        self.jenis_pasar = jenis_pasar
        self.tgl_awal = tgl_awal

        # set header untuk dataframe
        self.header = [
            "Waktu Pembukaan",
            "Buka",
            "Tinggi",
            "Rendah",
            "Tutup",
            "Volum Aset",
            "Waktu Penutupan",
            "Volum Aset dlm USDT",
            "Jumlah Transaksi",
            "Volum Instan Aset",
            "Volum Instan dlm USDT",
            "Ignore",
        ]

        # fetch data_historis
        match self.jenis_pasar:
            case "SPOT":
                data_historis = self.exchange.get_historical_klines(
                    self.simbol, self.interval_kline, self.tgl_awal
                )
            case "FUTURES":
                data_historis = self.exchange.futures_historical_klines(
                    self.simbol, self.interval_kline, self.tgl_awal
                )

        data_historis_df = pd.DataFrame(data_historis, columns=self.header)

        # konversi datetime
        data_historis_df["Waktu Pembukaan"] = pd.to_datetime(
            data_historis_df["Waktu Pembukaan"] / 1000, unit="s"
        )
        data_historis_df["Waktu Penutupan"] = pd.to_datetime(
            data_historis_df["Waktu Penutupan"] / 1000, unit="s"
        )

        # konversi objek menjadi nilai numerik
        kolom_numerik = [
            "Buka",
            "Tinggi",
            "Rendah",
            "Tutup",
            "Volum Aset",
            "Volum Aset dlm USDT",
            "Volum Instan Aset",
            "Volum Instan dlm USDT",
        ]
        data_historis_df[kolom_numerik] = data_historis_df[kolom_numerik].apply(
            pd.to_numeric, axis=1
        )

        # return dataframe data_historis
        return data_historis_df
