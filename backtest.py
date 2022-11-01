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

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=1050,
    saldo_backtest=70,
    leverage_backtest=10,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_28_16_8()
