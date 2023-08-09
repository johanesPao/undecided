"""
Script untuk kelas Strategi
Script untuk implementasi strategi trading berdasarkan pertimbangan pribadi akan beberapa faktor 
seperti analisa teknikal
"""

import math
from typing import List, Literal

import pandas as pd
import numpy as np
from colorama import Fore, Style, init

from akun.akun import InfoAkun
from analisa.analisa_teknikal import AnalisaTeknikal
from baca_konfig import Inisiasi
from fungsi.fungsi import Fungsi
from model.model import Model
from tindakan.tindakan import Order
from ui.ui_sederhana import UI

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

init()


class Strategi:
    def __init__(
        self,
        simbol_data: str,
        simbol: str,
        exchange: str,
        leverage: int = 10,
        inter_eval: list[str] = [],
        inter_chart: list[str] = [],
        mode_harga_penutupan: bool = True,
        backtest: bool = False,
        jumlah_periode_backtest: int = 0,
        saldo_backtest: float = 0,
        jumlah_trade_usdt: float = 0,
        leverage_backtest: int = 10,
    ) -> None:
        self.inisiasi = Inisiasi()
        self.konektor_data = self.inisiasi.data()
        self.konektor_exchange = self.inisiasi.exchange()
        self.model = Model(self.konektor_data)
        self.analisa_teknikal = AnalisaTeknikal()
        self.akun = InfoAkun(self.konektor_exchange)
        (
            self.fee_tier,
            self.total_saldo,
            self.saldo_tersedia,
            self.saldo_terpakai,
            self.laba_rugi_terbuka,
            self.saldo_plus_profit,
            self.posisi_futures,
        ) = self.akun.akun_futures()
        self.simbol_data = simbol_data
        self.simbol = simbol
        self.order = Order(self.simbol)
        self.exchange = exchange
        self.leverage = leverage
        self.inter_eval = inter_eval
        self.inter_chart = inter_chart
        self.mode_harga_penutupan = mode_harga_penutupan
        self.backtest = backtest
        if not self.backtest:
            self.ui = UI()
        self.jumlah_periode_backtest = jumlah_periode_backtest
        if self.backtest and self.jumlah_periode_backtest <= 0:
            raise ValueError(
                f"Jika backtest={self.backtest}, maka jumlah_periode_backtest harus lebih besar dari 0."
            )
        self.saldo_backtest = saldo_backtest
        self.jumlah_trade_usdt = jumlah_trade_usdt
        self.leverage_backtest = leverage_backtest
        self.fungsi = Fungsi()
        self.HOLD_TRADE = ""
        self.kuantitas_long_nir = 0
        self.kuantitas_short_nir = 0
        self.MODE_SCALPING = ""
        self.kuantitas_long_rtw = 0
        self.kuantitas_short_rtw = 0
        self.kuantitas_long_rte = 0
        self.kuantitas_short_rte = 0
        self.kuantitas_long_svm = 0
        self.kuantitas_short_svm = 0
        self.kuantitas_long_dsha = 0
        self.kuantitas_short_dsha = 0

    def jpao_niten_ichi_ryu_28_16_8(
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
        ] = ["4 jam", "4 jam"],
        k_cepat: int = 28,
        k_lambat: int = 16,
        d_lambat: int = 8,
    ) -> None | list:
        self.interval = interval
        self.k_cepat = k_cepat
        self.k_lambat = k_lambat
        self.d_lambat = d_lambat
        self.dua = 2
        # state interval
        self.INTERVAL_SAMA = self.interval[0] == self.interval[1]

        if len(self.interval) != self.dua:
            return print(
                "STRATEGI INI (jpao_niten_ichi_ryu_28_16_8) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH DUA DAN KOMPONEN KEDUA HARUS LEBIH BESAR ATAU SAMA DENGAN KOMPONEN PERTAMA"
            )

        self.jumlah_bar = (
            self.k_cepat
            + self.k_lambat
            + self.d_lambat
            + (self.jumlah_periode_backtest if self.backtest else 0)
        )

        self.data_stokastik = []

        try:
            self.offset = self.fungsi.konverter_offset(
                self.interval[1],
                offset_kosong=True if self.interval[0] == self.interval[1] else False,
            )
        except ValueError as e:
            print(
                "KESALAHAN: Kami tidak dapat membaca interval waktu yang diberikan, pastikan interval waktu dalam list dengan dua komponen dimana komponen kedua adalah timeframe yang lebih besar atau sama dengan timeframe kecil (komponen pertama)"
            )

        for waktu in self.interval:
            self.interval_data = self.fungsi.konverter_waktu(waktu)

            self.df = self.model.ambil_data_historis(
                self.simbol_data, self.exchange, self.interval_data, self.jumlah_bar
            )

            self.df_ta = self.analisa_teknikal.stokastik(
                self.df, self.k_cepat, self.k_lambat, self.d_lambat, self.backtest
            )

            self.data_stokastik.append(self.df_ta)

        # FUNGSI SAAT LIVE
        def live(list_df_stokastik) -> str | None:
            # VARIABEL DAN KONSTANTA
            DATA_POSISI_FUTURES = self.posisi_futures
            # cek posisi aset yang dipegang saat ini
            POSISI = DATA_POSISI_FUTURES["positionSide"].unique().tolist()
            if "SHORT" in POSISI:
                data_short = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "SHORT"
                ]
                # kuantitas short yang perlu ditutup
                self.kuantitas_short_nir = abs(int(data_short.iloc[0]["positionAmt"]))
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                # kuantitas long yang perlu ditutup
                self.kuantitas_long_nir = int(data_long.iloc[0]["positionAmt"])

            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(
                self.jumlah_trade_usdt * self.leverage / harga_koin_terakhir
            )

            # set nilai k_lambat_tf_kecil, d_lambat_tf_kecil, k_lambat_tf_besar dan d_lambat_tf_besar
            # untuk evaluasi state strategi

            if not self.INTERVAL_SAMA:
                k_lambat_tf_kecil = list_df_stokastik[0].iloc[-1]["k_lambat"]
                d_lambat_tf_kecil = list_df_stokastik[0].iloc[-1]["d_lambat"]
                k_lambat_tf_kecil_sebelumnya = list_df_stokastik[0].iloc[-2]["k_lambat"]
                d_lambat_tf_kecil_sebelumnya = list_df_stokastik[0].iloc[-2]["d_lambat"]
            k_lambat_tf_besar = list_df_stokastik[1].iloc[-1]["k_lambat"]
            d_lambat_tf_besar = list_df_stokastik[1].iloc[-1]["d_lambat"]
            k_lambat_tf_besar_sebelumnya = list_df_stokastik[1].iloc[-2]["k_lambat"]
            d_lambat_tf_besar_sebelumnya = list_df_stokastik[1].iloc[-2]["d_lambat"]

            # set self.HOLD_TRADE sesuai kondisi pada timeframe besar
            self.HOLD_TRADE = (
                (
                    "LONG_SHORT"
                    if k_lambat_tf_besar >= d_lambat_tf_besar
                    else "SHORT_LONG"
                )
                if len(POSISI) != 0
                else (
                    "LONG_SHORT"
                    if k_lambat_tf_besar >= d_lambat_tf_besar
                    and k_lambat_tf_besar_sebelumnya < d_lambat_tf_besar_sebelumnya
                    else "SHORT_LONG"
                    if k_lambat_tf_besar < d_lambat_tf_besar
                    and k_lambat_tf_besar_sebelumnya >= d_lambat_tf_besar_sebelumnya
                    else "MENUNGGU_TREND"
                )
            )

            if not self.INTERVAL_SAMA:
                print(f"k_lambat pada TF kecil: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(k_lambat_tf_kecil, 5)}{Style.RESET_ALL}")  # type: ignore
                print(f"d_lambat pada TF kecil: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(d_lambat_tf_kecil, 5)}{Style.RESET_ALL}")  # type: ignore
                print(f"k_lambat pada TF besar: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(k_lambat_tf_besar, 5)}{Style.RESET_ALL}")  # type: ignore
                print(f"d_lambat pada TF besar: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(d_lambat_tf_besar, 5)}{Style.RESET_ALL}")  # type: ignore
            else:
                print(f"k_lambat: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(k_lambat_tf_besar, 5)}{Style.RESET_ALL}")  # type: ignore
                print(f"d_lambat: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(d_lambat_tf_besar, 5)}{Style.RESET_ALL}")  # type: ignore
            print(f"\nHARGA {self.simbol} TERAKHIR: {round(harga_koin_terakhir, 4)}")
            print(
                f"\nMODE STRATEGI: [{Fore.GREEN if self.HOLD_TRADE == 'LONG_SHORT' else Fore.RED if self.HOLD_TRADE == 'SHORT_LONG' else Fore.YELLOW}{self.HOLD_TRADE}{Style.RESET_ALL}]"
            )

            # STRATEGI HOLD
            # jika variabel self.HOLD_TRADE == 'LONG_SHORT'
            if self.HOLD_TRADE != "MENUNGGU_TREND":
                if self.HOLD_TRADE == "LONG_SHORT":
                    # jika tidak ada posisi LONG
                    # print("BUKA_LONG")
                    # jangan memaksakan diri untuk membuka posisi LONG
                    # jika timeframe kecil tidak mendukung
                    if "LONG" not in POSISI and (
                        k_lambat_tf_kecil >= d_lambat_tf_kecil  # type: ignore
                        if not self.INTERVAL_SAMA
                        else k_lambat_tf_besar >= d_lambat_tf_besar
                    ):
                        self.kuantitas_long_nir = self.order.buka_long(
                            kuantitas_koin, leverage=self.leverage
                        )
                    # jika k_lambat < d_lambat pada timeframe kecil
                    if (
                        k_lambat_tf_kecil < d_lambat_tf_kecil  # type: ignore
                        if not self.INTERVAL_SAMA
                        else k_lambat_tf_besar < d_lambat_tf_besar
                    ):
                        # jika tidak ada posisi SHORT
                        if "SHORT" not in POSISI:
                            self.kuantitas_short_nir = self.order.buka_short(
                                kuantitas_koin, leverage=self.leverage
                            )
                    # jika ada posisi SHORT
                    elif "SHORT" in POSISI and self.kuantitas_short_nir > 0:  # type: ignore
                        self.order.tutup_short(
                            self.kuantitas_short_nir, leverage=self.leverage
                        )
                        self.kuantitas_short_nir = 0
                # jika variabel self.HOLD_TRADE == 'SHORT_LONG
                elif self.HOLD_TRADE == "SHORT_LONG":
                    # jika tidak ada posisi SHORT
                    # print("BUKA_SHORT")
                    # jangan memaksakan diri untuk membuka posisi SHORT
                    # jika timeframe kecil tidak mendukung
                    if "SHORT" not in POSISI and (
                        k_lambat_tf_kecil < d_lambat_tf_kecil  # type: ignore
                        if not self.INTERVAL_SAMA
                        else k_lambat_tf_besar < d_lambat_tf_besar
                    ):
                        self.kuantitas_short_nir = self.order.buka_short(
                            kuantitas_koin, leverage=self.leverage
                        )
                    # jika k_lambat >= d_lambat pada timeframe kecil
                    if (
                        k_lambat_tf_kecil >= d_lambat_tf_kecil  # type: ignore
                        if not self.INTERVAL_SAMA
                        else k_lambat_tf_besar >= d_lambat_tf_besar
                    ):
                        # jika tidak ada posisi LONG
                        if "LONG" not in POSISI:
                            self.kuantitas_long_nir = self.order.buka_long(
                                kuantitas_koin, leverage=self.leverage
                            )
                    # jika ada posisi LONG
                    elif "LONG" in POSISI and self.kuantitas_long_nir > 0:  # type: ignore
                        self.order.tutup_long(
                            self.kuantitas_long_nir, leverage=self.leverage
                        )
                        self.kuantitas_long_nir = 0

        # FUNGSI SAAT BACKTEST
        def backtest(list_df_stokastik) -> str:
            # VARIABEL DAN KONSTANTA
            # SALDO = self.saldo_backtest
            # LEVERAGE = self.leverage_backtest
            # STOKASTIK = list_df_stokastik

            if isinstance(list_df_stokastik, list):
                # iterrows pada timeframe kecil
                list_akhir = []
                df_backtest = pd.DataFrame()

                # pembentukan df inisial waktu_tf_kecil, close_tf_kecil, k_lambat_tf_kecil, d_lambat_tf_kecil, waktu_tf_besar, k_lambat_tf_besar, d_lambat_tf_besar
                # type: ignore : pasti mengembalikan list
                for baris in list_df_stokastik[0].iterrows():
                    # kembalikan waktu_tf_kecil, waktu_tf_besar, k_lambat_tf_kecil,
                    # d_lambat_tf_kecil, k_lambat_tf_besar, d_lambat_tf_besar
                    waktu_tf_kecil = baris[0]
                    tinggi_tf_kecil = baris[1]["high"]
                    rendah_tf_kecil = baris[1]["low"]
                    close_tf_kecil = baris[1]["close"]
                    k_lambat_tf_kecil = baris[1]["k_lambat"]
                    d_lambat_tf_kecil = baris[1]["d_lambat"]
                    # slice dataframe tf_besar dengan waktu_tf_besar <= waktu_tf_kecil
                    # timeframe besar yang berbeda membutuhkan offset yang berbeda
                    df_tf_besar = list_df_stokastik[1][
                        list_df_stokastik[1].index <= (waktu_tf_kecil - self.offset)
                    ].iloc[-1:, :]
                    tinggi_tf_besar = df_tf_besar.iloc[-1]["high"]
                    rendah_tf_besar = df_tf_besar.iloc[-1]["low"]
                    close_tf_besar = df_tf_besar.iloc[-1]["close"]
                    waktu_tf_besar = df_tf_besar.index[0]
                    k_lambat_tf_besar = df_tf_besar.iloc[-1]["k_lambat"]
                    d_lambat_tf_besar = df_tf_besar.iloc[-1]["d_lambat"]
                    # list umum untuk beda interval dan sama interval
                    list_interval_umum = [
                        waktu_tf_besar,
                        tinggi_tf_besar,
                        rendah_tf_besar,
                        close_tf_besar,
                        k_lambat_tf_besar,
                        d_lambat_tf_besar,
                    ]
                    # jika interval berbeda
                    if not self.INTERVAL_SAMA:
                        list_interval_beda = [
                            waktu_tf_kecil,
                            tinggi_tf_kecil,
                            rendah_tf_kecil,
                            close_tf_kecil,
                            k_lambat_tf_kecil,
                            d_lambat_tf_kecil,
                        ]
                        for i in range(len(list_interval_umum)):
                            list_interval_beda.append(list_interval_umum[i])
                    list_akhir.append(
                        list_interval_umum
                        if self.INTERVAL_SAMA
                        else list_interval_beda  # type: ignore
                    )
                    # list kolom umum
                    list_kolom_umum = [
                        "waktu_tf_besar",
                        "tinggi_tf_besar",
                        "rendah_tf_besar",
                        "close_tf_besar",
                        "k_lambat_tf_besar",
                        "d_lambat_tf_besar",
                    ]
                    # tambahan list kolom interval beda
                    if not self.INTERVAL_SAMA:
                        list_kolom_int_beda = [
                            "waktu_tf_kecil",
                            "tinggi_tf_kecil",
                            "rendah_tf_kecil",
                            "close_tf_kecil",
                            "k_lambat_tf_kecil",
                            "d_lambat_tf_kecil",
                        ]
                        for i in range(len(list_kolom_umum)):
                            list_kolom_int_beda.append(list_kolom_umum[i])
                    df_backtest = pd.DataFrame(
                        list_akhir,
                        columns=list_kolom_umum if self.INTERVAL_SAMA else list_kolom_int_beda,  # type: ignore
                    )

                # iterasi pada dataframe untuk kolom tindakan, posisi, harga_long, harga_short
                HOLD_TRADE = ""
                posisi = []
                harga_long = []
                harga_short = []
                list_df_mode = []
                list_df_posisi = []
                list_df_tindakan = []
                list_df_harga_long = []
                list_df_harga_short = []
                for baris in range(len(df_backtest)):
                    tindakan = []
                    mode = []
                    harga = (
                        df_backtest.iloc[baris]["close_tf_kecil"]
                        if not self.INTERVAL_SAMA
                        else df_backtest.iloc[baris]["close_tf_besar"]
                    )
                    rendah = (
                        df_backtest.iloc[baris]["rendah_tf_kecil"]
                        if not self.INTERVAL_SAMA
                        else df_backtest.iloc[baris]["rendah_tf_besar"]
                    )
                    tinggi = (
                        df_backtest.iloc[baris]["tinggi_tf_kecil"]
                        if not self.INTERVAL_SAMA
                        else df_backtest.iloc[baris]["tinggi_tf_besar"]
                    )
                    if not self.INTERVAL_SAMA:
                        k_lambat_tf_kecil = df_backtest.iloc[baris]["k_lambat_tf_kecil"]
                        d_lambat_tf_kecil = df_backtest.iloc[baris]["d_lambat_tf_kecil"]
                    k_lambat_tf_besar = df_backtest.iloc[baris]["k_lambat_tf_besar"]
                    d_lambat_tf_besar = df_backtest.iloc[baris]["d_lambat_tf_besar"]
                    k_lambat_tf_besar_sebelumnya = df_backtest.iloc[baris - 1][
                        "k_lambat_tf_besar"
                    ]
                    d_lambat_tf_besar_sebelumnya = df_backtest.iloc[baris - 1][
                        "d_lambat_tf_besar"
                    ]

                    HOLD_TRADE = (
                        ("MENUNGGU_TREND")
                        if baris == 0
                        else (
                            "LONG_SHORT"
                            if k_lambat_tf_besar >= d_lambat_tf_besar
                            else "SHORT_LONG"
                        )
                        if len(posisi) != 0
                        else (
                            "LONG_SHORT"
                            if k_lambat_tf_besar >= d_lambat_tf_besar
                            and k_lambat_tf_besar_sebelumnya
                            < d_lambat_tf_besar_sebelumnya
                            else "SHORT_LONG"
                            if k_lambat_tf_besar < d_lambat_tf_besar
                            and k_lambat_tf_besar_sebelumnya
                            >= d_lambat_tf_besar_sebelumnya
                            else "MENUNGGU_TREND"
                        )
                    )

                    mode.append(HOLD_TRADE)

                    # Cek semua posisi pada masing - masing interval,
                    # jika ada posisi short atau long dengan
                    # percentage loss * leverage >= 100% anggap terkena
                    # margin call dan hapus posisi
                    if (
                        "LONG" in posisi
                        and (rendah - harga_long) / harga_long * self.leverage_backtest
                        <= -0.8
                    ):
                        tindakan.append("MARGIN_CALL_LONG")
                        posisi.remove("LONG")
                        harga_long.clear()
                    if (
                        "SHORT" in posisi
                        and (harga_short - tinggi)
                        / harga_short
                        * self.leverage_backtest
                        <= -0.8
                    ):
                        tindakan.append("MARGIN_CALL_SHORT")
                        posisi.remove("SHORT")
                        harga_short.clear()

                    if HOLD_TRADE != "MENUNGGU_TREND":
                        if (
                            HOLD_TRADE == "LONG_SHORT"
                            and k_lambat_tf_besar_sebelumnya
                            < d_lambat_tf_besar_sebelumnya
                        ):
                            if "LONG" not in posisi and (
                                k_lambat_tf_kecil >= d_lambat_tf_kecil  # type: ignore
                                if not self.INTERVAL_SAMA
                                else k_lambat_tf_besar >= d_lambat_tf_besar
                            ):
                                tindakan.append("BUKA_LONG")
                                posisi.append("LONG")
                                harga_long.append(harga)
                            if (
                                k_lambat_tf_kecil < d_lambat_tf_kecil  # type: ignore
                                if not self.INTERVAL_SAMA
                                else k_lambat_tf_besar < d_lambat_tf_besar
                            ):
                                if "SHORT" not in posisi:
                                    tindakan.append("BUKA_SHORT")
                                    posisi.append("SHORT")
                                    harga_short.append(harga)
                            elif "SHORT" in posisi:
                                tindakan.append("TUTUP_SHORT")
                                posisi.remove("SHORT")
                                harga_short.clear()
                        elif (
                            HOLD_TRADE == "SHORT_LONG"
                            and k_lambat_tf_besar_sebelumnya
                            >= d_lambat_tf_besar_sebelumnya
                        ):
                            if "SHORT" not in posisi and (
                                k_lambat_tf_kecil < d_lambat_tf_kecil  # type: ignore
                                if not self.INTERVAL_SAMA
                                else k_lambat_tf_besar < d_lambat_tf_besar
                            ):
                                tindakan.append("BUKA_SHORT")
                                posisi.append("SHORT")
                                harga_short.append(harga)
                            if (
                                k_lambat_tf_kecil >= d_lambat_tf_kecil  # type: ignore
                                if not self.INTERVAL_SAMA
                                else k_lambat_tf_besar >= d_lambat_tf_besar
                            ):
                                if "LONG" not in posisi:
                                    tindakan.append("BUKA_LONG")
                                    posisi.append("LONG")
                                    harga_long.append(harga)
                            elif "LONG" in posisi:
                                tindakan.append("TUTUP_LONG")
                                posisi.remove("LONG")
                                harga_long.clear()

                    list_df_tindakan.append(tindakan)
                    list_df_mode.append(mode)
                    list_df_posisi.append(posisi.copy())
                    list_df_harga_long.append(harga_long.copy())
                    list_df_harga_short.append(harga_short.copy())

                df_backtest["mode"] = list_df_mode
                df_backtest["tindakan"] = list_df_tindakan
                df_backtest["posisi"] = list_df_posisi
                df_backtest["harga_long"] = list_df_harga_long
                df_backtest["harga_short"] = list_df_harga_short

                # iterasi kolom untung_rugi
                list_df_profit_dan_loss = []
                list_df_saldo_tersedia = []
                list_df_saldo_short = []
                list_df_saldo_long = []
                saldo_long = 0
                saldo_short = 0
                for baris in range(len(df_backtest)):
                    profit_dan_loss = 0
                    if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = (
                            df_backtest.iloc[baris]["close_tf_kecil"]
                            if not self.INTERVAL_SAMA
                            else df_backtest.iloc[baris]["close_tf_besar"]
                        )
                        harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                        profit_dan_loss = (
                            (harga_keluar - harga_long)
                            / harga_long
                            * saldo_long
                            * self.leverage_backtest
                        ) - (0.031 * saldo_long)
                        self.saldo_backtest = (
                            self.saldo_backtest + saldo_long + profit_dan_loss
                        )
                        saldo_long = 0
                    if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = (
                            df_backtest.iloc[baris]["close_tf_kecil"]
                            if not self.INTERVAL_SAMA
                            else df_backtest.iloc[baris]["close_tf_besar"]
                        )
                        harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                        profit_dan_loss = (
                            (harga_short - harga_keluar)
                            / harga_short
                            * saldo_short
                            * self.leverage_backtest
                        ) - (0.031 * saldo_short)
                        self.saldo_backtest = (
                            self.saldo_backtest + saldo_short + profit_dan_loss
                        )
                        saldo_short = 0
                    if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        profit_dan_loss = -saldo_short - (
                            saldo_short * 0.031 / self.leverage_backtest
                        )
                        self.saldo_backtest = (
                            self.saldo_backtest + saldo_short + profit_dan_loss
                        )
                        saldo_short = 0
                    if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        profit_dan_loss = -saldo_long - (
                            saldo_long * 0.01 / self.leverage_backtest
                        )
                        self.saldo_backtest = (
                            self.saldo_backtest + saldo_long + profit_dan_loss
                        )
                        saldo_long = 0
                    # NOTES: Penggunaan saldo untuk pembukaan posisi tidak harus setengah atau seluruh saldo, tapi akan
                    # selalu merujuk kepada saldo + saldo_posisi jika ada dibagi dua atau saldo tersedia
                    # jika saldo tersedia < saldo + saldo_posisi dibagi dua
                    if "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        # # HALF INVESTMENT STRATEGY
                        # # jika baris pertama dalam iterrows
                        # if baris == 0:
                        #     saldo_long = 0.5 * self.saldo_backtest
                        #     self.saldo_backtest = self.saldo_backtest - saldo_long
                        # else:
                        #     # jika ada posisi short pada timeframe sebelumnya dan ditutup pada timeframe ini maka gunakan setengah saldo yang ada
                        #     if "SHORT" in df_backtest.iloc[baris - 1]["posisi"] and (
                        #         "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]
                        #         or "MARGIN_CALL_SHORT"
                        #         in df_backtest.iloc[baris]["tindakan"]
                        #     ):
                        #         saldo_long = 0.5 * SALDO
                        #         self.saldo_backtest = self.saldo_backtest - saldo_long
                        #     else:
                        #         saldo_long = min((self.saldo_backtest + saldo_short) / 2, self.saldo_backtest)
                        #         self.saldo_backtest = self.saldo_backtest - saldo_long
                        saldo_long = min(self.saldo_backtest, 3.3)
                        self.saldo_backtest = self.saldo_backtest - saldo_long
                    if "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        # # HALF INVESTMENT STRATEGY
                        # # jika baris pertama dalam iterrows
                        # if baris == 0:
                        #     saldo_short = 0.5 * SALDO
                        #     self.saldo_backtest = self.saldo_backtest - saldo_short
                        # else:
                        #     # jika ada posisi long pada timeframe sebelumnya dan ditutup pada timeframe ini maka gunakan setengah saldo yang ada
                        #     if "LONG" in df_backtest.iloc[baris - 1]["posisi"] and (
                        #         "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]
                        #         or "MARGIN_CALL_LONG"
                        #         in df_backtest.iloc[baris]["tindakan"]
                        #     ):
                        #         saldo_short = 0.5 * self.saldo_backtest
                        #         self.saldo_backtest = self.saldo_backtest - saldo_short
                        #     else:
                        #         saldo_short = min((self.saldo_backtest + saldo_long) / 2, self.saldo_backtest)
                        #         self.saldo_backtest = self.saldo_backtest - saldo_short
                        saldo_short = min(self.saldo_backtest, 3.3)
                        self.saldo_backtest = self.saldo_backtest - saldo_short
                    list_df_saldo_tersedia.append(self.saldo_backtest)
                    list_df_saldo_long.append(saldo_long)
                    list_df_saldo_short.append(saldo_short)
                    list_df_profit_dan_loss.append(profit_dan_loss)
                df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
                df_backtest["saldo_long"] = list_df_saldo_long
                df_backtest["saldo_short"] = list_df_saldo_short
                df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

                # print(k_lambat_tf_kecil)

                print(df_backtest.to_string())
            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"]))} dollar.'  # type: ignore

        # jika live stream strategi
        if not self.backtest:
            live(self.data_stokastik)
        else:
            print(backtest(self.data_stokastik))

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

    def jpao_ride_the_wave(
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
        ] = ["15 menit"],
        periode_ma_cepat: int = 7,
        periode_ma_lambat: int = 9,
    ) -> None | list:
        self.interval = interval
        self.periode_ma_cepat = periode_ma_cepat
        self.periode_ma_lambat = periode_ma_lambat

        if len(self.interval) != 1:
            return print(
                "STRATEGI INI (jpao_ride_the_wave) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH SATU"
            )

        # if self.periode_ma < self.k_cepat + self.k_lambat + self.d_lambat:  # type: ignore
        #     return print(
        #         "JUMLAH PARAMETER k_cepat, k_lambat dan d_lambat HARUS LEBIH KECIL DARI periode_ma"
        #     )

        self.jumlah_bar = (
            self.jumlah_periode_backtest
            + max(self.periode_ma_cepat, self.periode_ma_lambat)
            + 1
            if self.backtest
            else max(self.periode_ma_cepat, self.periode_ma_lambat) + 2
        )

        waktu = self.fungsi.konverter_waktu(self.interval[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        self.df_ma_cepat = self.analisa_teknikal.moving_average(
            self.df, self.periode_ma_cepat, backtest=self.backtest
        )
        self.df_ma_lambat = self.analisa_teknikal.moving_average(
            self.df, self.periode_ma_lambat, backtest=self.backtest
        )

        if self.df_ma_cepat is not None and self.df_ma_lambat is not None:
            self.df["ma_cepat"] = self.df_ma_cepat["ma"]
            self.df["ma_lambat"] = self.df_ma_lambat["ma"]

        self.df.dropna(subset=["ma_cepat", "ma_lambat"], inplace=True)

        self.data.append(self.df)

        # FUNGSI SAAT LIVE
        def live(list_data: list = self.data) -> str | None:
            # VARIABEL DAN KONSTANTA
            DATA_POSISI_FUTURES = self.posisi_futures
            # cek posisi aset yang dipegang saat ini
            POSISI = DATA_POSISI_FUTURES["positionSide"].unique().tolist()
            if "SHORT" in POSISI:
                data_short = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "SHORT"
                ]
                # kuantitas short yang perlu ditutup
                self.kuantitas_short_rtw = abs(int(data_short.iloc[0]["positionAmt"]))
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                # kuantitas long yang perlu ditutup
                self.kuantitas_long_rtw = int(data_long.iloc[0]["positionAmt"])

            TRADE_USDT = self.jumlah_trade_usdt
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(TRADE_USDT * self.leverage / harga_koin_terakhir)

            ma_cepat = list_data[0].iloc[-1]["ma_cepat"]
            ma_cepat_sebelumnya = list_data[0].iloc[-2]["ma_cepat"]
            ma_lambat = list_data[0].iloc[-1]["ma_lambat"]
            ma_lambat_sebelumnya = list_data[0].iloc[-2]["ma_lambat"]

            harga_penutupan = list_data[0].iloc[-1]["close"]

            MODE_SCALPING = (
                ("MA_NAIK" if ma_cepat >= ma_lambat else "MA_TURUN")
                if len(POSISI) != 0
                else (
                    "MA_NAIK"
                    if ma_cepat >= ma_lambat
                    and ma_cepat_sebelumnya < ma_lambat_sebelumnya
                    else "MA_TURUN"
                    if ma_cepat < ma_lambat
                    and ma_cepat_sebelumnya >= ma_lambat_sebelumnya
                    else "MENUNGGU_TREND"
                )
            )

            self.ui.label_nilai(
                label="Harga Penutupan terakhir", nilai=harga_penutupan, spasi_label=50
            )
            print("")
            self.ui.label_nilai(
                label=f"Moving Average Cepat ({self.periode_ma_cepat}) [-1]",
                nilai=round(ma_cepat_sebelumnya, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Moving Average Lambat ({self.periode_ma_lambat}) [-1]",
                nilai=round(ma_lambat_sebelumnya, 8),
                spasi_label=50,
            )
            print("")
            self.ui.label_nilai(
                label=f"Moving Average Cepat ({self.periode_ma_cepat}) [0]",
                nilai=round(ma_cepat, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Moving Average Lambat ({self.periode_ma_lambat}) [0]",
                nilai=round(ma_lambat, 8),
                spasi_label=50,
            )
            print(
                f"\nMODE STRATEGI: \nRIDE THE WAVE (fast_ma: {self.periode_ma_cepat}; slow_ma: {self.periode_ma_lambat}) {Fore.YELLOW if MODE_SCALPING == 'MENUNGGU_TREND' else Fore.RED if ma_cepat < ma_lambat else Fore.GREEN}[{MODE_SCALPING}]{Style.RESET_ALL}"
            )

            if MODE_SCALPING != "MENUNGGU_TREND":
                if MODE_SCALPING == "MA_NAIK":
                    if "SHORT" in POSISI and self.kuantitas_short_rtw > 0:
                        self.order.tutup_short(
                            self.kuantitas_short_rtw, leverage=self.leverage
                        )
                        self.kuantitas_short_rtw = 0
                    if "LONG" not in POSISI:
                        self.kuantitas_long_rtw = self.order.buka_long(
                            kuantitas_koin, leverage=self.leverage
                        )
                elif MODE_SCALPING == "MA_TURUN":
                    if "LONG" in POSISI and self.kuantitas_long_rtw > 0:
                        self.order.tutup_long(
                            self.kuantitas_long_rtw, leverage=self.leverage
                        )
                        self.kuantitas_long_rtw = 0
                    if "SHORT" not in POSISI:
                        self.kuantitas_short_rtw = self.order.buka_short(
                            kuantitas_koin, leverage=self.leverage
                        )

        # FUNGSI BACKTEST
        def backtest(list_data: list = self.data) -> str:
            # VARIABEL DAN KONSTANTA
            SALDO = self.saldo_backtest
            TRADE_USDT = self.jumlah_trade_usdt
            LEVERAGE = self.leverage_backtest
            DATA = list_data

            df_backtest = pd.DataFrame(DATA[0])

            MODE_SCALPING = ""
            posisi = []
            harga_posisi = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_harga_posisi = []
            for baris in range(len(df_backtest)):
                tindakan = []
                harga = df_backtest.iloc[baris]["close"]
                rendah = df_backtest.iloc[baris]["low"]
                tinggi = df_backtest.iloc[baris]["high"]
                ma_cepat = df_backtest.iloc[baris]["ma_cepat"]
                ma_cepat_sebelumnya = df_backtest.iloc[baris - 1]["ma_cepat"]
                ma_lambat = df_backtest.iloc[baris]["ma_lambat"]
                ma_lambat_sebelumnya = df_backtest.iloc[baris - 1]["ma_lambat"]

                # Cek semua posisi pada masing - masing interval,
                # jika ada posisi short atau long dengan
                # percentage loss * leverage >= 100% anggap terkena
                # margin call dan hapus posisi
                if (
                    "LONG" in posisi
                    and (rendah - harga_posisi) / harga_posisi * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_LONG")
                    posisi.remove("LONG")
                    harga_posisi.clear()
                if (
                    "SHORT" in posisi
                    and (harga_posisi - tinggi) / harga_posisi * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_SHORT")
                    posisi.remove("SHORT")
                    harga_posisi.clear()

                MODE_SCALPING = (
                    ("MA_NAIK" if ma_cepat >= ma_lambat else "MA_TURUN")
                    if len(posisi) != 0
                    else (
                        "MA_NAIK"
                        if ma_cepat >= ma_lambat
                        and ma_cepat_sebelumnya < ma_lambat_sebelumnya
                        else "MA_TURUN"
                        if ma_cepat < ma_lambat
                        and ma_cepat_sebelumnya >= ma_lambat_sebelumnya
                        else "MENUNGGU_TREND"
                    )
                )

                if MODE_SCALPING != "MENUNGGU_TREND":
                    if MODE_SCALPING == "MA_NAIK":
                        if "SHORT" in posisi:
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_posisi.clear()
                        if "LONG" not in posisi:
                            tindakan.append("BUKA_LONG")
                            posisi.append("LONG")
                            harga_posisi.append(harga)
                    elif MODE_SCALPING == "MA_TURUN":
                        if "LONG" in posisi:
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_posisi.clear()
                        if "SHORT" not in posisi:
                            tindakan.append("BUKA_SHORT")
                            posisi.append("SHORT")
                            harga_posisi.append(harga)

                list_df_tindakan.append(tindakan)
                list_df_posisi.append(posisi.copy())
                list_df_harga_posisi.append(harga_posisi.copy())

            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_posisi"] = list_df_harga_posisi

            # iterasi kolom untung_rugi
            list_df_profit_dan_loss = []
            list_df_saldo_tersedia = []
            list_df_saldo_posisi = []
            saldo_posisi = 0
            for baris in range(len(df_backtest)):
                profit_dan_loss = 0
                if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_keluar - harga_posisi
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (0.016 * saldo_posisi)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_posisi - harga_keluar
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (0.016 * saldo_posisi)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = -saldo_posisi - (saldo_posisi * 0.016)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = -saldo_posisi - (saldo_posisi * 0.016)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if (
                    "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]
                    or "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]
                ):
                    saldo_posisi = TRADE_USDT
                    SALDO = SALDO - saldo_posisi

                list_df_saldo_tersedia.append(SALDO)
                list_df_saldo_posisi.append(saldo_posisi)
                list_df_profit_dan_loss.append(profit_dan_loss)

            df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
            df_backtest["saldo_posisi"] = list_df_saldo_posisi
            df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

            print(df_backtest.to_string())

            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"]))} dollar'  # type: ignore

        # jika live stream strategi
        if not self.backtest:
            live()
        else:
            print(backtest())

    def jpao_ride_the_ema(
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
        ] = ["5 menit"],
        periode_ema: int = 50,
        smoothing: int = 2,
        dual_ema: bool = False,
        periode_ema_cepat: int = 37,
        demastoch: bool = False,
        k_cepat: int = 60,
        k_lambat: int = 70,
        d_lambat: int = 30,
    ) -> None | list:
        self.interval = interval
        self.periode_ema = periode_ema
        self.demastoch = demastoch
        if self.demastoch:
            self.k_cepat = k_cepat
            self.k_lambat = k_lambat
            self.d_lambat = d_lambat
        self.dual_ema = dual_ema
        if self.dual_ema:
            self.periode_ema_cepat = periode_ema_cepat
        # nilai EMA baru menunjukkan nilai yang benar saat data historikal adalah minimal 600 periode
        self.multiplier = math.ceil(
            5000 / self.periode_ema
            if not self.dual_ema
            else max(self.periode_ema, self.periode_ema_cepat)
        )
        if self.dual_ema:
            self.periode_ema_mod = (
                max(self.periode_ema, self.periode_ema_cepat) * self.multiplier
            )
        else:
            self.periode_ema_mod = self.periode_ema * 3
        self.smoothing = smoothing

        if len(self.interval) != 1:
            return print(
                "STRATEGI INI (jpao_ride_the_ema) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH SATU"
            )

        if self.demastoch and not self.dual_ema:
            return print(
                "FITUR DEMASTOCH HANYA BISA DIGUNAKAN BERSAMAAN DENGAN FITUR DUAL EMMA"
            )

        if self.dual_ema and self.periode_ema <= self.periode_ema_cepat:
            return print("PERIODE EMA CEPAT HARUS LEBIH KECIL DARI PERIODE EMA")

        self.jumlah_bar = (
            (
                self.jumlah_periode_backtest + self.periode_ema_mod
                if self.backtest
                else self.periode_ema_mod
            )
            if not self.demastoch
            else (
                self.jumlah_periode_backtest
                + max(
                    self.periode_ema_mod, self.k_cepat + self.k_lambat + self.d_lambat
                )
                if self.backtest
                else max(
                    self.periode_ema_mod, self.k_cepat + self.k_lambat + self.d_lambat
                )
            )
        )

        waktu = self.fungsi.konverter_waktu(self.interval[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        self.df_ema = (
            self.analisa_teknikal.ema(
                data=self.df,
                periode=self.periode_ema,
                smoothing=self.smoothing,
                backtest=self.backtest,
            )
            if not self.dual_ema
            else self.analisa_teknikal.ema(
                data=self.df,
                periode=self.periode_ema,
                smoothing=self.smoothing,
                dual_ema=True,
                periode_ema_cepat=self.periode_ema_cepat,
                backtest=self.backtest,
            )
        )

        if self.demastoch:
            self.df_stokastik = self.analisa_teknikal.stokastik(
                self.df,
                self.k_cepat,
                self.k_lambat,
                self.d_lambat,
                backtest=self.backtest,
            )
            self.df_ema["k_lambat"] = self.df_stokastik["k_lambat"]
            self.df_ema["d_lambat"] = self.df_stokastik["d_lambat"]
            self.df_ema.dropna(subset=["k_lambat", "d_lambat"], inplace=True)

        self.df_ema = self.df_ema.iloc[-self.jumlah_periode_backtest :]

        self.data.append(self.df_ema)

        # FUGNSI SAAT LIVE
        def live(list_data: list = self.data) -> str | None:
            # VARIABEL DAN KONSTANTA
            DATA_POSISI_FUTURES = self.posisi_futures
            # cek posisi yang dipegang saat ini
            POSISI = DATA_POSISI_FUTURES["positionSide"].unique().tolist()
            if "SHORT" in POSISI:
                data_short = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "SHORT"
                ]
                # kuantitas short yang perlu ditutup
                self.kuantitas_short_rte = abs(int(data_short.iloc[0]["positionAmt"]))
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                # kuantitas long yang perlu ditutup
                self.kuantitas_long_rte = int(data_long.iloc[0]["positionAmt"])

            USDT_AKUN = 2
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(USDT_AKUN * self.leverage / harga_koin_terakhir)

            ema = list_data[0].iloc[-1]["ema"]  # - 0.000110
            ema_sebelumnya = list_data[0].iloc[-2]["ema"]

            if self.dual_ema:
                ema_cepat = list_data[0].iloc[-1]["ema_cepat"]
                ema_cepat_sebelumnya = list_data[0].iloc[-2]["ema_cepat"]

            harga_penutupan_terakhir = list_data[0].iloc[-1]["close"]
            harga_penutupan_sebelumnya = list_data[0].iloc[-2]["close"]

            MODE_EMA = (
                (
                    ("DIATAS_EMA" if harga_penutupan_terakhir > ema else "DIBAWAH_EMA")
                    if len(POSISI) != 0
                    else (
                        "MENUNGGU_TREND"
                        if (
                            harga_penutupan_sebelumnya <= ema_sebelumnya
                            and harga_penutupan_terakhir <= ema
                        )
                        or (
                            harga_penutupan_sebelumnya > ema_sebelumnya
                            and harga_penutupan_terakhir > ema
                        )
                        else "DIATAS_EMA"
                        if harga_penutupan_sebelumnya <= ema_sebelumnya
                        and harga_penutupan_terakhir > ema
                        else "DIBAWAH_EMA"
                    )
                )
                if not self.dual_ema
                else (
                    ("EMA_NAIK" if ema_cepat > ema else "EMA_TURUN")  # type: ignore
                    if len(POSISI) != 0
                    else (
                        "MENUNGGU_TREND"
                        if (ema_cepat_sebelumnya <= ema_sebelumnya and ema_cepat <= ema)  # type: ignore
                        or (ema_cepat_sebelumnya > ema_sebelumnya and ema_cepat > ema)  # type: ignore
                        else "EMA_NAIK"
                        if ema_cepat_sebelumnya <= ema_sebelumnya and ema_cepat > ema  # type: ignore
                        else "EMA_TURUN"
                    )
                )
            )

            if not self.dual_ema:
                print(
                    f"Harga Penutupan sebelumnya: {Fore.GREEN if harga_penutupan_sebelumnya > ema_sebelumnya else Fore.RED}{harga_penutupan_sebelumnya}{Style.RESET_ALL}"
                )
                print(
                    f"Harga Penutupan terakhir: {Fore.GREEN if harga_penutupan_terakhir > ema else Fore.RED}{harga_penutupan_terakhir}{Style.RESET_ALL}"
                )
                print(f"\nSebelumnya:")
                print(
                    f"Exponential Moving Average: {Fore.RED if harga_penutupan_sebelumnya <= ema_sebelumnya else Fore.GREEN}{round(ema_sebelumnya, 4)}{Style.RESET_ALL}"
                )
                print(f"\nTerakhir:")
                print(
                    f"Exponential Moving Average terakhir: {Fore.RED if harga_penutupan_terakhir <= ema else Fore.GREEN}{round(ema, 4)}{Style.RESET_ALL}"
                )

                print(
                    f"\nMODE STRATEGI: \nRIDE THE EMA {Fore.RED if harga_penutupan_terakhir <= ema else Fore.GREEN}[{MODE_EMA}]{Style.RESET_ALL}"
                )
            else:
                if not self.demastoch:
                    self.ui.label_nilai(
                        label="Harga Penutupan terakhir",
                        nilai=harga_penutupan_terakhir,
                        spasi_label=35,
                    )
                    print(f"\nSebelumnya:")
                    self.ui.label_nilai(
                        label="Exponential Moving Average",
                        nilai=round(ema_sebelumnya, 6),
                        spasi_label=35,
                    )
                    self.ui.label_nilai(
                        label="Exponential Moving Average [Cepat]",
                        nilai=round(ema_cepat_sebelumnya, 6),  # type: ignore
                        spasi_label=35,
                    )
                    print(f"\nTerakhir:")
                    self.ui.label_nilai(
                        label="Exponential Moving Average",
                        nilai=round(ema, 6),
                        spasi_label=35,
                    )
                    self.ui.label_nilai(
                        label="Exponential Moving Average [Cepat]",
                        nilai=round(ema_cepat, 6),  # type: ignore
                        spasi_label=35,
                    )
                    print(
                        f"\nMODE STRATEGI: \nRIDE THE EMA - DUAL EMA {Fore.RED if ema_cepat <= ema else Fore.GREEN}[{MODE_EMA}]{Style.RESET_ALL}"  # type: ignore
                    )
                else:
                    print(
                        f"Harga Penutupan terakhir: {Fore.GREEN if harga_penutupan_terakhir > ema_cepat else Fore.RED}{harga_penutupan_terakhir}{Style.RESET_ALL}"  # type: ignore
                    )
                    print(f"\nSebelumnya:")
                    print(
                        f"Exponential Moving Average\t\t: {Fore.RED if ema_cepat_sebelumnya <= ema_sebelumnya else Fore.GREEN}{round(ema_sebelumnya, 4)}{Style.RESET_ALL}"  # type: ignore
                    )
                    print(
                        f"Exponential Moving Average [Cepat]\t\t: {Fore.RED if ema_cepat_sebelumnya <= ema_sebelumnya else Fore.GREEN}{round(ema_cepat_sebelumnya, 4)}{Style.RESET_ALL}"  # type: ignore
                    )
                    print(f"\nTerakhir:")
                    print(
                        f"Exponential Moving Average\t\t: {Fore.RED if ema_cepat <= ema else Fore.GREEN}{round(ema, 4)}{Style.RESET_ALL}"  # type: ignore
                    )
                    print(
                        f"Exponential Moving Average [Cepat]\t\t: {Fore.RED if ema_cepat <= ema else Fore.GREEN}{round(ema_cepat, 4)}{Style.RESET_ALL}"  # type:ignore
                    )

                    print(
                        f"\nMODE STRATEGI: \nRIDE THE EMA [] - DUAL EMA {Fore.RED if ema_cepat <= ema else Fore.GREEN}[{MODE_EMA}]{Style.RESET_ALL} - STOKASTIK {Fore.RED}[]{Style.RESET_ALL}"  # type: ignore
                    )

            if not self.dual_ema:
                if MODE_EMA != "MENUNGGU_TREND":
                    if MODE_EMA == "DIATAS_EMA":
                        # cek posisi short dan tutup
                        if "SHORT" in POSISI and self.kuantitas_short_rte > 0:
                            self.order.tutup_short(
                                self.kuantitas_short_rte, leverage=self.leverage
                            )
                            self.kuantitas_short_rte = 0
                        if "LONG" not in POSISI:
                            self.kuantitas_long_rte = self.order.buka_long(
                                kuantitas_koin, leverage=self.leverage
                            )
                    else:
                        # cek posisi long dan tutup
                        if "LONG" in POSISI and self.kuantitas_long_rte > 0:
                            self.order.tutup_long(
                                self.kuantitas_long_rte, leverage=self.leverage
                            )
                            self.kuantitas_long_rte = 0
                        if "SHORT" not in POSISI:
                            self.kuantitas_short_rte = self.order.buka_short(
                                kuantitas_koin, leverage=self.leverage
                            )
            else:
                if MODE_EMA != "MENUNGGU_TREND":
                    if MODE_EMA == "EMA_NAIK":
                        # cek posisi short dan tutup
                        if (
                            "SHORT" in POSISI and self.kuantitas_short_rte > 0
                        ):  # and harga_penutupan_terakhir < (harga_masuk_short - harga_penutupan_terakhir * 0.01 / self.leverage):  # type: ignore
                            self.order.tutup_short(
                                self.kuantitas_short_rte, leverage=self.leverage
                            )
                            self.kuantitas_short_rte = 0
                        if "LONG" not in POSISI:
                            self.kuantitas_long_rte = self.order.buka_long(
                                kuantitas_koin, leverage=self.leverage
                            )
                    else:
                        # cek posisi long dan tutup
                        if (
                            "LONG" in POSISI and self.kuantitas_long_rte > 0
                        ):  # and harga_penutupan_terakhir > (harga_masuk_long + harga_penutupan_terakhir * 0.01 / self.leverage):  # type: ignore
                            self.order.tutup_long(
                                self.kuantitas_long_rte, leverage=self.leverage
                            )
                            self.kuantitas_long_rte = 0
                        if "SHORT" not in POSISI:
                            self.kuantitas_short_rte = self.order.buka_short(
                                kuantitas_koin, leverage=self.leverage
                            )

        # FUNGSI BACKTEST
        def backtest(list_data: list = self.data) -> str:
            # VARIABEL DAN KONSTANTA
            SALDO = self.saldo_backtest
            LEVERAGE = self.leverage_backtest
            DATA = list_data

            df_backtest = pd.DataFrame(DATA[0])

            MODE_EMA = ""
            posisi = []
            harga_long = []
            harga_short = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_harga_long = []
            list_df_harga_short = []
            list_df_mode_ema = []
            if self.demastoch:
                list_df_mode_stokastik = []
            list_df_mode_rte = []
            for baris in range(len(df_backtest)):
                if baris < 2:
                    list_df_mode_ema.append(["MENUNGGU_TREND"])
                    list_df_tindakan.append([])
                    list_df_posisi.append([])
                    list_df_harga_long.append([])
                    list_df_harga_short.append([])
                    if self.demastoch:
                        list_df_mode_stokastik.append(["MENUNGGU_TREND"])  # type: ignore
                    list_df_mode_rte.append(["MENUNGGU_TREND"])
                else:
                    tindakan = []
                    mode_ema = []
                    if self.demastoch:
                        mode_stokastik = []
                    mode_rte = []
                    harga = df_backtest.iloc[baris]["close"]
                    tinggi = df_backtest.iloc[baris]["high"]
                    rendah = df_backtest.iloc[baris]["low"]
                    ema = df_backtest.iloc[baris]["ema"]
                    harga_sebelumnya = df_backtest.iloc[baris - 1]["close"]
                    ema_sebelumnya = df_backtest.iloc[baris - 1]["ema"]
                    ema_smooth = df_backtest.iloc[baris]["ema_smooth"]
                    ema_smooth_sebelumnya = df_backtest.iloc[baris - 1]["ema_smooth"]
                    if self.dual_ema:
                        ema_cepat = df_backtest.iloc[baris]["ema_cepat"]
                        ema_cepat_sebelumnya = df_backtest.iloc[baris - 1]["ema_cepat"]
                    if self.demastoch:
                        k_lambat = df_backtest.iloc[baris]["k_lambat"]
                        d_lambat = df_backtest.iloc[baris]["d_lambat"]

                    # Cek semua posisi pada masing - masing interval,
                    # jika ada posisi short atau long dengan
                    # percentage loss * leverage >= 100% anggap terkena
                    # margin call dan hapus posisi
                    if (
                        "LONG" in posisi
                        and (rendah - harga_long) / harga_long * LEVERAGE <= -0.8
                    ):
                        tindakan.append("MARGIN_CALL_LONG")
                        posisi.remove("LONG")
                        harga_long.clear()
                    if (
                        "SHORT" in posisi
                        and (harga_short - tinggi) / harga_short * LEVERAGE <= -0.8
                    ):
                        tindakan.append("MARGIN_CALL_SHORT")
                        posisi.remove("SHORT")
                        harga_short.clear()

                    MODE_EMA = (
                        ("DIATAS_EMA" if ema > ema_smooth else "DIBAWAH_EMA")
                        if not self.dual_ema
                        else (
                            "EMA_NAIK"
                            if ema_cepat > ema  # type: ignore
                            else "EMA_TURUN"
                        )
                    )

                    MODE_EMA_SEBELUMNYA = (
                        (
                            "DIATAS_EMA"
                            if ema_sebelumnya > ema_smooth_sebelumnya
                            else "DIBAWAH_EMA"
                        )
                        if not self.dual_ema
                        else (
                            "EMA_NAIK"
                            if ema_cepat_sebelumnya > ema_sebelumnya  # type: ignore
                            else "EMA_TURUN"
                        )
                    )

                    if self.demastoch:
                        MODE_STOCH = "STOKASTIK_NAIK" if k_lambat > d_lambat else "STOKASTIK_TURUN"  # type: ignore

                    # EVALUASI MODE
                    if not self.demastoch:
                        if len(posisi) == 0:
                            if (
                                MODE_EMA_SEBELUMNYA
                                == ("DIBAWAH_EMA" if not self.dual_ema else "EMA_TURUN")
                                and MODE_EMA
                                == ("DIBAWAH_EMA" if not self.dual_ema else "EMA_TURUN")
                            ) or (
                                MODE_EMA_SEBELUMNYA
                                == ("DIATAS_EMA" if not self.dual_ema else "EMA_NAIK")
                                and MODE_EMA
                                == ("DIATAS_EMA" if not self.dual_ema else "EMA_NAIK")
                            ):
                                MODE_RTE = "MENUNGGU_TREND"
                            else:
                                if MODE_EMA_SEBELUMNYA == (
                                    "DIBAWAH_EMA" if not self.dual_ema else "EMA_TURUN"
                                ) and (
                                    MODE_EMA == "DIATAS_EMA"
                                    if not self.dual_ema
                                    else "EMA_NAIK"
                                ):
                                    MODE_RTE = "RTE_NAIK"
                                if MODE_EMA_SEBELUMNYA == (
                                    "DIATAS_EMA" if not self.dual_ema else "EMA_NAIK"
                                ) and MODE_EMA == (
                                    "DIBAWAH_EMA" if not self.dual_ema else "EMA_TURUN"
                                ):
                                    MODE_RTE = "RTE_TURUN"
                        else:
                            MODE_RTE = (
                                "RTE_NAIK"
                                if MODE_EMA
                                == ("DIATAS_EMA" if not self.dual_ema else "EMA_NAIK")
                                else "RTE_TURUN"
                            )
                    else:
                        # if len(posisi) == 0:
                        #     if MODE_STOCH == "STOKASTIK_NAIK":  # type: ignore
                        #         if (
                        #             MODE_EMA == "EMA_NAIK"
                        #             and MODE_EMA_SEBELUMNYA == "EMA_TURUN"
                        #         ):
                        #             MODE_RTE = "RTE_NAIK"
                        #         else:
                        #             MODE_RTE = "MENUNGGU_TREND"
                        #     if MODE_STOCH == "STOKASTIK_TURUN":  # type: ignore
                        #         if (
                        #             MODE_EMA == "EMA_TURUN"
                        #             and MODE_EMA_SEBELUMNYA == "EMA_NAIK"
                        #         ):
                        #             MODE_RTE = "RTE_TURUN"
                        #         else:
                        #             MODE_RTE = "MENUNGGU_TREND"
                        # else:
                        if MODE_EMA == "EMA_NAIK" and MODE_STOCH == "STOKASTIK_NAIK":  # type: ignore
                            MODE_RTE = "RTE_NAIK"
                        elif MODE_EMA == "EMA_TURUN" and MODE_STOCH == "STOKASTIK_TURUN":  # type: ignore
                            MODE_RTE = "RTE_TURUN"
                        else:
                            MODE_RTE = "MENUNGGU_TREND"

                    if not self.demastoch:
                        if MODE_RTE != "MENUNGGU_TREND":  # type: ignore
                            if MODE_RTE == "RTE_NAIK":  # type: ignore
                                if "SHORT" in posisi and harga_sebelumnya < (
                                    harga_short - harga_sebelumnya * 0.031 / LEVERAGE
                                ):
                                    tindakan.append("TUTUP_SHORT")
                                    posisi.remove("SHORT")
                                    harga_short.clear()
                                if "LONG" not in posisi:
                                    tindakan.append("BUKA_LONG")
                                    posisi.append("LONG")
                                    harga_long.append(harga)
                                mode_ema.append(MODE_EMA)
                                mode_rte.append(MODE_RTE)  # type: ignore
                            if MODE_RTE == "RTE_TURUN":  # type: ignore
                                if "LONG" in posisi and harga_sebelumnya > (
                                    harga_long + harga_sebelumnya * 0.031 / LEVERAGE
                                ):  # type: ignore
                                    tindakan.append("TUTUP_LONG")
                                    posisi.remove("LONG")
                                    harga_long.clear()
                                if "SHORT" not in posisi:
                                    tindakan.append("BUKA_SHORT")
                                    posisi.append("SHORT")
                                    harga_short.append(harga)
                                mode_ema.append(MODE_EMA)
                                mode_rte.append(MODE_RTE)  # type: ignore
                        elif MODE_RTE == "MENUNGGU_TREND":  # type: ignore
                            mode_ema.append(MODE_EMA)
                            mode_rte.append(MODE_RTE)  # type: ignore
                    else:
                        if MODE_RTE != "MENUNGGU_TREND":  # type: ignore
                            if MODE_RTE == "RTE_NAIK":  # type: ignore
                                if "SHORT" in posisi and harga_sebelumnya < (
                                    harga_short - harga_sebelumnya * 0.016 / LEVERAGE
                                ):
                                    tindakan.append("TUTUP_SHORT")
                                    posisi.remove("SHORT")
                                    harga_short.clear()
                                if "LONG" not in posisi:
                                    tindakan.append("BUKA_LONG")
                                    posisi.append("LONG")
                                    harga_long.append(harga)
                                mode_ema.append(MODE_EMA)
                                mode_stokastik.append(MODE_STOCH)  # type: ignore
                                mode_rte.append(MODE_RTE)  # type: ignore
                            if MODE_RTE == "RTE_TURUN":  # type: ignore
                                if "LONG" in posisi and harga_sebelumnya > (
                                    harga_long + harga_sebelumnya * 0.016 / LEVERAGE
                                ):
                                    tindakan.append("TUTUP_LONG")
                                    posisi.remove("LONG")
                                    harga_long.clear()
                                if "SHORT" not in posisi:
                                    tindakan.append("BUKA_SHORT")
                                    posisi.append("SHORT")
                                    harga_short.append(harga)
                                mode_ema.append(MODE_EMA)
                                mode_stokastik.append(MODE_STOCH)  # type: ignore
                                mode_rte.append(MODE_RTE)  # type: ignore
                        elif MODE_RTE == "MENUNGGU_TREND":  # type: ignore
                            # cek posisi dan tutup
                            if len(posisi) != 0:
                                if "LONG" in posisi and harga_sebelumnya > (
                                    harga_long + harga_sebelumnya * 0.016 / LEVERAGE
                                ):
                                    tindakan.append("TUTUP_LONG")
                                    posisi.remove("LONG")
                                    harga_long.clear()
                                elif "SHORT" in posisi and harga_sebelumnya < (
                                    harga_short - harga_sebelumnya * 0.016 / LEVERAGE
                                ):
                                    tindakan.append("TUTUP_SHORT")
                                    posisi.remove("SHORT")
                                    harga_short.clear()
                            mode_ema.append(MODE_EMA)
                            mode_stokastik.append(MODE_STOCH)  # type: ignore
                            mode_rte.append(MODE_RTE)  # type: ignore

                    list_df_mode_ema.append(mode_ema.copy())
                    list_df_mode_rte.append(mode_rte.copy())
                    if self.demastoch:
                        list_df_mode_stokastik.append(mode_stokastik.copy())  # type: ignore
                    list_df_tindakan.append(tindakan)
                    list_df_posisi.append(posisi.copy())
                    list_df_harga_long.append(harga_long.copy())
                    list_df_harga_short.append(harga_short.copy())

            df_backtest["mode_ema"] = list_df_mode_ema
            if self.demastoch:
                df_backtest["mode_stokastik"] = list_df_mode_stokastik  # type: ignore
            df_backtest["mode_rte"] = list_df_mode_rte
            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_long"] = list_df_harga_long
            df_backtest["harga_short"] = list_df_harga_short

            # iterasi kolom untung dan rugi
            list_df_profit_dan_loss = []
            list_df_saldo_tersedia = []
            list_df_saldo_long = []
            list_df_saldo_short = []
            saldo_long = 0
            saldo_short = 0
            for baris in range(len(df_backtest)):
                profit_dan_loss = 0
                if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                    profit_dan_loss = (
                        harga_keluar - harga_long
                    ) / harga_long * saldo_long * LEVERAGE - (0.031 * saldo_long)
                    SALDO = SALDO + saldo_long + profit_dan_loss
                    saldo_long = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                    profit_dan_loss = (
                        harga_short - harga_keluar
                    ) / harga_short * saldo_short * LEVERAGE - (0.031 * saldo_short)
                    SALDO = SALDO + saldo_short + profit_dan_loss
                    saldo_short = 0
                if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                    profit_dan_loss = -saldo_short - (saldo_short * 0.031)
                    SALDO = SALDO + saldo_short + profit_dan_loss
                    saldo_short = 0
                if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                    profit_dan_loss = -saldo_long - (saldo_long * 0.031)
                    SALDO = SALDO + saldo_long + profit_dan_loss
                    saldo_long = 0
                if "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    saldo_long = min(SALDO, 2)
                    # saldo_long = SALDO / 2
                    SALDO = SALDO - saldo_long
                if "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    saldo_short = min(SALDO, 2)
                    # saldo_short = SALDO / 2
                    SALDO = SALDO - saldo_short

                list_df_saldo_tersedia.append(SALDO)
                list_df_saldo_long.append(saldo_long)
                list_df_saldo_short.append(saldo_short)
                list_df_profit_dan_loss.append(profit_dan_loss)

            df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
            df_backtest["saldo_long"] = list_df_saldo_long
            df_backtest["saldo_short"] = list_df_saldo_short
            df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

            print(df_backtest.to_string())

            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"]))} dollar'

        # jika live stream strategi
        if not self.backtest:
            live()
        else:
            print(backtest())

    def jpao_smooth_ma_velocity(
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
        ] = ["15 menit"],
        periode_ma: int = 7,
        smoothing: int = 70,
    ) -> None | list:
        self.interval = interval
        self.periode_ma = periode_ma
        self.smoothing = smoothing

        if len(self.interval) != 1:
            return print(
                "STRATEGI INI (jpao_smooth_ma_velocity) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH SATU"
            )

        # if self.periode_ma < self.k_cepat + self.k_lambat + self.d_lambat:  # type: ignore
        #     return print(
        #         "JUMLAH PARAMETER k_cepat, k_lambat dan d_lambat HARUS LEBIH KECIL DARI periode_ma"
        #     )

        self.jumlah_bar = (
            max(self.jumlah_periode_backtest, self.periode_ma + self.smoothing + 2)
            if self.backtest
            else self.periode_ma + self.smoothing + 2
        )

        waktu = self.fungsi.konverter_waktu(self.interval[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        self.df_ma = self.analisa_teknikal.moving_average(
            self.df, self.periode_ma, backtest=self.backtest, smoothing=self.smoothing
        )

        self.data.append(self.df_ma)

        # FUNGSI SAAT LIVE
        def live(list_data: list = self.data) -> str | None:
            # VARIABEL DAN KONSTANTA
            DATA_POSISI_FUTURES = self.posisi_futures
            # cek posisi aset yang dipegang saat ini
            POSISI = DATA_POSISI_FUTURES["positionSide"].unique().tolist()
            if "SHORT" in POSISI:
                data_short = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "SHORT"
                ]
                # kuantitas short yang perlu ditutup
                self.kuantitas_short_svm = abs(int(data_short.iloc[0]["positionAmt"]))
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                # kuantitas long yang perlu ditutup
                self.kuantitas_long_svm = int(data_long.iloc[0]["positionAmt"])

            TRADE_USDT = self.jumlah_trade_usdt
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(TRADE_USDT * self.leverage / harga_koin_terakhir)

            ma_smoothing = list_data[0].iloc[-1]["ma_smoothing"]
            ma_smoothing_sebelumnya = list_data[0].iloc[-2]["ma_smoothing"]
            ma_smoothing_dua_penutupan_sebelumnya = list_data[0].iloc[-3][
                "ma_smoothing"
            ]

            laju_ma_smoothing_sekarang = ma_smoothing - ma_smoothing_sebelumnya
            laju_ma_smoothing_sebelumnya = (
                ma_smoothing_sebelumnya - ma_smoothing_dua_penutupan_sebelumnya
            )

            harga_penutupan = list_data[0].iloc[-1]["close"]

            MODE_MA_SMOOTHING = (
                (
                    "MA_SMOOTH_NAIK"
                    if laju_ma_smoothing_sekarang >= 0
                    else "MA_SMOOTH_TURUN"
                )
                if len(POSISI) != 0
                else (
                    "MA_SMOOTH_NAIK"
                    if laju_ma_smoothing_sekarang >= 0
                    and laju_ma_smoothing_sebelumnya < 0
                    else "MA_SMOOTH_TURUN"
                    if laju_ma_smoothing_sekarang < 0
                    and laju_ma_smoothing_sebelumnya >= 0
                    else "MENUNGGU_TREND"
                )
            )

            self.ui.label_nilai(
                label="Harga Penutupan terakhir", nilai=harga_penutupan, spasi_label=50
            )
            print("")
            self.ui.label_nilai(
                label="Smooth Moving Average [-2]",
                nilai=round(ma_smoothing_dua_penutupan_sebelumnya, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label="Smooth Moving Average [-1]",
                nilai=round(ma_smoothing_sebelumnya, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label="Smooth Moving Average [0]",
                nilai=round(ma_smoothing, 8),
                spasi_label=50,
            )
            print("")
            self.ui.label_nilai(
                label="Smooth Moving Average Velocity [-1]",
                nilai=round(laju_ma_smoothing_sebelumnya, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label="Smooth Moving Average Velocity [0]",
                nilai=round(laju_ma_smoothing_sekarang, 8),
                spasi_label=50,
            )
            print(
                f"\nMODE STRATEGI: \nSMOOTH MOVING AVERAGE VELOCITY ({self.smoothing}) {Fore.YELLOW if MODE_MA_SMOOTHING == 'MENUNGGU_TREND' else Fore.RED if laju_ma_smoothing_sekarang < 0 else Fore.GREEN}[{MODE_MA_SMOOTHING}]{Style.RESET_ALL}"
            )

            if MODE_MA_SMOOTHING != "MENUNGGU_TREND":
                if MODE_MA_SMOOTHING == "MA_SMOOTH_NAIK":
                    # cek apakah masih ada short
                    if "SHORT" in POSISI and self.kuantitas_short_svm > 0:
                        self.order.tutup_short(
                            self.kuantitas_short_svm, leverage=self.leverage
                        )
                        self.kuantitas_short_svm = 0
                    if "LONG" not in POSISI:
                        self.kuantitas_long_svm = self.order.buka_long(
                            kuantitas_koin, leverage=self.leverage
                        )
                elif MODE_MA_SMOOTHING == "MA_SMOOTH_TURUN":
                    # cek apakah masih ada long
                    if "LONG" in POSISI and self.kuantitas_long_svm > 0:
                        self.order.tutup_long(
                            self.kuantitas_long_svm, leverage=self.leverage
                        )
                        self.kuantitas_long_svm = 0
                    if "SHORT" not in POSISI:
                        self.kuantitas_short_svm = self.order.buka_short(
                            kuantitas_koin, leverage=self.leverage
                        )

        # FUNGSI BACKTEST
        def backtest(list_data: list = self.data) -> str:
            # VARIABEL DAN KONSTANTA
            SALDO = self.saldo_backtest
            TRADE_USDT = self.jumlah_trade_usdt
            LEVERAGE = self.leverage_backtest
            DATA = list_data

            df_backtest = pd.DataFrame(DATA[0])

            MODE_MA_SMOOTHING = ""
            posisi = []
            harga_posisi = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_laju_ma_smoothing = []
            list_df_harga_posisi = []
            for baris in range(len(df_backtest)):
                tindakan = []
                harga = df_backtest.iloc[baris]["close"]
                tinggi = df_backtest.iloc[baris]["high"]
                rendah = df_backtest.iloc[baris]["low"]
                ma_smoothing = df_backtest.iloc[baris]["ma_smoothing"]
                ma_smoothing_sebelumnya = df_backtest.iloc[baris - 1]["ma_smoothing"]
                ma_smoothing_dua_penutupan_sebelumnya = df_backtest.iloc[baris - 2][
                    "ma_smoothing"
                ]
                laju_ma_smoothing_sekarang = ma_smoothing - ma_smoothing_sebelumnya
                laju_ma_smoothing_sebelumnya = (
                    ma_smoothing_sebelumnya - ma_smoothing_dua_penutupan_sebelumnya
                )

                # Cek semua posisi pada masing - masing interval,
                # jika ada posisi short atau long dengan
                # percentage loss * leverage >= 100% anggap terkena
                # margin call dan hapus posisi
                if (
                    "LONG" in posisi
                    and (rendah - harga_posisi) / harga_posisi * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_LONG")
                    posisi.remove("LONG")
                    harga_posisi.clear()
                if (
                    "SHORT" in posisi
                    and (harga_posisi - tinggi) / harga_posisi * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_SHORT")
                    posisi.remove("SHORT")
                    harga_posisi.clear()

                MODE_MA_SMOOTHING = (
                    (
                        "MA_SMOOTH_NAIK"
                        if laju_ma_smoothing_sekarang >= 0
                        else "MA_SMOOTH_TURUN"
                    )
                    if len(posisi) != 0
                    else (
                        "MA_SMOOTH_NAIK"
                        if laju_ma_smoothing_sekarang >= 0
                        and laju_ma_smoothing_sebelumnya < 0
                        else "MA_SMOOTH_TURUN"
                        if laju_ma_smoothing_sekarang < 0
                        and laju_ma_smoothing_sebelumnya >= 0
                        else "MENUNGGU_TREND"
                    )
                )

                if MODE_MA_SMOOTHING != "MENUNGGU_TREND":
                    if MODE_MA_SMOOTHING == "MA_SMOOTH_NAIK":
                        if "SHORT" in posisi:
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_posisi.clear()
                        if "LONG" not in posisi:
                            tindakan.append("BUKA_LONG")
                            posisi.append("LONG")
                            harga_posisi.append(harga)
                    elif MODE_MA_SMOOTHING == "MA_SMOOTH_TURUN":
                        if "LONG" in posisi:
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_posisi.clear()
                        if "SHORT" not in posisi:
                            tindakan.append("BUKA_SHORT")
                            posisi.append("SHORT")
                            harga_posisi.append(harga)

                list_df_laju_ma_smoothing.append(laju_ma_smoothing_sekarang.copy())
                list_df_tindakan.append(tindakan)
                list_df_posisi.append(posisi.copy())
                list_df_harga_posisi.append(harga_posisi.copy())

            df_backtest["laju_ma_smoothing_sekarang"] = list_df_laju_ma_smoothing
            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_posisi"] = list_df_harga_posisi

            # iterasi kolom untung_rugi
            list_df_profit_dan_loss = []
            list_df_saldo_tersedia = []
            list_df_saldo_posisi = []
            saldo_posisi = 0
            for baris in range(len(df_backtest)):
                profit_dan_loss = 0
                if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_keluar - harga_posisi
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (
                        0.031 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_posisi - harga_keluar
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (
                        0.031 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = -saldo_posisi - (saldo_posisi * 0.031)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = -saldo_posisi - (saldo_posisi * 0.031)
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if (
                    "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]
                    or "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]
                ):
                    saldo_posisi = TRADE_USDT
                    SALDO = SALDO - saldo_posisi

                list_df_saldo_tersedia.append(SALDO)
                list_df_saldo_posisi.append(saldo_posisi)
                list_df_profit_dan_loss.append(profit_dan_loss)

            df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
            df_backtest["saldo_posisi"] = list_df_saldo_posisi
            df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

            print(df_backtest.to_string())

            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"]))} dollar'  # type: ignore

        # jika live stream strategi
        if not self.backtest:
            live()
        else:
            print(backtest())

    def jpao_double_smoothed_heiken_ashi(
        self,
        smoothed_ha: bool = False,
        tipe_ma_smoothing: List[Literal["sma", "ema"]] = ["sma"],
        smoothing_1: int = 4,
        smoothing_2: int = 9,
        periode_ma_1: int = 20,
        periode_ma_2: int = 50,
    ) -> None | list:
        self.smoothed_ha = smoothed_ha
        self.tipe_ma_smoothing = tipe_ma_smoothing
        if self.smoothed_ha:
            if len(self.tipe_ma_smoothing) < 1 or len(self.tipe_ma_smoothing) > 2:
                return print(
                    f"STRATEGI DOUBLE SMOOTHING HEIKEN ASHI MEMBUTUHKAN 1 ATAU 2 JENIS MA UNTUK SMOOTHING!"
                )
        self.smoothing_1 = smoothing_1
        self.smoothing_2 = smoothing_2
        self.periode_ma_1 = periode_ma_1
        self.periode_ma_2 = periode_ma_2

        if len(self.inter_chart) != 1:
            return print(
                "STRATEGI INI (jpao_double_smoothed_heiken_ashi) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH SATU"
            )

        # if self.periode_ma < self.k_cepat + self.k_lambat + self.d_lambat:  # type: ignore
        #     return print(
        #         "JUMLAH PARAMETER k_cepat, k_lambat dan d_lambat HARUS LEBIH KECIL DARI periode_ma"
        #     )

        # Karena kalkulasi melibatkan exponential moving average, nilainya bisa tidak akurat jika jumlah_bar terlalu sedikit
        # sesuaikan jumlah bar dengan nilai heiken ashi pada versi live production
        self.jumlah_bar = (
            (
                self.jumlah_periode_backtest
                + max(
                    self.smoothing_1 + self.smoothing_2,
                    max(self.periode_ma_1, self.periode_ma_2),
                )
                + 1
            )
            if self.backtest
            else (
                max(
                    (self.smoothing_1 + self.smoothing_2) * 10,
                    max(self.periode_ma_1, self.periode_ma_2),
                )
                + 2
            )
        )

        waktu = self.fungsi.konverter_waktu(self.inter_chart[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        # Cek jika smoothed ha
        if self.smoothed_ha:
            # nilai self.smoothing_1 dan self.smoothing_2 tidak boleh kurang dari 1
            if self.smoothing_1 < 1 or self.smoothing_2 < 1:
                return print(
                    "JIKA MENGGUNAKAN METODE SMOOTHED_HA, PASTIKAN SMOOTHING_1 DAN SMOOTHING_2 LEBIH BESAR DARI 0"
                )

        # MA 1 dan 2
        self.seri_ma_1 = pd.DataFrame(
            self.analisa_teknikal.moving_average(
                self.df["close"], self.periode_ma_1, backtest=self.backtest
            )
        )
        self.seri_ma_2 = pd.DataFrame(
            self.analisa_teknikal.moving_average(
                self.df["close"], self.periode_ma_2, backtest=self.backtest
            )
        )

        # Heiken Ashi smoothed
        self.df_ha = self.analisa_teknikal.heiken_ashi(
            self.df,
            tipe_ma=self.tipe_ma_smoothing,
            smoothed=self.smoothed_ha,
            smooth_period_1=self.smoothing_1,
            smooth_period_2=self.smoothing_2,
            mode_harga_penutupan=self.mode_harga_penutupan,
            backtest=self.backtest,
        )

        # cek jika hasil seri_ma dan heiken ashi tidak None
        if (
            self.seri_ma_1 is not None
            and self.seri_ma_2 is not None
            and self.df_ha is not None
        ):
            self.df[f"ma_{self.periode_ma_1}"] = self.seri_ma_1.values
            self.df[f"ma_{self.periode_ma_2}"] = self.seri_ma_2.values
            self.df["buka_ha"] = self.df_ha["buka_ha"].values
            self.df["tinggi_ha"] = self.df_ha["tinggi_ha"].values
            self.df["rendah_ha"] = self.df_ha["rendah_ha"].values
            self.df["tutup_ha"] = self.df_ha["tutup_ha"].values

        # drop baris dengan nilai NaN
        self.df.dropna(
            subset=[
                f"ma_{self.periode_ma_1}",
                f"ma_{self.periode_ma_2}",
                "buka_ha",
                "tinggi_ha",
                "rendah_ha",
                "tutup_ha",
            ],
            inplace=True,
        )

        # Ambil data tergantung mode backtest
        if self.backtest:
            # Semua baris tidak termasuk baris terakhir
            self.df = self.df.iloc[:-1]
        else:
            # Dua baris data terakhir tidak termasuk baris data terakhir
            # Untuk live dilakukan perubahan data yang dikembalikan untuk
            # memasukkan harga terakhir (belum tutup) jika self.mode_harga_penutupan
            # adalah False dan sebaliknya
            self.df = self.df.iloc[-3:-1] if self.mode_harga_penutupan else self.df.iloc[-2:]

        # spread tutup dan buka Heiken Ashi upscale 100000
        self.df = self.df.assign(
            ha_spread=lambda x: (round((x.tutup_ha - x.buka_ha) * 100000, 6))
        )

        # evaluasi kondisi moving average
        # memilah ma_cepat
        periode_ma_cepat = (
            self.periode_ma_1
            if self.periode_ma_1 <= self.periode_ma_2
            else self.periode_ma_2
        )
        periode_ma_lambat = (
            self.periode_ma_2
            if periode_ma_cepat == self.periode_ma_1
            else self.periode_ma_1
        )
        list_keadaan_ma = []
        for baris in range(len(self.df)):
            ma_naik = (
                self.df.iloc[baris][f"ma_{periode_ma_cepat}"]
                >= self.df.iloc[baris][f"ma_{periode_ma_lambat}"]
            )
            if ma_naik:
                list_keadaan_ma.append("MA_NAIK")
            else:
                list_keadaan_ma.append("MA_TURUN")
        # menambahkan list_keadaan_ma ke dalam self.df
        self.df["keadaan_ma"] = list_keadaan_ma

        # jika spread negatif maka warna_ha MERAH dan jika positif HIJAU
        self.df["warna_ha"] = [
            "HA_MERAH" if x < 0 else "HA_HIJAU" for x in self.df["ha_spread"]
        ]

        # jika spread melebar maka ha_state MEMBESAR dan jika menyempit maka has_state MENGECIL
        list_keadaan_ha = []
        for baris in range(len(self.df)):
            if baris != 0:
                # Merubah keadaan_ha dari membesar atau mengecil menjadi positif atau negatif
                positif = self.df.iloc[baris].ha_spread > self.df.iloc[baris - 1].ha_spread
                # membesar = abs(self.df.iloc[baris].ha_spread) >= abs(
                #     self.df.iloc[baris - 1].ha_spread
                # )
                list_keadaan_ha.append("POSITIF" if positif else "NEGATIF")
            else:
                list_keadaan_ha.append(np.nan)
        # menambahkan list_keadaan_ha ke dalam self.df
        self.df["keadaan_ha"] = list_keadaan_ha

        self.data.append(self.df)

        # FUNGSI SAAT LIVE
        def live(list_data: list = self.data) -> str | None:
            # VARIABEL DAN KONSTANTA
            DATA_POSISI_FUTURES = self.posisi_futures
            # cek posisi aset yang dipegang saat ini
            POSISI = DATA_POSISI_FUTURES["positionSide"].unique().tolist()
            if "SHORT" in POSISI:
                data_short = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "SHORT"
                ]
                # kuantitas short yang perlu ditutup
                self.kuantitas_short_dsha = abs(int(data_short.iloc[0]["positionAmt"]))
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                # kuantitas long yang perlu ditutup
                self.kuantitas_long_dsha = int(data_long.iloc[0]["positionAmt"])

            TRADE_USDT = self.jumlah_trade_usdt
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(TRADE_USDT * self.leverage / harga_koin_terakhir)

            harga_terakhir = list_data[0].iloc[-1].close

            buka_ha = list_data[0].iloc[-1].buka_ha
            tinggi_ha = list_data[0].iloc[-1].tinggi_ha
            rendah_ha = list_data[0].iloc[-1].rendah_ha
            tutup_ha = list_data[0].iloc[-1].tutup_ha
            keadaan_ha = list_data[0].iloc[-1].keadaan_ha

            # warna_ha = list_data[0].iloc[-1].warna_ha
            # warna_ha_sebelumnya = list_data[0].iloc[-2].warna_ha

            self.ui.label_nilai(
                label="Harga Terakhir",
                nilai=harga_terakhir,
                spasi_label=50,
            )
            print("")
            print("Data Smoothed Heiken Ashi Terakhir:")
            self.ui.label_nilai(
                label=f"Pembukaan",
                nilai=round(buka_ha, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Tertinggi",
                nilai=round(tinggi_ha, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Terendah",
                nilai=round(rendah_ha, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Penutupan",
                nilai=round(tutup_ha, 8),
                spasi_label=50,
            )
            self.ui.label_nilai(
                label=f"Keadaan HA",
                nilai=keadaan_ha,
                spasi_label=50,
            )
            print(
                f"\nMODE STRATEGI: \nDOUBLE SMOOTHED HEIKEN ASHI (smoothing 1: {self.smoothing_1}; smoothing 2: {self.smoothing_2}) {Fore.RED if keadaan_ha == 'NEGATIF' else Fore.GREEN}[{keadaan_ha}]{Style.RESET_ALL}"
            )

            # KONDISI EXIT
            if "LONG" in POSISI:
                if keadaan_ha == "NEGATIF":
                    self.order.tutup_long(
                        self.kuantitas_long_dsha, leverage=self.leverage
                    )
                    self.kuantitas_long_dsha = 0
            if "SHORT" in POSISI:
                if keadaan_ha == "POSITIF":
                    self.order.tutup_short(
                        self.kuantitas_short_dsha, leverage=self.leverage
                    )
                    self.kuantitas_short_dsha = 0

            # KONDISI ENTRY
            if "LONG" not in POSISI:
                if keadaan_ha == "POSITIF":
                    self.kuantitas_long_dsha = self.order.buka_long(
                        kuantitas_koin, leverage=self.leverage
                    )
            if "SHORT" not in POSISI:
                if keadaan_ha == "NEGATIF":
                    self.kuantitas_short_dsha = self.order.buka_short(
                        kuantitas_koin, leverage=self.leverage
                    )

        # FUNGSI BACKTEST
        def backtest(list_data: list = self.data) -> str:
            # VARIABEL DAN KONSTANTA
            SALDO = self.saldo_backtest
            TRADE_USDT = self.jumlah_trade_usdt
            LEVERAGE = self.leverage_backtest
            DATA = list_data

            df_backtest = pd.DataFrame(DATA[0])

            MODE_SCALPING = ""
            posisi = []
            harga_long = []
            harga_short = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_harga_long = []
            list_df_harga_short = []
            for baris in range(len(df_backtest)):
                tindakan = []
                harga = df_backtest.iloc[baris].close
                rendah = df_backtest.iloc[baris].low
                tinggi = df_backtest.iloc[baris].high
                keadaan_ma = df_backtest.iloc[baris].keadaan_ma
                warna_ha = df_backtest.iloc[baris].warna_ha
                warna_ha_sebelumnya = df_backtest.iloc[baris - 1].warna_ha
                keadaan_ha = df_backtest.iloc[baris].keadaan_ha

                # Cek semua posisi pada masing - masing interval,
                # jika ada posisi short atau long dengan
                # percentage loss * leverage >= 100% anggap terkena
                # margin call dan hapus posisi
                if (
                    "LONG" in posisi
                    and (rendah - harga_long) / harga_long * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_LONG")
                    posisi.remove("LONG")
                    harga_long.clear()
                if (
                    "SHORT" in posisi
                    and (harga_short - tinggi) / harga_short * LEVERAGE <= -0.8
                ):
                    tindakan.append("MARGIN_CALL_SHORT")
                    posisi.remove("SHORT")
                    harga_short.clear()

                if baris != 0:

                    # KONDISI EXIT
                    # 5. jika ada posisi LONG
                    if (
                        "LONG" in posisi
                    ):  # harga_penutupan_terakhir < (harga_masuk_short - harga_penutupan_terakhir * 0.01 / self.leverage)
                        # 6. keadaan_ma adalah MA_TURUN atau keadaan_ha MENGECIL (Apakah perlu mengevaluasi warna_ma juga?)
                        # if (
                        #     keadaan_ma == "MA_TURUN"
                        #     or (
                        #         warna_ha == "HA_HIJAU"
                        #         and warna_ha_sebelumnya == "HA_HIJAU"
                        #         and keadaan_ha == "MENGECIL"
                        #     )
                        #     or (
                        #         warna_ha == "HA_MERAH" and warna_ha_sebelumnya == "HA_HIJAU"
                        #     )
                        # ):
                        #     tindakan.append("TUTUP_LONG")
                        #     posisi.remove("LONG")
                        #     harga_posisi.clear()
                        # metode sederhana
                        if warna_ha == "HA_MERAH" and warna_ha_sebelumnya == "HA_HIJAU":
                            # and harga > (harga_long + harga * 0.016)
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_long.clear()
                    # 7. jika ada posisi SHORT
                    if "SHORT" in posisi:
                        # 8. keadaan_ma adalah MA_NAIK atau keadaan_ha MENGECIL (Apakah perlu mengevaluasi warna_ma juga?)
                        # if (
                        #     keadaan_ma == "MA_NAIK"
                        #     or (
                        #         warna_ha == "HA_MERAH"
                        #         and warna_ha_sebelumnya == "HA_MERAH"
                        #         and keadaan_ha == "MENGECIL"
                        #     )
                        #     or (
                        #         warna_ha == "HA_HIJAU" and warna_ha_sebelumnya == "HA_MERAH"
                        #     )
                        # ):
                        #     tindakan.append("TUTUP_SHORT")
                        #     posisi.remove("SHORT")
                        #     harga_posisi.clear()
                        # metode sederhana
                        if warna_ha == "HA_HIJAU" and warna_ha_sebelumnya == "HA_MERAH":
                            # and harga < (harga_short - harga * 0.016)
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_short.clear()
                    # KONDISI ENTRY
                    # 1. jika keadaan_ma adalah MA_NAIK dan posisi LONG belum ada
                    if "LONG" not in posisi:
                        # 2. jika HA_HIJAU dan sebelumnya HA_MERAH atau HA_HIJAU dan sebelumnya HA_HIJAU dan MEMBESAR
                        # if (
                        #     warna_ha == "HA_HIJAU" and warna_ha_sebelumnya == "HA_MERAH"
                        # ) or (
                        #     warna_ha == "HA_HIJAU"
                        #     and warna_ha_sebelumnya == "HA_HIJAU"
                        #     and keadaan_ha == "MEMBESAR"
                        # ):
                        #     tindakan.append("BUKA_LONG")
                        #     posisi.append("LONG")
                        #     harga_posisi.append(harga)
                        # metode sederhana
                        if warna_ha == "HA_HIJAU" and warna_ha_sebelumnya == "HA_MERAH":
                            tindakan.append("BUKA_LONG")
                            posisi.append("LONG")
                            harga_long.append(harga)
                    # 3. jika keadaan_ma adalah MA_TURUN dan posisi SHORT belum ada
                    if "SHORT" not in posisi:
                        # 4.jika HA_MERAH dan sebelumnya HA_HIJAU atau HA_MERAH dan sebelumnya HA_MERAH dan MEMBESAR
                        # if (
                        #     warna_ha == "HA_MERAH" and warna_ha_sebelumnya == "HA_HIJAU"
                        # ) or (
                        #     warna_ha == "HA_MERAH"
                        #     and warna_ha_sebelumnya == "HA_MERAH"
                        #     and keadaan_ha == "MEMBESAR"
                        # ):
                        #     tindakan.append("BUKA_SHORT")
                        #     posisi.append("SHORT")
                        #     harga_posisi.append(harga)
                        # metode sederhana
                        if warna_ha == "HA_MERAH" and warna_ha_sebelumnya == "HA_HIJAU":
                            tindakan.append("BUKA_SHORT")
                            posisi.append("SHORT")
                            harga_short.append(harga)

                list_df_tindakan.append(tindakan)
                list_df_posisi.append(posisi.copy())
                list_df_harga_long.append(harga_long.copy())
                list_df_harga_short.append(harga_short.copy())

            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_long"] = list_df_harga_long
            df_backtest["harga_short"] = list_df_harga_short

            # iterasi kolom untung_rugi
            list_df_profit_dan_loss = []
            list_df_saldo_tersedia = []
            list_df_saldo_long = []
            list_df_saldo_short = []
            saldo_long = 0
            saldo_short = 0
            for baris in range(len(df_backtest)):
                profit_dan_loss = 0
                if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                    profit_dan_loss = (
                        harga_keluar - harga_long
                    ) / harga_long * saldo_long * LEVERAGE - (0.016 * saldo_long)
                    SALDO = SALDO + saldo_long + profit_dan_loss
                    saldo_long = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                    profit_dan_loss = (
                        harga_short - harga_keluar
                    ) / harga_short * saldo_short * LEVERAGE - (0.016 * saldo_short)
                    SALDO = SALDO + saldo_short + profit_dan_loss
                    saldo_short = 0
                if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                    profit_dan_loss = -saldo_short - (saldo_short * 0.016)
                    SALDO = SALDO + saldo_short + profit_dan_loss
                    saldo_short = 0
                if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris - 1]["close"]
                    harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                    profit_dan_loss = -saldo_long - (saldo_long * 0.016)
                    SALDO = SALDO + saldo_long + profit_dan_loss
                    saldo_long = 0
                if "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]:
                    saldo_long = TRADE_USDT
                    SALDO = SALDO - saldo_long
                if "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    saldo_short = TRADE_USDT
                    SALDO = SALDO - saldo_short

                list_df_saldo_tersedia.append(SALDO)
                list_df_saldo_long.append(saldo_long)
                list_df_saldo_short.append(saldo_short)
                list_df_profit_dan_loss.append(profit_dan_loss)

            df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
            df_backtest["saldo_long"] = list_df_saldo_long
            df_backtest["saldo_short"] = list_df_saldo_short
            df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

            print(df_backtest.to_string())

            print(sum(df_backtest.profit_dan_loss))

            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"].fillna(0)))} dollar'  # type: ignore

        # jika live stream strategi
        if not self.backtest:
            live()
        else:
            print(backtest())
