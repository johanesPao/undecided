"""
Script untuk kelas Strategi
Script untuk implementasi strategi trading berdasarkan pertimbangan pribadi akan beberapa faktor seperti analisa teknikal
"""

from typing import List, Literal

import pandas as pd
from tvDatafeed import Interval

from akun.akun import InfoAkun
from analisa.analisa_teknikal import AnalisaTeknikal
from baca_konfig import Inisiasi
from model.model import Model
from tindakan.tindakan import Order

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Strategi:
    def __init__(
        self,
        simbol: str,
        exchange: str,
        backtest: bool = False,
        jumlah_periode_backtest: int = 0,
    ) -> None:
        self.inisiasi = Inisiasi()
        self.konektor_data = self.inisiasi.data()
        self.konektor_exchange = self.inisiasi.exchange()
        self.model = Model(self.konektor_data)
        self.analisa_teknikal = AnalisaTeknikal()
        self.posisi_futures = InfoAkun(self.konektor_exchange).akun_futures()[6]
        self.order = Order()
        self.simbol = simbol
        self.exchange = exchange
        self.backtest = backtest
        self.jumlah_periode_backtest = jumlah_periode_backtest
        if self.backtest and self.jumlah_periode_backtest <= 0:
            raise ValueError(
                f"Jika backtest={self.backtest}, maka jumlah_periode_backtest harus lebih besar dari 0."
            )

    def jpao_hold_trade_sto_1533(
        self,
        interval: List[
            Literal[
                "1 menit",
                "3 menit",
                "5 menit",
                "15 menit",
                "30 menit",
                "45 menit",
                "1 jam",
                "2 jam",
                "3 jam",
                "4 jam",
                "1 hari",
                "1 minggu",
                "1 bulan",
            ]
        ] = ["4 jam", "1 hari"],
        k_cepat: int = 15,
        k_lambat: int = 5,
        d_lambat: int = 3,
    ) -> None | list:
        self.interval = interval
        self.k_cepat = k_cepat
        self.k_lambat = k_lambat
        self.d_lambat = d_lambat

        if len(self.interval) != 2:
            return print(
                "Strategi ini (strategi_stokastik_jpao) memerlukan dua interval waktu dalam list"
            )

        self.jumlah_bar = max(
            self.jumlah_periode_backtest, self.k_cepat + self.k_lambat + self.d_lambat
        )

        self.data_stokastik = []

        for waktu in self.interval:
            match waktu:
                case "1 menit":
                    self.interval_data = Interval.in_1_minute
                case "3 menit":
                    self.interval_data = Interval.in_3_minute
                case "5 menit":
                    self.interval_data = Interval.in_5_minute
                case "15 menit":
                    self.interval_data = Interval.in_15_minute
                case "30 menit":
                    self.interval_data = Interval.in_30_minute
                case "45 menit":
                    self.interval_data = Interval.in_45_minute
                case "1 jam":
                    self.interval_data = Interval.in_1_hour
                case "2 jam":
                    self.interval_data = Interval.in_2_hour
                case "3 jam":
                    self.interval_data = Interval.in_3_hour
                case "4 jam":
                    self.interval_data = Interval.in_4_hour
                case "1 hari":
                    self.interval_data = Interval.in_daily
                case "1 minggu":
                    self.interval_data = Interval.in_weekly
                case "1 bulan":
                    self.interval_data = Interval.in_monthly

            self.df = self.model.ambil_data_historis(
                self.simbol, self.exchange, self.interval_data, self.jumlah_bar
            )

            self.df_ta = self.analisa_teknikal.stokastik(
                self.df, self.k_cepat, self.k_lambat, self.d_lambat, self.backtest
            )

            self.data_stokastik.append(self.df_ta)

        print(self.data_stokastik)  # HAPUS NANTI

        # jika live stream strategi
        if not self.backtest:
            # cek posisi aset yang dipegang saat ini
            print(self.posisi_futures["positionSide"])

        return self.data_stokastik
