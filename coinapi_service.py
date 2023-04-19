from datetime import date, datetime, timedelta
import requests
import json
from coinapi_config import API_KEY, BASE_URL

headers = {"X-CoinAPI-Key": API_KEY}


'''def coinapi_service_get_all_assets():

    url = BASE_URL + "v1/assets"
    response = requests.get(url, headers=headers)

    #  200 sinon afficher numéro erreur
    if response.status_code == 200:
        print("Appel validé !")
        data = json.loads(response.text)
        nb_asset = len(data)
        print("nombre d'assets monétaires: ", nb_asset)

        if nb_asset >= 10:
            for i in range(10):
                d = data[i]
                print(d["asset_id"] + ": " + d["name"])
        print()
        print("quota d'appels restant: ", response.headers['x-ratelimit-remaining'])
    else:
        print("ERREUR: " + str(response.status_code))'''

# period_id , 1DAY
# url = 'https://rest.coinapi.io/v1/exchangerate/BTC/USD/history?period_id=1MIN&time_start=2016-01-01T00:00:00&time_end=2016-02-01T00:00:00'
# date_start / date_end : date objects
# max_days : int
# start : 2023-03-27
# end : 2023-04-07
# [] -> decouper en interval de max 100 jours


def get_dates_intervals(date_start, date_end, max_days):
    diff = date_end - date_start
    diff_days = diff.days
    dates_intervals = []
    interval_begin_date = date_start
    while diff_days > 0:
        nb_days_to_add = max_days-1
        if diff_days < max_days-1:
            nb_days_to_add = diff_days
        interval_end_date = interval_begin_date + timedelta(nb_days_to_add)
        dates_intervals.append([interval_begin_date, interval_end_date])
        diff_days -= nb_days_to_add+1
        interval_begin_date = interval_end_date + timedelta(1)

    return dates_intervals


# extended : start and end dates can be seperated more than 100 days
def coin_api_get_exchange_rates_extended(assets, date_start, date_end):
    rates = []
    dates_intervals = get_dates_intervals(date_start, date_end, 100)
    if len(dates_intervals) > 0:
        for i in dates_intervals:
            rates += coin_api_get_exchange_rates(assets, i[0], i[1])
    return rates


def coin_api_get_exchange_filtered_rates_extended(assets, date_start, date_end):
    rates = coin_api_get_exchange_rates_extended(assets, date_start, date_end)
    filtered_rates = filter_inconsistent_rates_values(rates)
    return filtered_rates


def rate_is_inconsistent(rate):
    v = rate["rate_open"]
    vmin = v / 10
    vmax = v * 10
    if not vmin <= rate["rate_close"] <= vmax:
        return True
    if not vmin <= rate["rate_high"] <= vmax:
        return True
    if not vmin <= rate["rate_low"] <= vmax:
        return True
    return False


def filter_inconsistent_rates_values(input_rates):
    if len(input_rates) < 2:
        return input_rates
    filtered_rates = []
    for i in range(len(input_rates)):
        r = input_rates[i]
        if rate_is_inconsistent(r):
            # prendre le jour précedent ou suivant
            if i > 0:
                refence_rate = input_rates[i - 1]
            else:
                refence_rate = input_rates[i + 1]
            patched_rate = r
            patched_rate["rate_open"] = refence_rate["rate_open"]
            patched_rate["rate_close"] = refence_rate["rate_close"]
            patched_rate["rate_high"] = refence_rate["rate_high"]
            patched_rate["rate_low"] = refence_rate["rate_low"]
            filtered_rates.append(patched_rate)
        else:
            filtered_rates.append(r)

    return filtered_rates

# assets : str"BTS/EUR"
# date_start / date_end : date objects (inclusive)
def coin_api_get_exchange_rates(assets, date_start, date_end):
    date_start_str = date_start.strftime("%Y-%m-%d")
    date_end_str = (date_end + timedelta(1)).strftime("%Y-%m-%d")
    url = BASE_URL + 'v1/exchangerate/' + \
          assets + '/history?period_id=1DAY&time_start=' +\
          date_start_str + 'T00:00:00&time_end=' + date_end_str + "T00:00:00"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Appel validé !")
        data = json.loads(response.text)
        nb_asset = len(data)
        print("quota d'appels restant: ", response.headers['x-ratelimit-remaining'])
        return data
    else:
        print("ERREUR: " + str(response.status_code))
        return None
# 'rate_close'
# 'time_period_start'
