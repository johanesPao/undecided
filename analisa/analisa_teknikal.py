"""
Script untuk kelas AnalisaTeknikal
Definisikan logika dari metode analisa teknikal untuk dipergunakan pada script strategi.py
"""

from typing import List, Literal

import numpy as np
import pandas as pd

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class AnalisaTeknikal:
    """
    Kelas AnalisaTeknikal berisikan metode - metode untuk melakukan analisa teknikal terhadap sekumpulan data harga yang disajikan dalam format pd.DataFrame. Metode yang saat ini baru tersedia adalah metode stokastik. Untuk metode moving_average dan parabolic_sar belum dibuat.
    Anda juga dapat menambahkan berbagai jenis metode analisa teknikal pada kelas ini.
    Hampir keseluruhan metode dalam kelas AnalisaTeknikal akan menerima data OHLC (Open High Low Close) dalam format pd.DataFrame.
    Argumen backtest juga wajib ada dalam metode di kelas ini, karena metode di kelas ini akan mengembalikan nilai indikator teknikal untuk timeframe terakhir (latest/current) saja jika metode dipergunakan sebagai bagian dari implementasi live, namun akan mengembalikan data dalam jumlah yang besar jika diimplementasikan sebagai bagian dari proses backtesting strategi.

    Atribut
    -------
    (None)

    Metode
    ------
    stokastik(data: pd.DataFrame, periode_k_cepat: int, periode_k_lambat: int, periode_d_lambat: int, backtest: bool, k_tinggi: str, k_rendah: str, k_tutup: str) -> pd.DataFrame:
        Metode ini akan melakukan kalkulasi nilai Stochastic dari sekumpulan data yang diberikan.
    moving_average():
        Metode ini akan melakukan kalkulasi nilai Moving Average dari sekumpulan data yang diberikan.
    parabolic_sar():
        Metode ini akan melakukan kalkulasi nilai Parabolic SAR dari sekumpulan data yang diberikan.

    ...UNTUK DITAMBAHKAN
    """

    def __init__(self) -> None:
        """
        Metode inisiasi kelas AnalisaTeknikal

        Argumen
        -------
        (None)

        Return
        ------
        (None)
        """
        pass

    # DEFINISI FUNGSI ANALISA TEKNIKAL DAPAT DITAMBAHKAN DI BAWAH INI
    # ANALISA TEKNIKAL STOCHASTIC
    def stokastik(
        self,
        data: pd.DataFrame,
        periode_k_cepat: int = 14,
        periode_k_lambat: int = 3,
        periode_d_lambat: int = 3,
        backtest: bool = False,
        k_tinggi: str = "High",
        k_rendah: str = "Low",
        k_tutup: str = "Close",
    ) -> pd.DataFrame:
        """
        Implementasi dari analisa teknikal Stochastic. Mengembalikan nilai stochastic terakhir atau keseluruhan dataframe jika backtest adalah True

        Argumen
        -------
        data (pd.DataFrame):
            data dengan format pd.DataFrame yang memiliki kolom HLC
        periode_k_cepat (int):
            jumlah periode yang dipergunakan untuk perhitungan k_cepat
        periode_k_lambat (int):
            jumlah periode yang dipergunakan untuk perhitungan k_lambat
        periode_d_lambat (int):
            jumlah periode yang dipergunakan untuk perhitungan d_lambat
        backtest (bool):
            mengembalikan analisa untuk keperluan backtest atau live trading
        k_tinggi (str):
            nama kolom yang mengandung data harga tertinggi
        k_rendah (str):
            nama kolom yang mengandung data harga terendah
        k_tutup (str):
            nama kolom yang mengandung data harga penutupan

        Return
        ------
        (pd.DataFrame):
            Mengembalikan pd.DataFrame dengan format kolom k_lambat dan d_lambat terbaru atau keseluruhan dataframe dalam periode backtest yang dilakukan dengan format kolom waktu_penutupan, k_lambat dan d_lambat
        """
        self.data = data
        self.p_k_cepat = periode_k_cepat
        self.p_k_lambat = periode_k_lambat
        self.p_d_lambat = periode_d_lambat
        self.backtest = backtest

        self.df = self.data.copy()

        # Slicing kolom yang dibutuhkan dari dataframe
        kolom_df = [k_tinggi, k_rendah, k_tutup]

        # Slicing dataframe
        self.df = self.df[kolom_df]

        # Membuat variabel untuk representasi kolom
        tinggi = self.df[k_tinggi]
        rendah = self.df[k_rendah]
        tutup = self.df[k_tutup]

        # Menambahkan kolom 'n_tinggi' dengan nilai maks dari n periode (self.p_k_cepat) sebelumnya
        self.df["n_tinggi"] = tinggi.rolling(self.p_k_cepat).max()

        # Menambahkan kolom 'n_rendah' dengan nilai minimum dari n periode (self.p_k_cepat) sebelumnya
        self.df["n_rendah"] = rendah.rolling(self.p_k_cepat).min()

        # Menggunakan nilai min/maks untuk menghitung %k_cepat
        self.df["k_cepat"] = (
            (tutup - self.df["n_rendah"]) / (self.df["n_tinggi"] - self.df["n_rendah"])
        ) * 100

        # Menghitung nilai %k_lambat yang merupakan rata-rata dari %k_cepat selama n periode (self.p_k_lambat) sebelumnya
        self.df["k_lambat"] = self.df["k_cepat"].rolling(self.p_k_lambat).mean()

        # Menghitung nilai %d_lambat yang merupakan rata-rata dari %k_lambat selama n periode (self.p_d_lambat) sebelumnya
        self.df["d_lambat"] = self.df["k_lambat"].rolling(self.p_d_lambat).mean()

        # Jika bukan backtest, kembalikan kolom k_lambat dan d_lambat dari baris terakhir data
        # Dengan perubahan data API endpoint ke tradingview, baris terakhir akan menghasilkan nilai yang berjalan dan belum close, ambil data pada urutan baris kedua terakhir saja (dalam kasus backtest false) atau sampai dengan dua baris terakhir saja (dalam kasus backtest true)
        # Untuk mendapatkan realtime posisi, pada live, slicing diubah menjadi [-2:, :] yang sebelumnya [-3:-1, :]
        if not self.backtest:
            self.df = self.df[
                [k_tinggi, k_rendah, k_tutup, "k_lambat", "d_lambat"]
            ].iloc[-2:, :]
        else:
            self.df = self.df[
                [k_tinggi, k_rendah, k_tutup, "k_lambat", "d_lambat"]
            ].iloc[:-1, :]

        # Membuang data dengan nilai NaN pada kolom k_lambat atau d_lambat
        self.df.dropna(
            subset=[k_tinggi, k_rendah, k_tutup, "k_lambat", "d_lambat"], inplace=True
        )

        # Mengembalikan dataframe yang telah diolah
        return self.df

    # MOVING AVERAGE
    def moving_average(
        self,
        data: pd.Series,
        periode: int = 100,
        backtest: bool = False,
        smoothed: bool = False,
        smoothing: int = 0,
    ) -> None | pd.Series:
        self.backtest = backtest

        if len(data) < periode + (smoothing if smoothed else 0) + 1:
            return print(
                "Data tidak cukup untuk menghitung moving_average dan smoothing"
            )

        # Menambahkan kolom 'ma' dengan nilai rata - rata k_tutup selama periode 'ma'
        ma = data.rolling(periode).mean()

        # Menambahkan kolom 'ma_smoothing' jika self.smoothed
        if smoothed:
            ma = ma if smoothing <= 0 else ma.rolling(smoothing).mean()

        # Mengembalikan dataframe
        return ma

    # PARABOLIC SAR
    def parabolic_sar(self):
        pass

    # EXPONENTIAL MOVING AVERAGE
    def ema(
        self,
        data: pd.Series,
        periode: int = 50,
        smoothed: bool = False,
        smoothing: int = 20,
        backtest: bool = False,
    ) -> pd.Series:
        self.backtest = backtest

        # multiplier ema
        multiplier = 2 / (1 + periode)

        # fungsi olah_ema
        def olah_ema(data: pd.Series, periode: int) -> list:
            ema = []
            for baris in range(len(data)):
                # di bawah periode ema
                if baris < periode - 1:
                    ema.append(np.nan)
                # ema pertama
                elif baris == periode - 1:
                    ema.append(sum(data.iloc[: baris + 1].fillna(0)) / periode)
                # ema kedua dan seterusnya
                else:
                    ema.append(
                        (data.iloc[baris] * multiplier) + (ema[-1] * (1 - multiplier))
                    )
            return ema

        # generate ema
        ema = pd.Series(olah_ema(data, periode))

        # ema smoothing menggunakan simple ma
        if smoothed:
            ema = ema.rolling(smoothing).mean()

        return ema

    def heiken_ashi(
        self,
        data: pd.DataFrame,
        smoothed: bool = False,
        tipe_ma: List[Literal["sma", "ema"]] = ["sma"],
        smooth_period_1: int = 1,
        smooth_period_2: int = 1,
        k_buka: str = "Open",
        k_tinggi: str = "High",
        k_rendah: str = "Low",
        k_tutup: str = "Close",
        mode_harga_penutupan: bool = True,
        backtest: bool = False,
    ) -> None | pd.DataFrame:
        # Cek jika smoothed
        if smoothed:
            # Cek jika panjang tipe_ma lebih dari tidak 1 atau 2
            if len(tipe_ma) < 1 or len(tipe_ma) > 2:
                return print(
                    f"TA Heiken Ashi dengan mode smoothed hanya bisa memiliki 1 atau 2 tipe Moving Average untuk smoothingnya"
                )
        # Cek jumlah tipe_ma, jika 1 maka tipe_ma1 dan tipe_ma2 adalah sama
        if len(tipe_ma) == 1:
            tipe_ma1 = tipe_ma[0]
            tipe_ma2 = tipe_ma[0]
        # Jika jumlah tipe_ma adalah 2, maka tipe_ma1 = tipe_ma[0] dan tipe_ma2 = tipe_ma[1]
        else:
            tipe_ma1 = tipe_ma[0]
            tipe_ma2 = tipe_ma[1]
        self.backtest = backtest

        df = data.copy()

        def olah_smoothed_komponen(
            data: pd.Series,
            tipe_ma: List[Literal["sma", "ema"]] = ["sma"],
            periode: int = 7,
        ) -> None | pd.Series:
            # Jika tipe_ma = sma
            if tipe_ma == "sma":
                # smoothing menggunakan simple moving average
                smoothed_komponen = self.moving_average(
                    data, periode, backtest=self.backtest
                )
            # Jika tipe_ma = 'ema'
            if tipe_ma == "ema":
                # smoothing menggunakan exponential moving average
                smoothed_komponen = self.ema(data, periode, backtest=self.backtest)

            # return smoothed_komponen jika tidak None
            if smoothed_komponen is not None:  # type: ignore
                return smoothed_komponen  # type: ignore

        def olah_heiken_ashi(
            data: pd.DataFrame,
            k_buka: str = "Open",
            k_tinggi: str = "High",
            k_rendah: str = "Low",
            k_tutup: str = "Close",
            mulai_hitung: int = 1,
        ) -> pd.DataFrame:
            list_buka_ha = []
            list_tinggi_ha = []
            list_rendah_ha = []
            list_tutup_ha = []
            for baris in range(len(data)):
                tutup = (
                    data.iloc[baris][k_buka]
                    + data.iloc[baris][k_tinggi]
                    + data.iloc[baris][k_rendah]
                    + data.iloc[baris][k_tutup]
                ) / 4
                buka = (
                    (data.iloc[baris][k_buka] + data.iloc[baris][k_tutup])
                    if baris <= mulai_hitung - 1
                    else (list_buka_ha[-1] + list_tutup_ha[-1]) / 2
                )
                tinggi = max(data.iloc[baris][k_tinggi], max(buka, tutup))
                rendah = min(data.iloc[baris][k_rendah], min(buka, tutup))
                list_buka_ha.append(buka)
                list_tinggi_ha.append(tinggi)
                list_rendah_ha.append(rendah)
                list_tutup_ha.append(tutup)
            heiken_ashi = pd.DataFrame(
                data={
                    "buka_ha": list_buka_ha,
                    "tinggi_ha": list_tinggi_ha,
                    "rendah_ha": list_rendah_ha,
                    "tutup_ha": list_tutup_ha,
                }
            )

            # kembalikan heiken ashi dalam dataframe
            return heiken_ashi

        # Jika smoothed, olah_smooth_komponen dari data sebelum diolah menjadi heiken ashi
        # print(self.df)
        if smoothed:
            seri_buka_smooth = pd.DataFrame(olah_smoothed_komponen(df[k_buka].astype(float), tipe_ma1, smooth_period_1))  # type: ignore
            seri_tinggi_smooth = pd.DataFrame(olah_smoothed_komponen(df[k_tinggi].astype(float), tipe_ma1, smooth_period_1))  # type: ignore
            seri_rendah_smooth = pd.DataFrame(olah_smoothed_komponen(df[k_rendah].astype(float), tipe_ma1, smooth_period_1))  # type: ignore
            seri_tutup_smooth = pd.DataFrame(olah_smoothed_komponen(df[k_tutup].astype(float), tipe_ma1, smooth_period_1))  # type: ignore
            df["buka_smooth"] = seri_buka_smooth.values
            df["tinggi_smooth"] = seri_tinggi_smooth.values
            df["rendah_smooth"] = seri_rendah_smooth.values
            df["tutup_smooth"] = seri_tutup_smooth.values

        # Generate Heiken Ashi
        df_heiken_ashi = olah_heiken_ashi(
            df,
            k_buka="buka_smooth" if smoothed else k_buka,
            k_tinggi="tinggi_smooth" if smoothed else k_tinggi,
            k_rendah="rendah_smooth" if smoothed else k_rendah,
            k_tutup="tutup_smooth" if smoothed else k_tutup,
            mulai_hitung=smooth_period_1,
        )

        # Jika smoothed, lakukan smoothing pada Heiken Ashi
        if smoothed:
            buka_has = pd.DataFrame(olah_smoothed_komponen(df_heiken_ashi["buka_ha"].astype(float), tipe_ma2, smooth_period_2))  # type: ignore
            tinggi_has = pd.DataFrame(olah_smoothed_komponen(df_heiken_ashi["tinggi_ha"].astype(float), tipe_ma2, smooth_period_2))  # type: ignore
            rendah_has = pd.DataFrame(olah_smoothed_komponen(df_heiken_ashi["rendah_ha"].astype(float), tipe_ma2, smooth_period_2))  # type: ignore
            tutup_has = pd.DataFrame(olah_smoothed_komponen(df_heiken_ashi["tutup_ha"].astype(float), tipe_ma2, smooth_period_2))  # type: ignore
            # overwrite kolom df_heiken_ashi dengan versi smoothed
            df_heiken_ashi["buka_ha"] = buka_has.values
            df_heiken_ashi["tinggi_ha"] = tinggi_has.values
            df_heiken_ashi["rendah_ha"] = rendah_has.values
            df_heiken_ashi["tutup_ha"] = tutup_has.values

        # Tambahkan kolom Heiken Ashi dan return
        df["buka_ha"] = df_heiken_ashi["buka_ha"].values
        df["tinggi_ha"] = df_heiken_ashi["tinggi_ha"].values
        df["rendah_ha"] = df_heiken_ashi["rendah_ha"].values
        df["tutup_ha"] = df_heiken_ashi["tutup_ha"].values

        # backtest atau live
        # if not self.backtest:
        #     return df.iloc[-3: -1] if mode_harga_penutupan else df.iloc[-2:]
        # else:
        #     return df.iloc[:-1]

        return df
