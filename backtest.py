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

# # NIR
# k_cepat = 300
# k_lambat = 300
# d_lambat = 30

# RTW
# periode_ma_cepat = 21
# periode_ma_lambat = 69

# DSHA
smoothed = True
tipe_ma_smoothing = ["ema"]
smoothing_1 = 4
smoothing_2 = 9
ma_1 = 20
ma_2 = 50

# RTE
# periode_ema = 36
# periode_ema_cepat = 5
# dual_ema = False
# smoothing = 14
# demastoch = False
# k_cepat = 50
# k_lambat = 400
# d_lambat = 100

# SMV
# periode_ma = 7
# smoothing = 21

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=600,
    saldo_backtest=66,
    leverage_backtest=25,
    jumlah_trade_usdt=12,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
# hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_28_16_8(
#     interval=["1 jam", "1 jam"],
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
# )

# hasil_strategi = strategi_backtest.jpao_ride_the_wave(
#     interval=["1 menit"],
#     periode_ma_cepat=periode_ma_cepat,
#     periode_ma_lambat=periode_ma_lambat,
# )

hasil_strategi = strategi_backtest.jpao_double_smoothed_heiken_ashi(
    interval=["1 menit"],
    smoothed_ha=smoothed,
    tipe_ma_smoothing=tipe_ma_smoothing, # type: ignore
    smoothing_1=smoothing_1,
    smoothing_2=smoothing_2,
    periode_ma_1=ma_1,
    periode_ma_2=ma_2,
)

# hasil_strategi = strategi_backtest.jpao_ride_the_ema(
#     interval=["1 menit"],
#     periode_ema=periode_ema,
#     smoothing=smoothing,
#     dual_ema=dual_ema,
#     periode_ema_cepat=periode_ema_cepat,
#     demastoch=demastoch,
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
# )

# hasil_strategi = strategi_backtest.jpao_smooth_ma_velocity(
#     interval=["3 menit"], periode_ma=periode_ma, smoothing=smoothing
# )
