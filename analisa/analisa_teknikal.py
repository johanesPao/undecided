"""
Script untuk kelas AnalisaTeknikal
Definisikan logika dari metode analisa teknikal untuk dipergunakan pada script strategi.py
"""

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

    Atribut:
        None

    Metode:
        stokastik():
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

        Argumen:
            None

        Return:
            None
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
        k_tinggi: str = "high",
        k_rendah: str = "low",
        k_tutup: str = "close",
    ) -> pd.DataFrame:
        """
        Implementasi dari analisa teknikal Stochastic. Mengembalikan nilai stochastic terakhir atau keseluruhan dataframe jika backtest adalah True

        Argumen:
          data (pd.DataFrame): data dengan format pd.DataFrame yang memiliki kolom HLC
          periode_k_cepat (int): jumlah periode yang dipergunakan untuk perhitungan k_cepat
          periode_k_lambat (int): jumlah periode yang dipergunakan untuk perhitungan k_lambat
          periode_d_lambat (int): jumlah periode yang dipergunakan untuk perhitungan d_lambat
          backtest (bool): mengembalikan analisa untuk keperluan backtest atau live trading
          k_tinggi (str): nama kolom yang mengandung data harga tertinggi
          k_rendah (str): nama kolom yang mengandung data harga terendah
          k_tutup (str): nama kolom yang mengandung data harga penutupan

        Return:
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
        if not self.backtest:
            self.df = self.df[[k_tutup, "k_lambat", "d_lambat"]].iloc[-2:-1, :]
        else:
            self.df = self.df[[k_tutup, "k_lambat", "d_lambat"]].iloc[:-1, :]

        # Membuang data dengan nilai NaN pada kolom k_lambat atau d_lambat
        self.df.dropna(subset=[k_tutup, "k_lambat", "d_lambat"], inplace=True)

        # Mengembalikan dataframe yang telah diolah
        return self.df

    # MOVING AVERAGE
    def moving_average(self):
        pass

    # PARABOLIC SAR
    def parabolic_sar(self):
        pass
