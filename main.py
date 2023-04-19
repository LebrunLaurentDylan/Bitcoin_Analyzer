from rates_data_manager import get_and_manage_rates_data
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from rates_data_processing import *

# end_date = date(2021, 1, 1)
end_date = date.today() - timedelta(1)
start_date = date(2020, 1, 1)
assets = "BTC/EUR"


rates = get_and_manage_rates_data(assets, start_date, end_date)
print("nb rates:", len(rates))

ma_intervals = [1, 2, 3, 4, 5, 8, 10, 15, 20, 50, 60, 70, 80, 90, 100, 150]
ma_list = []

for intervals in ma_intervals:
    ma = compute_moving_average_for_rates_data(rates, intervals)
    ma_list.append((ma, intervals))

buy_and_sell_points = compute_buy_and_sell_points_from_ma(ma_list[0][0], ma_list[1][0], 1)
initial_wallet = 1000

final_wallets_for_intervals = []  # 0 : petit interval, 1 : grand interval, 3 : wallet

# calcul de correlation
for i in range(len(ma_intervals)):
    for j in range(i+1, len(ma_intervals)):
        p = compute_buy_and_sell_points_from_ma(ma_list[i][0], ma_list[j][0], 1)
        final_wallet = compute_buy_and_sell_currency(initial_wallet, rates, p)
        final_wallets_for_intervals.append((ma_intervals[i], ma_intervals[j], final_wallet))

final_wallets_for_intervals.sort(key=lambda x: x[2], reverse=True)
for final_wallet_for_intervals in final_wallets_for_intervals:
    print(final_wallet_for_intervals)
# fin du calcul


final_wallet = compute_buy_and_sell_currency(initial_wallet, rates, buy_and_sell_points)
print("valeur du porte feuille :", initial_wallet, " EUR à la date de début:", start_date)
print("valeur du porte feuille :", round(final_wallet, 2), "EUR à la date de fin:", end_date)

# afficher date de début et de fin
# afficher le porte feuille de début et de fin


# ma20 = compute_moving_average_for_rates_data(rates, 20)
# ma100 = compute_moving_average_for_rates_data(rates, 100)

rates_dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in rates]
rates_values = [r["value"] for r in rates]
plt.ylabel(assets)
plt.plot(rates_dates, rates_values)

for ma_item in ma_list:
    ma_values = [r["value"] for r in ma_item[0]]
    plt.plot(rates_dates, ma_values, label="MA" + str(ma_item[1]))

# r = achat y= vente
# [0] date_str
# [1] true / False

for points in buy_and_sell_points:
    buy_and_sell_points_date = datetime.strptime(points[0], "%Y-%m-%d").date()
    plt.axvline(x=buy_and_sell_points_date, color='r' if points[1] else 'y')

plt.legend()
plt.show()
