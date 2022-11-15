"""
Script untuk kelas Strategi
Script untuk implementasi strategi trading berdasarkan pertimbangan pribadi akan beberapa faktor seperti analisa teknikal
"""

import math
from typing import List, Literal

import pandas as pd
from colorama import Fore, Style, init

from akun.akun import InfoAkun
from analisa.analisa_teknikal import AnalisaTeknikal
from baca_konfig import Inisiasi
from fungsi.fungsi import Fungsi
from model.model import Model
from tindakan.tindakan import Order

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
        backtest: bool = False,
        jumlah_periode_backtest: int = 0,
        saldo_backtest: float = 40,
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
        self.backtest = backtest
        self.jumlah_periode_backtest = jumlah_periode_backtest
        if self.backtest and self.jumlah_periode_backtest <= 0:
            raise ValueError(
                f"Jika backtest={self.backtest}, maka jumlah_periode_backtest harus lebih besar dari 0."
            )
        self.saldo_backtest = saldo_backtest
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

        if len(self.interval) != self.dua:
            return print(
                "STRATEGI INI (jpao_niten_ichi_ryu_28_16_8) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH DUA DAN KOMPONEN KEDUA HARUS LEBIH BESAR ATAU SAMA DENGAN KOMPONEN PERTAMA"
            )

        self.jumlah_bar = (
            self.jumlah_periode_backtest
            if self.backtest
            else self.k_cepat + self.k_lambat + self.d_lambat
        )

        self.data_stokastik = []

        try:
            self.offset = self.fungsi.konverter_offset(
                self.interval[1],
                offset_kosong=True if self.interval[0] == self.interval[1] else False,
            )
        except:
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
                nilai_usdt_short = float(data_short.iloc[0]["isolatedWallet"])
                harga_masuk_short = float(data_short.iloc[0]["entryPrice"])
                leverage_short = float(data_short.iloc[0]["leverage"])
                self.kuantitas_short_nir = round(
                    (nilai_usdt_short + 0.5) * leverage_short / harga_masuk_short
                )
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                nilai_usdt_long = float(data_long.iloc[0]["isolatedWallet"])
                harga_masuk_long = float(data_long.iloc[0]["entryPrice"])
                leverage_long = float(data_long.iloc[0]["leverage"])
                self.kuantitas_long_nir = round(
                    (nilai_usdt_long + 0.5) * leverage_long / harga_masuk_long
                )

            USDT_AKUN = (self.saldo_tersedia + self.saldo_terpakai) - 1
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(USDT_AKUN / 2 * self.leverage / harga_koin_terakhir)

            # set nilai k_lambat_tf_kecil, d_lambat_tf_kecil, k_lambat_tf_besar dan d_lambat_tf_besar
            # untuk evaluasi state strategi
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
                    else "MENUNGGU_PERMULAAN_TREND"
                )
            )

            if self.interval[0] != self.interval[1]:
                print(
                    f"k_lambat pada TF kecil: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(k_lambat_tf_kecil, 4)}{Style.RESET_ALL}"
                )
                print(
                    f"d_lambat pada TF kecil: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(d_lambat_tf_kecil, 4)}{Style.RESET_ALL}"
                )
                print(
                    f"k_lambat pada TF besar: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(k_lambat_tf_besar, 4)}{Style.RESET_ALL}"
                )
                print(
                    f"d_lambat pada TF besar: {Fore.GREEN if k_lambat_tf_besar > d_lambat_tf_besar else Fore.RED}{round(d_lambat_tf_besar, 4)}{Style.RESET_ALL}"
                )
            else:
                print(
                    f"k_lambat: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(k_lambat_tf_kecil, 4)}{Style.RESET_ALL}"
                )
                print(
                    f"d_lambat: {Fore.GREEN if k_lambat_tf_kecil > d_lambat_tf_kecil else Fore.RED}{round(d_lambat_tf_kecil, 4)}{Style.RESET_ALL}"
                )
            print(f"\nHARGA {self.simbol} TERAKHIR: {round(harga_koin_terakhir, 4)}")
            print(
                f"\nMODE STRATEGI: [{Fore.GREEN if self.HOLD_TRADE == 'LONG_SHORT' else Fore.RED}{self.HOLD_TRADE}{Style.RESET_ALL}]"
            )

            # STRATEGI HOLD
            # jika variabel self.HOLD_TRADE == 'LONG_SHORT'
            if self.HOLD_TRADE == "LONG_SHORT":
                # jika tidak ada posisi LONG
                # print("BUKA_LONG")
                # jangan memaksakan diri untuk membuka posisi LONG
                # jika timeframe kecil tidak mendukung
                if "LONG" not in POSISI and (
                    k_lambat_tf_kecil >= d_lambat_tf_kecil
                    and k_lambat_tf_kecil_sebelumnya < d_lambat_tf_kecil_sebelumnya
                ):
                    self.kuantitas_long_nir = self.order.buka_long(
                        kuantitas_koin, leverage=self.leverage
                    )
                # jika k_lambat < d_lambat pada timeframe kecil
                if (
                    k_lambat_tf_kecil < d_lambat_tf_kecil
                    and k_lambat_tf_kecil_sebelumnya >= d_lambat_tf_kecil_sebelumnya
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
                    k_lambat_tf_kecil < d_lambat_tf_kecil
                    and k_lambat_tf_kecil_sebelumnya >= d_lambat_tf_kecil_sebelumnya
                ):
                    self.kuantitas_short_nir = self.order.buka_short(
                        kuantitas_koin, leverage=self.leverage
                    )
                # jika k_lambat >= d_lambat pada timeframe kecil
                if (
                    k_lambat_tf_kecil >= d_lambat_tf_kecil
                    and k_lambat_tf_kecil_sebelumnya < d_lambat_tf_kecil_sebelumnya
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
            SALDO = self.saldo_backtest
            LEVERAGE = self.leverage_backtest
            STOKASTIK = list_df_stokastik

            if type(STOKASTIK) == list:
                # iterrows pada timeframe kecil
                list_akhir = []
                df_backtest = pd.DataFrame()

                # pembentukan df inisial waktu_tf_kecil, close_tf_kecil, k_lambat_tf_kecil, d_lambat_tf_kecil, waktu_tf_besar, k_lambat_tf_besar, d_lambat_tf_besar
                # type: ignore : pasti mengembalikan list
                for baris in STOKASTIK[0].iterrows():
                    # kembalikan waktu_tf_kecil, waktu_tf_besar, k_lambat_tf_kecil,
                    # d_lambat_tf_kecil, k_lambat_tf_besar, d_lambat_tf_besar
                    waktu_tf_kecil = baris[0]
                    close_tf_kecil = baris[1]["close"]
                    k_lambat_tf_kecil = baris[1]["k_lambat"]
                    d_lambat_tf_kecil = baris[1]["d_lambat"]
                    # slice dataframe tf_besar dengan waktu_tf_besar <= waktu_tf_kecil
                    # timeframe besar yang berbeda membutuhkan offset yang berbeda
                    df_tf_besar = STOKASTIK[1][
                        STOKASTIK[1].index <= (waktu_tf_kecil - self.offset)
                    ].iloc[-1:, :]
                    waktu_tf_besar = df_tf_besar.index[0]
                    k_lambat_tf_besar = df_tf_besar.iloc[-1]["k_lambat"]
                    d_lambat_tf_besar = df_tf_besar.iloc[-1]["d_lambat"]
                    list_akhir.append(
                        [
                            waktu_tf_kecil,
                            close_tf_kecil,
                            k_lambat_tf_kecil,
                            d_lambat_tf_kecil,
                            waktu_tf_besar,
                            k_lambat_tf_besar,
                            d_lambat_tf_besar,
                        ]
                    )
                    df_backtest = pd.DataFrame(
                        list_akhir,
                        columns=[
                            "waktu_tf_kecil",
                            "close_tf_kecil",
                            "k_lambat_tf_kecil",
                            "d_lambat_tf_kecil",
                            "waktu_tf_besar",
                            "k_lambat_tf_besar",
                            "d_lambat_tf_besar",
                        ],
                    )

                # iterasi pada dataframe untuk kolom tindakan, posisi, harga_long, harga_short
                HOLD_TRADE = ""
                posisi = []
                harga_long = []
                harga_short = []
                list_df_posisi = []
                list_df_tindakan = []
                list_df_harga_long = []
                list_df_harga_short = []
                for baris in range(len(df_backtest)):
                    tindakan = []
                    harga = df_backtest.iloc[baris]["close_tf_kecil"]
                    k_lambat_tf_kecil = df_backtest.iloc[baris]["k_lambat_tf_kecil"]
                    d_lambat_tf_kecil = df_backtest.iloc[baris]["d_lambat_tf_kecil"]
                    k_lambat_tf_besar = df_backtest.iloc[baris]["k_lambat_tf_besar"]
                    d_lambat_tf_besar = df_backtest.iloc[baris]["d_lambat_tf_besar"]

                    HOLD_TRADE = (
                        "LONG_SHORT"
                        if k_lambat_tf_besar >= d_lambat_tf_besar
                        else "SHORT_LONG"
                    )

                    # Cek semua posisi pada masing - masing interval,
                    # jika ada posisi short atau long dengan
                    # percentage loss * leverage >= 100% anggap terkena
                    # margin call dan hapus posisi
                    if (
                        "LONG" in posisi
                        and (harga - harga_long) / harga_long * LEVERAGE <= -1
                    ):
                        tindakan.append("MARGIN_CALL_LONG")
                        posisi.remove("LONG")
                        harga_long.clear()
                    if (
                        "SHORT" in posisi
                        and (harga_short - harga) / harga_short * LEVERAGE <= -1
                    ):
                        tindakan.append("MARGIN_CALL_SHORT")
                        posisi.remove("SHORT")
                        harga_short.clear()

                    if HOLD_TRADE == "LONG_SHORT":
                        if (
                            "LONG" not in posisi
                            and k_lambat_tf_kecil >= d_lambat_tf_kecil
                        ):
                            tindakan.append("BUKA_LONG")
                            posisi.append("LONG")
                            harga_long.append(harga)
                        if k_lambat_tf_kecil < d_lambat_tf_kecil:
                            if "SHORT" not in posisi:
                                tindakan.append("BUKA_SHORT")
                                posisi.append("SHORT")
                                harga_short.append(harga)
                        elif "SHORT" in posisi:
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_short.clear()
                    elif HOLD_TRADE == "SHORT_LONG":
                        if (
                            "SHORT" not in posisi
                            and k_lambat_tf_kecil < d_lambat_tf_kecil
                        ):
                            tindakan.append("BUKA_SHORT")
                            posisi.append("SHORT")
                            harga_short.append(harga)
                        if k_lambat_tf_kecil >= d_lambat_tf_kecil:
                            if "LONG" not in posisi:
                                tindakan.append("BUKA_LONG")
                                posisi.append("LONG")
                                harga_long.append(harga)
                        elif "LONG" in posisi:
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_long.clear()

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
                list_df_saldo_short = []
                list_df_saldo_long = []
                saldo_long = 0
                saldo_short = 0
                for baris in range(len(df_backtest)):
                    profit_dan_loss = 0
                    if "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = df_backtest.iloc[baris]["close_tf_kecil"]
                        harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                        profit_dan_loss = (
                            (harga_keluar - harga_long)
                            / harga_long
                            * saldo_long
                            * LEVERAGE
                        ) - (saldo_long * 0.008 / LEVERAGE)
                        SALDO = SALDO + saldo_long + profit_dan_loss
                        saldo_long = 0
                    if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = df_backtest.iloc[baris]["close_tf_kecil"]
                        harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                        profit_dan_loss = (
                            (harga_short - harga_keluar)
                            / harga_short
                            * saldo_short
                            * LEVERAGE
                        ) - (saldo_short * 0.008 / LEVERAGE)
                        SALDO = SALDO + saldo_short + profit_dan_loss
                        saldo_short = 0
                    if "MARGIN_CALL_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = df_backtest.iloc[baris]["close_tf_kecil"]
                        harga_short = df_backtest.iloc[baris - 1]["harga_short"]
                        profit_dan_loss = -saldo_short - (
                            saldo_short * 0.008 / LEVERAGE
                        )
                        SALDO = SALDO + saldo_short + profit_dan_loss
                        saldo_short = 0
                    if "MARGIN_CALL_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        harga_keluar = df_backtest.iloc[baris]["close_tf_kecil"]
                        harga_long = df_backtest.iloc[baris - 1]["harga_long"]
                        profit_dan_loss = -saldo_long - (saldo_long * 0.008 / LEVERAGE)
                        SALDO = SALDO + saldo_long + profit_dan_loss
                        saldo_long = 0
                    # NOTES: Penggunaan saldo untuk pembukaan posisi tidak harus setengah atau seluruh saldo, tapi akan
                    # selalu merujuk kepada saldo + saldo_posisi jika ada dibagi dua atau saldo tersedia
                    # jika saldo tersedia < saldo + saldo_posisi dibagi dua
                    if "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]:
                        # jika baris pertama dalam iterrows
                        if baris == 0:
                            saldo_long = 0.5 * SALDO
                            SALDO = SALDO - saldo_long
                        else:
                            # jika ada posisi short pada timeframe sebelumnya dan ditutup pada timeframe ini maka gunakan setengah saldo yang ada
                            if "SHORT" in df_backtest.iloc[baris - 1]["posisi"] and (
                                "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]
                                or "MARGIN_CALL_SHORT"
                                in df_backtest.iloc[baris]["tindakan"]
                            ):
                                saldo_long = 0.5 * SALDO
                                SALDO = SALDO - saldo_long
                            else:
                                saldo_long = min((SALDO + saldo_short) / 2, SALDO)
                                SALDO = SALDO - saldo_long
                    if "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                        # jika baris pertama dalam iterrows
                        if baris == 0:
                            saldo_short = 0.5 * SALDO
                            SALDO = SALDO - saldo_short
                        else:
                            # jika ada posisi long pada timeframe sebelumnya dan ditutup pada timeframe ini maka gunakan setengah saldo yang ada
                            if "LONG" in df_backtest.iloc[baris - 1]["posisi"] and (
                                "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]
                                or "MARGIN_CALL_LONG"
                                in df_backtest.iloc[baris]["tindakan"]
                            ):
                                saldo_short = 0.5 * SALDO
                                SALDO = SALDO - saldo_short
                            else:
                                saldo_short = min((SALDO + saldo_long) / 2, SALDO)
                                SALDO = SALDO - saldo_short
                    list_df_saldo_tersedia.append(SALDO)
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
        periode_ma: int = 100,
        k_cepat: int = 15,
        k_lambat: int = 8,
        d_lambat: int = 3,
        mode_laju_stokastik: bool = False,
    ) -> None | list:
        self.interval = interval
        self.periode_ma = periode_ma
        self.k_cepat = k_cepat
        self.k_lambat = k_lambat
        self.d_lambat = d_lambat
        self.mode_laju_stokastik = mode_laju_stokastik

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
            if self.backtest
            else self.periode_ma + self.k_cepat + self.k_lambat + self.d_lambat + 1
        )

        waktu = self.fungsi.konverter_waktu(self.interval[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        self.df_stokastik = self.analisa_teknikal.stokastik(
            self.df, self.k_cepat, self.k_lambat, self.d_lambat, backtest=True
        )

        self.df_ma = self.analisa_teknikal.moving_average(
            self.df_stokastik, self.periode_ma, backtest=self.backtest
        )

        self.df_stokastik["ma"] = self.df_ma["ma"]
        self.data.append(self.df_stokastik)

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
                nilai_usdt_short = float(data_short.iloc[0]["isolatedWallet"])
                harga_masuk_short = float(data_short.iloc[0]["entryPrice"])
                leverage_short = float(data_short.iloc[0]["leverage"])
                self.kuantitas_short_rtw = round(
                    nilai_usdt_short * leverage_short / harga_masuk_short
                )
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                nilai_usdt_long = float(data_long.iloc[0]["isolatedWallet"])
                harga_masuk_long = float(data_long.iloc[0]["entryPrice"])
                leverage_long = float(data_long.iloc[0]["leverage"])
                self.kuantitas_long_rtw = round(
                    nilai_usdt_long * leverage_long / harga_masuk_long
                )

            USDT_AKUN = math.floor(self.saldo_tersedia + self.saldo_terpakai)
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(USDT_AKUN / 2 * self.leverage / harga_koin_terakhir)

            ma = list_data[0].iloc[-1]["ma"]
            k_lambat = list_data[0].iloc[-1]["k_lambat"]
            d_lambat = list_data[0].iloc[-1]["d_lambat"]
            k_lambat_sebelumnya = list_data[0].iloc[-2]["k_lambat"]
            d_lambat_sebelumnya = list_data[0].iloc[-2]["d_lambat"]
            harga_penutupan = list_data[0].iloc[-1]["close"]
            if self.mode_laju_stokastik:
                laju_stokastik = (
                    "UP"
                    if (k_lambat - d_lambat)
                    - (k_lambat_sebelumnya - d_lambat_sebelumnya)
                    >= 0
                    else "DOWN"
                )

            print(f"\nHarga Penutupan terakhir: {harga_penutupan}")
            print(
                f"Moving Average terakhir: {Fore.RED if harga_penutupan <= ma else Fore.GREEN}{round(ma, 4)}{Style.RESET_ALL}"
            )
            print(
                f"K Lambat terakhir: {Fore.GREEN if k_lambat > d_lambat else Fore.RED}{round(k_lambat, 4)}{Style.RESET_ALL}"
            )
            print(
                f"D Lambat terakhir: {Fore.GREEN if k_lambat > d_lambat else Fore.RED}{round(d_lambat, 4)}{Style.RESET_ALL}"
            )

            self.MODE_SCALPING = "DIATAS_MA" if harga_penutupan > ma else "DIBAWAH_MA"

            print(
                f"\nMODE STRATEGI: \nRIDE THE WAVE {Fore.RED if harga_penutupan <= ma else Fore.GREEN}[{self.MODE_SCALPING}]{Style.RESET_ALL}"
            )
            if self.mode_laju_stokastik:
                print(f"LAJU STOKASTIK {Fore.RED if laju_stokastik == 'DOWN' else Fore.GREEN}[{laju_stokastik}]{Style.RESET_ALL}")  # type: ignore

            if not self.mode_laju_stokastik:
                if self.MODE_SCALPING == "DIATAS_MA":
                    if "SHORT" in POSISI and self.kuantitas_short_rtw > 0:
                        self.order.tutup_short(
                            self.kuantitas_short_rtw, leverage=self.leverage
                        )
                        self.kuantitas_short_rtw = 0
                    if (
                        k_lambat > d_lambat
                    ):  # and k_lambat_sebelumnya <= d_lambat_sebelumnya:
                        if "LONG" not in POSISI:
                            self.kuantitas_long_rtw = self.order.buka_long(
                                kuantitas_koin, leverage=self.leverage
                            )
                    elif k_lambat <= d_lambat:
                        if "LONG" in POSISI and self.kuantitas_long_rtw > 0:
                            self.order.tutup_long(
                                self.kuantitas_long_rtw, leverage=self.leverage
                            )
                            self.kuantitas_long_rtw = 0
                elif self.MODE_SCALPING == "DIBAWAH_MA":
                    if "LONG" in POSISI and self.kuantitas_long_rtw > 0:
                        self.order.tutup_long(
                            self.kuantitas_long_rtw, leverage=self.leverage
                        )
                        self.kuantitas_long_rtw = 0
                    if (
                        k_lambat <= d_lambat
                    ):  # and k_lambat_sebelumnya > d_lambat_sebelumnya:
                        if "SHORT" not in POSISI:
                            self.kuantitas_short_rtw = self.order.buka_short(
                                kuantitas_koin, leverage=self.leverage
                            )
                    elif k_lambat > d_lambat:
                        if "SHORT" in POSISI:
                            self.order.tutup_short(
                                self.kuantitas_short_rtw, leverage=self.leverage
                            )
                            self.kuantitas_short_rtw = 0
            else:
                if self.MODE_SCALPING == "DIATAS_MA":
                    # cek apakah masih ada short
                    if "SHORT" in POSISI and self.kuantitas_short_rtw > 0:
                        self.order.tutup_short(
                            self.kuantitas_short_rtw, leverage=self.leverage
                        )
                        self.kuantitas_short_rtw = 0
                    # hanya trade long DIATAS_MA jika laju_stokastik UP
                    if laju_stokastik == "UP":  # type: ignore
                        if "LONG" not in POSISI:
                            self.kuantitas_long_rtw = self.order.buka_long(
                                kuantitas_koin, leverage=self.leverage
                            )
                    else:
                        if "LONG" in POSISI and self.kuantitas_long_rtw > 0:
                            self.order.tutup_long(
                                self.kuantitas_long_rtw, leverage=self.leverage
                            )
                            self.kuantitas_long_rtw = 0
                elif self.MODE_SCALPING == "DIBAWAH_MA":
                    # cek apakah masih ada long
                    if "LONG" in POSISI and self.kuantitas_long_rtw > 0:
                        self.order.tutup_long(
                            self.kuantitas_long_rtw, leverage=self.leverage
                        )
                        self.kuantitas_long_rtw = 0
                    # hanya trade short DIBAWAH_MA jika laju_stokastik DOWN
                    if laju_stokastik == "DOWN":  # type: ignore
                        if "SHORT" not in POSISI:
                            self.kuantitas_short_rtw = self.order.buka_short(
                                kuantitas_koin, leverage=self.leverage
                            )
                    else:
                        if "SHORT" in POSISI:
                            self.order.tutup_short(
                                self.kuantitas_short_rtw, leverage=self.leverage
                            )
                            self.kuantitas_short_rtw = 0

        # FUNGSI BACKTEST
        def backtest(list_data: list = self.data) -> str:
            # VARIABEL DAN KONSTANTA
            SALDO = self.saldo_backtest
            LEVERAGE = self.leverage_backtest
            DATA = list_data

            df_backtest = pd.DataFrame(DATA[0])

            MODE_SCALPING = ""
            posisi = []
            harga_posisi = []
            laju_stokastik = []
            pergerakan_stokastik = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_harga_posisi = []
            list_df_laju_stokastik = []
            list_df_pergerakan_stokastik = []
            for baris in range(len(df_backtest)):
                tindakan = []
                harga = df_backtest.iloc[baris]["close"]
                k_lambat = df_backtest.iloc[baris]["k_lambat"]
                d_lambat = df_backtest.iloc[baris]["d_lambat"]
                k_lambat_sebelumnya = df_backtest.iloc[baris - 1]["k_lambat"]
                d_lambat_sebelumnya = df_backtest.iloc[baris - 1]["d_lambat"]
                ma = df_backtest.iloc[baris]["ma"]
                delta_stokastik = k_lambat - d_lambat
                delta_stokastik_sebelumnya = k_lambat_sebelumnya - d_lambat_sebelumnya
                laju_stokastik.append(delta_stokastik - delta_stokastik_sebelumnya)
                pergerakan_stokastik.append(
                    "UP"
                ) if delta_stokastik - delta_stokastik_sebelumnya >= 0 else pergerakan_stokastik.append(
                    "DOWN"
                )

                MODE_SCALPING = "DIATAS_MA" if harga >= ma else "DIBAWAH_MA"

                if not self.mode_laju_stokastik:
                    if MODE_SCALPING == "DIATAS_MA":
                        if "SHORT" in posisi:
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_posisi.clear()
                        if (
                            k_lambat > d_lambat
                        ):  # and k_lambat_sebelumnya <= d_lambat_sebelumnya:  # type: ignore
                            if "LONG" not in posisi:
                                tindakan.append("BUKA_LONG")
                                posisi.append("LONG")
                                harga_posisi.append(harga)
                        if k_lambat <= d_lambat:
                            if "LONG" in posisi:
                                tindakan.append("TUTUP_LONG")
                                posisi.remove("LONG")
                                harga_posisi.clear()
                    elif MODE_SCALPING == "DIBAWAH_MA":
                        if "LONG" in posisi:
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_posisi.clear()
                        if (
                            k_lambat <= d_lambat
                        ):  # and k_lambat_sebelumnya > d_lambat_sebelumnya:  # type: ignore
                            if "SHORT" not in posisi:
                                tindakan.append("BUKA_SHORT")
                                posisi.append("SHORT")
                                harga_posisi.append(harga)
                        if k_lambat > d_lambat:
                            if "SHORT" in posisi:
                                tindakan.append("TUTUP_SHORT")
                                posisi.remove("SHORT")
                                harga_posisi.clear()
                else:
                    if MODE_SCALPING == "DIATAS_MA":
                        # cek apakah masih ada short
                        if "SHORT" in posisi:
                            tindakan.append("TUTUP_SHORT")
                            posisi.remove("SHORT")
                            harga_posisi.clear()
                        # trade DIATAS_MA hanya saat pergerakan_stokastik UP
                        if pergerakan_stokastik[0] == "UP":
                            if "LONG" not in posisi:
                                tindakan.append("BUKA_LONG")
                                posisi.append("LONG")
                                harga_posisi.append(harga)
                        else:
                            if "LONG" in posisi:
                                tindakan.append("TUTUP_LONG")
                                posisi.remove("LONG")
                                harga_posisi.clear()
                    else:
                        # cek apakah masih ada long
                        if "LONG" in posisi:
                            tindakan.append("TUTUP_LONG")
                            posisi.remove("LONG")
                            harga_posisi.clear()
                        # trade DIBAWAH_MA hanya saat pergerakan_stokastik DOWN
                        if pergerakan_stokastik[0] == "DOWN":
                            if "SHORT" not in posisi:
                                tindakan.append("BUKA_SHORT")
                                posisi.append("SHORT")
                                harga_posisi.append(harga)
                        else:
                            if "SHORT" in posisi:
                                tindakan.append("TUTUP_SHORT")
                                posisi.remove("SHORT")
                                harga_posisi.clear()

                list_df_laju_stokastik.append(laju_stokastik.copy())
                list_df_pergerakan_stokastik.append(pergerakan_stokastik.copy())
                laju_stokastik.clear()
                pergerakan_stokastik.clear()
                list_df_tindakan.append(tindakan)
                list_df_posisi.append(posisi.copy())
                list_df_harga_posisi.append(harga_posisi.copy())

            df_backtest["laju_stokastik"] = list_df_laju_stokastik
            df_backtest["pergerakan_stokastik"] = list_df_pergerakan_stokastik
            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_posisi"] = list_df_harga_posisi
            df_backtest.dropna(subset=["ma"], inplace=True)

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
                        0.008 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_posisi - harga_keluar
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (
                        0.008 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if (
                    "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]
                    or "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]
                ):
                    saldo_posisi = 0.5 * SALDO
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
    ) -> None | list:
        self.interval = interval
        self.periode_ema = periode_ema
        self.dual_ema = dual_ema
        if self.dual_ema:
            self.periode_ema_cepat = periode_ema_cepat
            # nilai EMA baru menunjukkan nilai yang benar saat data historikal adalah 3 kali periode ema
            self.periode_ema_mod = max(self.periode_ema, self.periode_ema_cepat) * 3
        else:
            self.periode_ema_mod = self.periode_ema * 3

        self.smoothing = smoothing

        if len(self.interval) != 1:
            return print(
                "STRATEGI INI (jpao_ride_the_ema) MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH SATU"
            )

        self.jumlah_bar = (
            self.jumlah_periode_backtest + self.periode_ema_mod
            if self.backtest
            else self.periode_ema_mod
        )

        waktu = self.fungsi.konverter_waktu(self.interval[0])

        self.data = []

        self.df = self.model.ambil_data_historis(
            self.simbol_data, self.exchange, waktu, self.jumlah_bar
        )

        self.df_ema = (
            self.analisa_teknikal.ema(
                self.df,
                self.periode_ema,
                "close",
                self.smoothing,
                backtest=self.backtest,
            )
            if not self.dual_ema
            else self.analisa_teknikal.ema(
                self.df,
                self.periode_ema,
                "close",
                self.smoothing,
                True,
                self.periode_ema_cepat,
                backtest=self.backtest,
            )
        )

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
                nilai_usdt_short = float(data_short.iloc[0]["isolatedWallet"])
                harga_masuk_short = float(data_short.iloc[0]["entryPrice"])
                leverage_short = float(data_short.iloc[0]["leverage"])
                self.kuantitas_short_rte = round(
                    nilai_usdt_short * leverage_short / harga_masuk_short
                )
            if "LONG" in POSISI:
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                data_long = DATA_POSISI_FUTURES[
                    DATA_POSISI_FUTURES["positionSide"] == "LONG"
                ]
                nilai_usdt_long = float(data_long.iloc[0]["isolatedWallet"])
                harga_masuk_long = float(data_long.iloc[0]["entryPrice"])
                leverage_long = float(data_long.iloc[0]["leverage"])
                self.kuantitas_long_rte = round(
                    nilai_usdt_long * leverage_long / harga_masuk_long
                )

            USDT_AKUN = self.saldo_tersedia * 0.9
            harga_koin_terakhir = self.akun.harga_koin_terakhir(self.simbol)
            kuantitas_koin = float(USDT_AKUN * self.leverage / harga_koin_terakhir)

            ema = list_data[0].iloc[-1]["ema"]
            ema_sebelumnya = list_data[0].iloc[-2]["ema"]
            ema_smooth = list_data[0].iloc[-1]["ema_smooth"]
            ema_smooth_sebelumnya = list_data[0].iloc[-2]["ema_smooth"]

            if self.dual_ema:
                ema_cepat = list_data[0].iloc[-1]["ema_cepat"]
                ema_cepat_sebelumnya = list_data[0].iloc[-2]["ema_cepat"]
                ema_cepat_smooth = list_data[0].iloc[-1]["ema_cepat_smooth"]
                ema_cepat_smooth_sebelumnya = list_data[0].iloc[-2]["ema_cepat_smooth"]

            harga_penutupan = list_data[0].iloc[-1]["close"]
            harga_penutupan_sebelumnya = list_data[0].iloc[-2]["close"]

            MODE_EMA = (
                (
                    ("DIATAS_EMA" if harga_penutupan > ema else "DIBAWAH_EMA")
                    if len(POSISI) != 0
                    else (
                        "MENUNGGU_TREND"
                        if (
                            harga_penutupan_sebelumnya <= ema_sebelumnya
                            and harga_penutupan <= ema
                        )
                        or (
                            harga_penutupan_sebelumnya > ema_sebelumnya
                            and harga_penutupan > ema
                        )
                        else "DIATAS_EMA"
                        if harga_penutupan_sebelumnya <= ema_sebelumnya
                        and harga_penutupan > ema
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
                        else "EMA_NAIK"
                    )
                )
            )

            if not self.dual_ema:
                print(
                    f"Harga Penutupan sebelumnya: {Fore.GREEN if harga_penutupan_sebelumnya > ema_sebelumnya else Fore.RED}{harga_penutupan_sebelumnya}{Style.RESET_ALL}"
                )
                print(
                    f"Harga Penutupan terakhir: {Fore.GREEN if harga_penutupan > ema else Fore.RED}{harga_penutupan}{Style.RESET_ALL}"
                )
                print(
                    f"\nExponential Moving Average sebelumnya: {Fore.RED if harga_penutupan_sebelumnya <= ema_sebelumnya else Fore.GREEN}{round(ema_sebelumnya, 4)}{Style.RESET_ALL}"
                )
                print(
                    f"Exponential Moving Average terakhir: {Fore.RED if harga_penutupan <= ema else Fore.GREEN}{round(ema, 4)}{Style.RESET_ALL}"
                )

                print(
                    f"\nMODE STRATEGI: \nRIDE THE EMA {Fore.RED if harga_penutupan <= ema else Fore.GREEN}[{MODE_EMA}]{Style.RESET_ALL}"
                )
            else:
                print(
                    f"Harga Penutupan terakhir: {Fore.GREEN if harga_penutupan > ema_cepat else Fore.RED}{harga_penutupan}{Style.RESET_ALL}"  # type: ignore
                )
                print(
                    f"\nEMA sebelumnya: {Fore.RED if ema_sebelumnya <= ema_cepat_sebelumnya else Fore.GREEN}{round(ema_sebelumnya, 4)}{Style.RESET_ALL}"  # type: ignore
                )
                print(
                    f"EMA terakhir: {Fore.RED if ema <= ema_cepat else Fore.GREEN}{round(ema, 4)}{Style.RESET_ALL}"  # type: ignore
                )
                print(
                    f"EMA Cepat sebelumnya: {Fore.RED if ema_cepat_sebelumnya <= ema_sebelumnya else Fore.GREEN}{round(ema_cepat_sebelumnya, 4)}{Style.RESET_ALL}"  # type: ignore
                )
                print(
                    f"EMA Cepat terakhir: {Fore.RED if ema_cepat <= ema else Fore.GREEN}{round(ema_cepat, 4)}{Style.RESET_ALL}"  # type:ignore
                )

                print(
                    f"\nMODE STRATEGI: \nRIDE THE EMA {Fore.RED if ema_cepat <= ema else Fore.GREEN}[{MODE_EMA}]{Style.RESET_ALL}"  # type: ignore
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
                                self.kuantitas_short_rte, leverage=self.leverage
                            )
            else:
                if MODE_EMA != "MENUNGGU_TREND":
                    if MODE_EMA == "EMA_NAIK":
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
                                self.kuantitas_short_rte, leverage=self.leverage
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
            harga_posisi = []
            list_df_posisi = []
            list_df_tindakan = []
            list_df_harga_posisi = []
            list_df_mode_ema = []
            for baris in range(len(df_backtest)):
                if baris < 2:
                    list_df_mode_ema.append(["MENUNGGU_TREND"])
                    list_df_tindakan.append([])
                    list_df_posisi.append([])
                    list_df_harga_posisi.append([])
                else:
                    tindakan = []
                    mode_ema = []
                    harga = df_backtest.iloc[baris]["close"]
                    ema_smooth = df_backtest.iloc[baris]["ema_smooth"]
                    ema = df_backtest.iloc[baris]["ema"]
                    if self.dual_ema:
                        ema_cepat = df_backtest.iloc[baris]["ema_cepat"]
                    harga_sebelumnya = df_backtest.iloc[baris - 1]["close"]
                    ema_smooth_sebelumnya = df_backtest.iloc[baris - 1]["close"]
                    ema_sebelumnya = df_backtest.iloc[baris - 1]["ema"]
                    if self.dual_ema:
                        ema_cepat_sebelumnya = df_backtest.iloc[baris - 1]["ema_cepat"]

                    MODE_EMA = (
                        (
                            "DIATAS_EMA"
                            if harga > ema
                            else "DIBAWAH_EMA"
                            if len(posisi) != 0
                            else "DIATAS_EMA"
                            if harga > ema and harga_sebelumnya <= ema_sebelumnya
                            else "DIBAWAH_EMA"
                            if harga <= ema and harga_sebelumnya > ema_sebelumnya
                            else "MENUNGGU_TREND"
                        )
                        if not self.dual_ema
                        else (
                            "EMA_NAIK"
                            if ema_cepat > ema  # type: ignore
                            else "EMA_TURUN"
                            if len(posisi) != 0
                            else "EMA_NAIK"
                            if ema_cepat > ema  # type: ignore
                            and hema_cepat_sebelumnya <= ema_sebelumnya  # type: ignore
                            else "EMA_TURUN"
                            if ema_cepat <= ema  # type: ignore
                            and ema_cepat_sebelumnya > ema_sebelumnya  # type: ignore
                            else "MENUNGGU_TREND"
                        )
                    )

                    if MODE_EMA != "MENUNGGU_TREND":
                        if (
                            MODE_EMA == "DIATAS_EMA"
                            if not self.dual_ema
                            else "EMA_NAIK"
                        ):
                            if "SHORT" in posisi:
                                tindakan.append("TUTUP_SHORT")
                                posisi.remove("SHORT")
                                harga_posisi.clear()
                            if "LONG" not in posisi:
                                tindakan.append("BUKA_LONG")
                                posisi.append("LONG")
                                harga_posisi.append(harga)
                            mode_ema.append(MODE_EMA)
                        elif (
                            MODE_EMA == "DIBAWAH_EMA"
                            if not self.dual_ema
                            else "EMA_TURUN"
                        ):
                            if "LONG" in posisi:
                                tindakan.append("TUTUP_LONG")
                                posisi.remove("LONG")
                                harga_posisi.clear()
                            if "SHORT" not in posisi:
                                tindakan.append("BUKA_SHORT")
                                posisi.append("SHORT")
                                harga_posisi.append(harga)
                            mode_ema.append(MODE_EMA)
                    else:
                        mode_ema.append(MODE_EMA)

                    list_df_mode_ema.append(mode_ema.copy())
                    list_df_tindakan.append(tindakan)
                    list_df_posisi.append(posisi.copy())
                    list_df_harga_posisi.append(harga_posisi.copy())

            df_backtest["mode_ema"] = list_df_mode_ema
            df_backtest["tindakan"] = list_df_tindakan
            df_backtest["posisi"] = list_df_posisi
            df_backtest["harga_posisi"] = list_df_harga_posisi

            # iterasi kolom untung dan rugi
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
                        0.008 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]:
                    harga_keluar = df_backtest.iloc[baris]["close"]
                    harga_posisi = df_backtest.iloc[baris - 1]["harga_posisi"]
                    profit_dan_loss = (
                        harga_posisi - harga_keluar
                    ) / harga_posisi * saldo_posisi * LEVERAGE - (
                        0.008 * saldo_posisi / LEVERAGE
                    )
                    SALDO = SALDO + saldo_posisi + profit_dan_loss
                    saldo_posisi = 0
                if (
                    "BUKA_LONG" in df_backtest.iloc[baris]["tindakan"]
                    or "BUKA_SHORT" in df_backtest.iloc[baris]["tindakan"]
                ):
                    saldo_posisi = SALDO
                    SALDO = SALDO - saldo_posisi

                list_df_saldo_tersedia.append(SALDO)
                list_df_saldo_posisi.append(saldo_posisi)
                list_df_profit_dan_loss.append(profit_dan_loss)

            df_backtest["saldo_tersedia"] = list_df_saldo_tersedia
            df_backtest["saldo_posisi"] = list_df_saldo_posisi
            df_backtest["profit_dan_loss"] = list_df_profit_dan_loss

            print(df_backtest.to_string())

            return f'Profit dan Loss menggunakan strategi ini: {float(sum(df_backtest["profit_dan_loss"]))} dollar'

        # jika live stream strategi
        if not self.backtest:
            live()
        else:
            print(backtest())
