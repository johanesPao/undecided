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
        self.HOLD_TRADE = ""

    def jpao_hold_trade_sto_1553(
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
        self.dua = 2

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

        # print(self.data_stokastik)  # HAPUS NANTI
        # fungsi saat live
        def live(list) -> str | None:
            # cek posisi aset yang dipegang saat ini
            posisi_aset = self.posisi_futures["positionSide"]

            # set nilai k_lambat_tf_kecil, d_lambat_tf_kecil, k_lambat_tf_besar dan d_lambat_tf_besar
            # untuk evaluasi state strategi
            k_lambat_tf_kecil = self.data_stokastik[0].iloc[-1]["k_lambat"]
            d_lambat_tf_kecil = self.data_stokastik[0].iloc[-1]["d_lambat"]
            k_lambat_tf_besar = self.data_stokastik[1].iloc[-1]["k_lambat"]
            d_lambat_tf_besar = self.data_stokastik[1].iloc[-1]["d_lambat"]
            print(f"Posisi Aset: {posisi_aset}")
            print(f"k_lambat pada timeframe kecil: {k_lambat_tf_kecil}")
            print(f"d_lambat pada timeframe kecil: {d_lambat_tf_kecil}")
            print(f"k_lambat pada timeframe besar: {k_lambat_tf_besar}")
            print(f"d_lambat pada timeframe besar: {d_lambat_tf_besar}")

            # set self.HOLD_TRADE sesuai kondisi pada timeframe besar
            self.HOLD_TRADE = (
                "LONG_SHORT" if k_lambat_tf_besar >= d_lambat_tf_besar else "SHORT_LONG"
            )

            # STRATEGI HOLD
            # jika variabel self.HOLD_TRADE == 'LONG_SHORT'
            if self.HOLD_TRADE == "LONG_SHORT":
                # jika tidak ada posisi LONG
                # print("BUKA_LONG")
                # jangan memaksakan diri untuk membuka posisi LONG
                # jika timeframe kecil tidak mendukung
                if (
                    "LONG" not in posisi_aset.unique()
                    and k_lambat_tf_kecil >= d_lambat_tf_kecil
                ):
                    return "BUKA_LONG"
                # jika k_lambat < d_lambat pada timeframe kecil
                if k_lambat_tf_kecil < d_lambat_tf_kecil:
                    # jika tidak ada posisi SHORT
                    if "SHORT" not in posisi_aset.unique():
                        return "BUKA_SHORT"
                # jika ada posisi SHORT
                elif "SHORT" in posisi_aset.unique():
                    return "TUTUP_SHORT"
                else:
                    return None
            # jika variabel self.HOLD_TRADE == 'SHORT_LONG
            elif self.HOLD_TRADE == "SHORT_LONG":
                # jika tidak ada posisi SHORT
                # print("BUKA_SHORT")
                # jangan memaksakan diri untuk membuka posisi SHORT
                # jika timeframe kecil tidak mendukung
                if (
                    "SHORT" not in posisi_aset.unique()
                    and k_lambat_tf_kecil < d_lambat_tf_kecil
                ):
                    return "BUKA_SHORT"
                # jika k_lambat >= d_lambat pada timeframe kecil
                if k_lambat_tf_kecil >= d_lambat_tf_kecil:
                    # jika tidak ada posisi LONG
                    if "LONG" not in posisi_aset.unique():
                        return "BUKA_LONG"
                # jika ada posisi LONG
                elif "LONG" in posisi_aset.unique():
                    return "TUTUP_LONG"
                else:
                    return None

        # fungsi saat backtest
        # def backtest(list) -> pd.DataFrame:
        #     iterasi

        # jika live stream strategi
        if not self.backtest:
            print(live(self.data_stokastik))
        else:
            return self.data_stokastik

            # STRATEGI TRADE
            # jika variabel self.HOLD_TRADE == 'LONG_SHORT'

            """
            1. Setiap pukul 3, 7, dan 11 strategi akan diinisiasi (scheduling akan dihandle di main script - undecided)
            2. Script strategi akan menarik data berdasarkan interval waktu (timeframe) yang ditetapkan dan menghitung k_lambat dan d_lambat (sudah dilakukan di atas)
            3. Strategi ini akan memiliki dua state dalam variabel self.HOLD_TRADE yang terbentuk pada saat inisiasi strategi, perubahan nilai variabel ini dipengaruhi oleh posisi k_lambat terhadap d_lambat pada timeframe besarnya
                1. HOLD_TRADE: 'LONG_SHORT' | 'SHORT_LONG'
                    a. LONG_SHORT: Saat k_lambat >= d_lambat pada timeframe besar
                        Analisa posisi_futures:
                            i. jika tidak ada posisi_futures LONG, BUKA_LONG jika
                                i.1 k_lambat >= d_lambat pada timeframe kecil
                            ii. jika ada posisi_futurres LONG, abaikan
                            iii. jika tidak ada posisi_futures SHORT, abaikan
                            iv. jika ada posisi_futures SHORT, abaikan (posisi SHORT akan tertutup secara optimal pada timeframe kecil)
                    b. SHORT_LONG: Saat k_lambat < d_lambat pada timeframe besar
                        Analisa posisi_futures:
                            i. jika tidak ada posisi_futures SHORT, BUKA_SHORT
                                i.1 k_lambat < d_lambat pada timeframe kecil
                            ii. jika ada posisi_futures SHORT, abaikan
                            iii. jika tidak ada posisi_futures LONG, abaikan
                            iv. jika ada posisi_futures LONG, abaikan (posisi LONG akan tertutup secara optimal pada timeframe kecil)
                2. Berdasarkan nilai dari HOLD_TRADE, strategi akan melakukan eksekusi pada timeframe kecil sebagai berikut:
                    a. HOLD_TRADE = 'LONG_SHORT':
                        i. BUKA_SHORT saat k_lambat < d_lambat pada timeframe kecil
                        ii. TUTUP_SHORT saat k_lambat >= d_lambat pada timeframe kecil
                    b. HOLD_TRADE = 'SHORT_LONG':
                        i. BUKA_LONG saat k_lambat >= d_lambat pada timeframe kecil
                        ii. TUTUP_LONG saat k_lambat < d_lambat pada timeframe kecil
            """

        return self.data_stokastik
