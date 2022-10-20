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
    def __init__(self) -> None:
        pass

    # definisi analisa teknikal dilakukan di bawah ini
    # STOKASTIK
    def stokastik(
        self,
        data: pd.DataFrame,
        periode_k_cepat: int = 14,
        periode_k_lambat: int = 3,
        periode_d_lambat: int = 3,
        backtest: bool = False,
    ) -> pd.DataFrame:
        """
        Implementasi dari analisa teknikal Stochastic. Mengembalikan nilai terakhir atau keseluruhan dataframe jika backtest adalah True

        Args:
          data: data dalam format pd.DataFrame dengan header kolom ['Waktu Pembukaan', 'Buka', 'Tinggi', 'Rendah', 'Tutup', 'Waktu Penutupan']
          periode_k_cepat: jumlah periode yang dipergunakan untuk perhitungan k_cepat
          periode_k_lambat: jumlah periode yang dipergunakan untuk perhitungan k_lambat
          periode_d_lambat: jumlah periode yang dipergunakan untuk perhitungan d_lambat
          backtest: mengembalikan analisa untuk keperluan backtest atau live trading

        Returns:
          Mengembalikan dataframe (k_lambat, d_lambat) terbaru atau Waktu Penutupan, k_lambat dan d_lambat untuk periode dataframe
        """
        self.data = data
        self.p_k_cepat = periode_k_cepat
        self.p_k_lambat = periode_k_lambat
        self.p_d_lambat = periode_d_lambat
        self.backtest = backtest

        df = self.data.copy()
        df = df[["open", "high", "low", "close", "volume"]]

        # Menambahkan kolom 'n_tinggi' dengan nilai maks dari n periode (self.p_k_cepat) sebelumnya
        df["n_tinggi"] = df["high"].rolling(self.p_k_cepat).max()

        # Menambahkan kolom 'n_rendah' dengan nilai minimum dari n periode (self.p_k_cepat) sebelumnya
        df["n_rendah"] = df["low"].rolling(self.p_k_cepat).min()

        # Menggunakan nilai min/maks untuk menghitung %k_cepat
        df["k_cepat"] = (
            (df["close"] - df["n_rendah"]) / (df["n_tinggi"] - df["n_rendah"])
        ) * 100

        # Menghitung nilai %k_lambat yang merupakan rata-rata dari %k_cepat selama n periode (self.p_k_lambat) sebelumnya
        df["k_lambat"] = df["k_cepat"].rolling(self.p_k_lambat).mean()

        # Menghitung nilai %d_lambat yang merupakan rata-rata dari %k_lambat selama n periode (self.p_d_lambat) sebelumnya
        df["d_lambat"] = df["k_lambat"].rolling(self.p_d_lambat).mean()

        # Jika bukan backtest, kembalikan kolom k_lambat dan d_lambat dari baris terakhir data
        # Dengan perubahan data API endpoint ke tradingview, baris terakhir akan menghasilkan nilai yang berjalan dan belum close, ambil data pada urutan baris kedua terakhir saja (dalam kasus backtest false) atau sampai dengan dua baris terakhir saja (dalam kasus backtest true)
        if not self.backtest:
            df = df[["k_lambat", "d_lambat"]].iloc[-2:-1, :]
        else:
            df = df[["k_lambat", "d_lambat"]].iloc[:-1, :]

        # Membuang data dengan nilai NaN pada kolom k_lambat atau d_lambat
        df.dropna(subset=["k_lambat", "d_lambat"], inplace=True)

        return df

    # MOVING AVERAGE
    def moving_average(self):
        pass

    # PARABOLIC SAR
    def parabolic_sar(self):
        pass
