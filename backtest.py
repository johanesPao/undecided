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
strategi = Strategi(ASET, EXCHANGE, backtest=True, jumlah_periode_backtest=1000)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi.jpao_hold_trade_sto_1533()
