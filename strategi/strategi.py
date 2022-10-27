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
        saldo: float = 40,
        leverage: int = 10,
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
        self.saldo = saldo
        self.leverage = leverage
        self.HOLD_TRADE = ""

    def jpao_niten_ichi_ryu_26_18_8(
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
        k_cepat: int = 26,
        k_lambat: int = 18,
        d_lambat: int = 8,
    ) -> None | list:
        self.interval = interval
        self.k_cepat = k_cepat
        self.k_lambat = k_lambat
        self.d_lambat = d_lambat
        self.dua = 2

        print(
            "PERINGATAN: STRATEGI INI MENGGUNAKAN INTERVAL WAKTU DALAM LIST BERJUMLAH DUA DAN KOMPONEN KEDUA HARUS LEBIH BESAR ATAU SAMA DENGAN KOMPONEN PERTAMA"
        )

        if len(self.interval) != 2:
            return print(
                "Strategi ini (strategi_stokastik_jpao) memerlukan dua interval waktu dalam list dan "
            )

        self.jumlah_bar = (
            self.jumlah_periode_backtest
            if self.backtest
            else self.k_cepat + self.k_lambat + self.d_lambat
        )

        self.data_stokastik = []

        self.offset = pd.DateOffset()

        try:
            if self.interval[0] == self.interval[1]:
                if "menit" in self.interval[0]:
                    self.offset = pd.DateOffset(minutes=0)
                if "jam" in self.interval[0]:
                    self.offset = pd.DateOffset(hours=0)
                if "hari" in self.interval[0]:
                    self.offset = pd.DateOffset(days=0)
                if "minggu" in self.interval[0]:
                    self.offset = pd.DateOffset(weeks=0)
                if "bulan" in self.interval[0]:
                    self.offset = pd.DateOffset(months=0)
            else:
                match self.interval[1]:
                    case "3 menit":
                        self.offset = pd.DateOffset(minutes=3)
                    case "5 menit":
                        self.offset = pd.DateOffset(minutes=5)
                    case "15 menit":
                        self.offset = pd.DateOffset(minutes=15)
                    case "45 menit":
                        self.offset = pd.DateOffset(minutes=45)
                    case "1 jam":
                        self.offset = pd.DateOffset(hours=1)
                    case "2 jam":
                        self.offset = pd.DateOffset(hours=2)
                    case "3 jam":
                        self.offset = pd.DateOffset(hours=3)
                    case "4 jam":
                        self.offset = pd.DateOffset(hours=4)
                    case "1 hari":
                        self.offset = pd.DateOffset(days=1)
                    case "1 minggu":
                        self.offset = pd.DateOffset(weeks=1)
                    case "1 bulan":
                        self.offset = pd.DateOffset(months=1)
        except:
            print(
                "KESALAHAN: Kami tidak dapat membaca interval waktu yang diberikan, pastikan interval waktu dalam list dengan dua komponen dimana komponen kedua adalah timeframe yang lebih besar atau sama dengan timeframe kecil (komponen pertama)"
            )

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

        # FUNGSI SAAT LIVE
        def live(list_df_stokastik) -> str | None:
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

        # FUNGSI SAAT BACKTEST
        def backtest(list_df_stokastik) -> str:
            # VARIABEL DAN KONSTANTA
            ASET = self.simbol
            EXCHANGE = self.exchange
            SALDO = self.saldo
            LEVERAGE = self.leverage
            STOKASTIK = self.data_stokastik
            JUMLAH_PERIODE_BACKTEST = self.jumlah_periode_backtest

            if type(STOKASTIK) == list:
                # iterrows pada timeframe kecil
                list_akhir = []
                df_backtest = pd.DataFrame()

                # pembentukan df inisial waktu_tf_kecil, close_tf_kecil, k_lambat_tf_kecil, d_lambat_tf_kecil, waktu_tf_besar, k_lambat_tf_besar, d_lambat_tf_besar
                for baris in STOKASTIK[0].iterrows():  # type: ignore : pasti mengembalikan list
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
                        )
                        if profit_dan_loss < 0 and abs(profit_dan_loss) >= saldo_long:
                            profit_dan_loss = -saldo_long
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
                        )
                        if profit_dan_loss < 0 and abs(profit_dan_loss) >= saldo_short:
                            profit_dan_loss = -saldo_short
                        SALDO = SALDO + saldo_short + profit_dan_loss
                        saldo_short = 0
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
                            if (
                                "SHORT" in df_backtest.iloc[baris - 1]["posisi"]
                                and "TUTUP_SHORT" in df_backtest.iloc[baris]["tindakan"]
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
                            if (
                                "LONG" in df_backtest.iloc[baris - 1]["posisi"]
                                and "TUTUP_LONG" in df_backtest.iloc[baris]["tindakan"]
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
            print(live(self.data_stokastik))
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

    def jpao_kodachijutsu_26_18_8(self):
        pass
