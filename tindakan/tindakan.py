"""
Script untuk kelas Order
Script ini akan melakukan eksekusi order buka_long, buka_short, tutup_long atau tutup_short
"""

from akun.akun import InfoAkun
from baca_konfig import Inisiasi

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

inisiasi_konektor = Inisiasi()
exchange = inisiasi_konektor.exchange()


class Order:
    def __init__(self, aset: str) -> None:
        self.inisiasi_konektor = Inisiasi()
        self.exchange = self.inisiasi_konektor.exchange()
        self.info_akun = InfoAkun(self.exchange)
        self.aset = aset

    def buka_long(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="BUY",
                positionSide="LONG",
                quantity=kuantitas,
            )

            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_long = df_saldo_futures[df_saldo_futures["positionSide"] == "LONG"]
            harga_masuk_long = df_long.iloc[0]["entryPrice"]
            saldo_long = df_long.iloc[0]["isolatedWallet"]

            return print(
                f"Posisi LONG senilai {saldo_long} USDT berhasil dibuka untuk {self.aset} pada harga {harga_masuk_long}"
            )
        except:
            return print(f"Posisi LONG tidak berhasil dibuka untuk {self.aset}")

    def buka_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="SELL",
                positionSide="SHORT",
                quantity=kuantitas,
            )
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_short = df_saldo_futures[df_saldo_futures["positionSide"] == "SHORT"]
            harga_masuk_short = df_short.iloc[0]["entryPrice"]
            saldo_short = df_short.iloc[0]["isolatedWallet"]

            return print(
                f"Posisi SHORT senilai {saldo_short} USDT berhasil dibuka untuk {self.aset} pada harga {harga_masuk_short}"
            )
        except:
            return print(f"Posisi SHORT tidak berhasil dibuka untuk {self.aset}")

    def tutup_long(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_long = df_saldo_futures[df_saldo_futures["positionSide"] == "LONG"]
            saldo_long = df_long.iloc[0]["isolatedWallet"]

            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="SELL",
                positionSide="LONG",
                quantity=kuantitas,
            )

            return print(
                f"Posisi LONG senilai {saldo_long} USDT berhasil ditutup untuk {self.aset}"
            )
        except:
            return print(f"Posisi LONG tidak berhasil ditutup untuk {self.aset}")

    def tutup_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_short = df_saldo_futures[df_saldo_futures["positionSide"] == "SHORT"]
            saldo_short = df_short.iloc[0]["isolatedWallet"]

            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="BUY",
                positionSide="SHORT",
                quantity=kuantitas,
            )

            return print(
                f"Posisi SHORT senilai {saldo_short} USDT berhasil ditutup untuk {self.aset}"
            )
        except:
            return print(f"Posisi SHORT tidak berhasil ditutup untuk {self.aset}")
