"""
Script untuk kelas Strategi
Script untuk implementasi strategi trading berdasarkan pertimbangan pribadi akan beberapa faktor seperti analisa teknikal
"""

from typing import List, Literal

import pandas as pd
from tvDatafeed import Interval

from analisa.analisa_teknikal import AnalisaTeknikal
from baca_konfig import Inisiasi
from model.model import Model

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Strategi:
    def __init__(self, simbol: str, exchange: str) -> None:
        self.inisiasi = Inisiasi()
        self.konektor_data = self.inisiasi.data()
        self.model = Model(self.konektor_data)
        self.simbol = simbol
        self.exchange = exchange
        self.analisa_teknikal = AnalisaTeknikal()

    def stokastik_jpao(
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
        k_cepat: int = 14,
        k_lambat: int = 3,
        d_lambat: int = 3,
    ):
        if len(interval) != 2:
            return print(
                "Strategi ini (strategi_stokastik_jpao) memerlukan dua interval waktu dalam list"
            )

        jumlah_bar = k_cepat * max(k_lambat, d_lambat)

        for waktu in interval:
            match waktu:
                case "1 menit":
                    interval_data = Interval.in_1_minute
                case "3 menit":
                    interval_data = Interval.in_3_minute
                case "5 menit":
                    interval_data = Interval.in_5_minute
                case "15 menit":
                    interval_data = Interval.in_15_minute
                case "30 menit":
                    interval_data = Interval.in_30_minute
                case "45 menit":
                    interval_data = Interval.in_45_minute
                case "1 jam":
                    interval_data = Interval.in_1_hour
                case "2 jam":
                    interval_data = Interval.in_2_hour
                case "3 jam":
                    interval_data = Interval.in_3_hour
                case "4 jam":
                    interval_data = Interval.in_4_hour
                case "1 hari":
                    interval_data = Interval.in_daily
                case "1 minggu":
                    interval_data = Interval.in_weekly
                case "1 bulan":
                    interval_data = Interval.in_monthly

            df = self.model.ambil_data_historis(
                self.simbol, self.exchange, interval_data, jumlah_bar
            )

            df_ta = self.analisa_teknikal.stokastik(df, k_cepat, k_lambat, d_lambat)

            print(df_ta)
