"""
Script untuk kelas Akun
Script untuk melakukan penarikan data akun di exchange
"""

import numpy as np
import pandas as pd
from binance import Client

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class InfoAkun:
    def __init__(self, exchange: Client) -> None:
        self.exchange = exchange
        pass

    def akun_spot(self) -> tuple:
        # AKUN SPOT
        spot = self.exchange.get_account()

        # SALDO SPOT
        saldo_aset_spot = pd.DataFrame(spot["balances"])

        # konversi objek menjadi nilai numerik
        kolom_numerik = ["free", "locked"]
        saldo_aset_spot[kolom_numerik] = saldo_aset_spot[kolom_numerik].apply(
            pd.to_numeric, axis=1
        )
        saldo_aset_spot = saldo_aset_spot[
            np.count_nonzero(saldo_aset_spot.values, axis=1)
            > len(saldo_aset_spot.columns) - 2
        ]

        # fee spot
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
        return float(self.exchange.futures_ticker(symbol=simbol)["lastPrice"])
