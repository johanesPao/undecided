"""
Script untuk simulasi backtest strategi trading
"""

from strategi.strategi import *

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

# VARIABEL DAN KONSTANTA
ASET = "MATICUSDTPERP"
EXCHANGE = "BINANCE"

# Inisiasi kelas strategi
strategi_backtest = Strategi(ASET, EXCHANGE, backtest=True, jumlah_periode_backtest=250)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_hold_trade_sto_1553()

if type(hasil_strategi) == list:
    # iterrows pada timeframe kecil
    list_akhir = []
    df_backtest = pd.DataFrame()
    for baris in hasil_strategi[0].iterrows():  # type: ignore : pasti mengembalikan list
        # kembalikan waktu_tf_kecil, waktu_tf_besar, k_lambat_tf_kecil,
        # d_lambat_tf_kecil, k_lambat_tf_besar, d_lambat_tf_besar
        waktu_tf_kecil = baris[0]
        k_lambat_tf_kecil = baris[1]["k_lambat"]
        d_lambat_tf_kecil = baris[1]["d_lambat"]
        # slice dataframe tf_besar dengan waktu_tf_besar <= waktu_tf_kecil
        # timeframe besar yang berbeda membutuhkan offset yang berbeda
        df_tf_besar = hasil_strategi[1][
            hasil_strategi[1].index <= (waktu_tf_kecil - pd.DateOffset(days=1))
        ].iloc[-1:, :]
        waktu_tf_besar = df_tf_besar.index[0]
        k_lambat_tf_besar = df_tf_besar.iloc[-1]["k_lambat"]
        d_lambat_tf_besar = df_tf_besar.iloc[-1]["d_lambat"]
        list_akhir.append(
            [
                waktu_tf_kecil,
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
                "k_lambat_tf_kecil",
                "d_lambat_tf_kecil",
                "waktu_tf_besar",
                "k_lambat_tf_besar",
                "d_lambat_tf_besar",
            ],
        )
    HOLD_TRADE = ""
    posisi = []
    list_df_tindakan = []
    for baris in range(len(df_backtest)):
        tindakan = []
        k_lambat_tf_kecil = df_backtest.iloc[baris]["k_lambat_tf_kecil"]
        d_lambat_tf_kecil = df_backtest.iloc[baris]["d_lambat_tf_kecil"]
        k_lambat_tf_besar = df_backtest.iloc[baris]["k_lambat_tf_besar"]
        d_lambat_tf_besar = df_backtest.iloc[baris]["d_lambat_tf_besar"]

        HOLD_TRADE = (
            "LONG_SHORT" if k_lambat_tf_besar >= d_lambat_tf_besar else "SHORT_LONG"
        )

        if HOLD_TRADE == "LONG_SHORT":
            if "LONG" not in posisi and k_lambat_tf_kecil >= d_lambat_tf_kecil:
                tindakan.append("BUKA_LONG")
                posisi.append("LONG")
            if k_lambat_tf_kecil < d_lambat_tf_kecil:
                if "SHORT" not in posisi:
                    tindakan.append("BUKA_SHORT")
                    posisi.append("SHORT")
            elif "SHORT" in posisi:
                tindakan.append("TUTUP_SHORT")
                posisi.remove("SHORT")
        elif HOLD_TRADE == "SHORT_LONG":
            if "SHORT" not in posisi and k_lambat_tf_kecil < d_lambat_tf_kecil:
                tindakan.append("BUKA_SHORT")
                posisi.append("SHORT")
            if k_lambat_tf_kecil >= d_lambat_tf_kecil:
                if "LONG" not in posisi:
                    tindakan.append("BUKA_LONG")
                    posisi.append("LONG")
            elif "LONG" in posisi:
                tindakan.append("TUTUP_LONG")
                posisi.remove("LONG")

        list_df_tindakan.append(tindakan)

    df_backtest["tindakan"] = list_df_tindakan
    # print(k_lambat_tf_kecil)

    print(df_backtest.to_string())
