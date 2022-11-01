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
ASET_DATA = "MATICUSDTPERP"
ASET = "MATICUSDT"
EXCHANGE = "BINANCE"
SALDO = 40
LEVERAGE = 10

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=220,
    saldo_backtest=70,
    leverage_backtest=10,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_26_18_8(
    interval=["4 jam", "4 jam"], k_cepat=28, k_lambat=16, d_lambat=8
)
