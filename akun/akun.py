"""
Script untuk kelas Akun
Script untuk melakukan penarikan data akun di exchange
"""

import datetime as dt
import numpy as np
import pandas as pd
import time
from binance import Client

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class InfoAkun:
    """
    Kelas InfoAkun merupakan penghubung antara program dengan API binance yang berkaitan dengan informasi akun pengguna


    Atribut
    -------
    exchange (Client):
        Objek Client dari binance.Client

    Metode
    ------
    akun_spot() -> tuple:
        Mengembalikan informasi akun di pasar spot
    akun_futures() -> tuple:
        Mengembalikan informasi akun di pasar futures
    harga_koin_terakhir(simbol: str) -> float:
        Mengembalikan harga terakhir dari simbol koin yang diberikan pada metode ini
    """

    def __init__(self, exchange: Client) -> None:
        """
        Metode inisiasi kelas InfoAkun

        Argumen
        _______
        exchange:
            Objek Client dari binance.Client

        Return
        ______
        (None)
        """
        self.exchange = exchange

    def akun_spot(self) -> tuple:
        """
        Metode untuk mengembalikan informasi akun di pasar spot

        Argumen
        _______
        (None)

        Return
        ______
        (tuple):
            Mengembalikan data akun di pasar spot dalam bentuk tuple (makerCommision, takerCommision, buyerCommision, sellerCommision dan pd.DataFrame saldo_aset_spot)
        """
        # AKUN SPOT
        spot = self.exchange.get_account()

        # SALDO SPOT
        saldo_aset_spot = pd.DataFrame(spot["balances"])

        # KONVERSI OBJEK MENJADI NILAI NUMERIK
        kolom_numerik = ["free", "locked"]
        saldo_aset_spot[kolom_numerik] = saldo_aset_spot[kolom_numerik].apply(
            pd.to_numeric, axis=1
        )
        saldo_aset_spot = saldo_aset_spot[
            np.count_nonzero(saldo_aset_spot.values, axis=1)
            > len(saldo_aset_spot.columns) - 2
        ]

        # DATA FEE SPOT
        maker_commission = spot["makerCommission"]
        taker_commission = spot["takerCommission"]
        buyer_commission = spot["buyerCommission"]
        seller_commission = spot["sellerCommission"]

        return (
            maker_commission,
            taker_commission,
            buyer_commission,
            seller_commission,
            saldo_aset_spot,
        )

    def akun_futures(self) -> tuple:
        """
        Metode untuk mengembalikan informasi akun di pasar futures

        Argumen
        -------
        (None)

        Return
        ------
        (tuple):
            Mengembalikan data akun di pasar futures dalam bentuk tuple (feeTier, total_saldo, saldo_tersedia, saldo_terpakai, laba_rugi_terbuka, saldo_plus_profit dan pd.DataFrame data_posisi_df)
        """
        # AKUN FUTURES
        futures = self.exchange.futures_account()
        fee_tier = futures["feeTier"]
        total_saldo = float(futures["totalWalletBalance"])
        saldo_tersedia = float(futures["availableBalance"])
        saldo_terpakai = total_saldo - saldo_tersedia
        laba_rugi_terbuka = float(futures["totalUnrealizedProfit"])
        saldo_plus_profit = float(futures["totalMarginBalance"])
        data_posisi_df = pd.DataFrame(futures["positions"])
        data_posisi_df = data_posisi_df.loc[
            pd.to_numeric(data_posisi_df["initialMargin"]) > 0
        ]
        data_posisi_df = data_posisi_df[
            [
                "symbol",
                "positionSide",
                "positionAmt",
                "leverage",
                "isolated",
                "initialMargin",
                "maintMargin",
                "isolatedWallet",
                "entryPrice",
                "unrealizedProfit",
            ]
        ]

        return (
            fee_tier,
            total_saldo,
            saldo_tersedia,
            saldo_terpakai,
            laba_rugi_terbuka,
            saldo_plus_profit,
            data_posisi_df,
        )

    def harga_koin_terakhir(self, simbol: str) -> float:
        """
        Metode untuk mengembalikan harga koin terakhir di pasar futures

        Argumen
        -------
        simbol (str):
            Simbol koin yang ingin diketahui harga terakhirnya di pasar futures

        Return
        ------
        (float):
            harga koin terakhir untuk simbol yang diberikan pada metode ini di pasar futures
        """
        return float(self.exchange.futures_ticker(symbol=simbol)["lastPrice"])

    def harga_pnl_transaksi_terakhir(
        self, simbol: str, sisi: str, limit: int = 20
    ) -> tuple:
        time.sleep(1)  # jeda 1 detik sebelum mengambil data trannsaksi
        df_transaksi = pd.DataFrame(
            self.exchange.futures_account_trades(symbol=simbol, limit=limit)
        )

        df_transaksi = df_transaksi[df_transaksi["positionSide"] == sisi]

        df_transaksi["realizedPnl"] = df_transaksi["realizedPnl"].astype(float)
        df_transaksi["commission"] = df_transaksi["commission"].astype(float)
        df_transaksi["price"] = df_transaksi["price"].astype(float)
        df_transaksi["qty"] = df_transaksi["qty"].astype(int)
        df_transaksi["time"] = (
            pd.to_datetime(df_transaksi["time"], unit="ms")
            .dt.tz_localize("UTC")
            .dt.tz_convert("Asia/Jakarta")
        )

        df_transaksi["pnl_setelah_komisi"] = (
            df_transaksi["realizedPnl"] - df_transaksi["commission"]
        )
        df_transaksi["nilai_total"] = df_transaksi["price"] * df_transaksi["qty"]
        df_ringkasan = df_transaksi.groupby(["orderId"]).aggregate(
            {"pnl_setelah_komisi": "sum", "nilai_total": "sum", "qty": "sum"}
        )
        df_ringkasan["harga"] = df_ringkasan["nilai_total"] / df_ringkasan["qty"]

        return round(df_ringkasan.iloc[-1]["harga"], 5), round(  # type: ignore
            df_ringkasan.iloc[-1]["pnl_setelah_komisi"], 5  # type: ignore
        )
