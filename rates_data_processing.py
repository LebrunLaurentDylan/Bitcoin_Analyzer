
def compute_moving_average_for_rates_data(rates, nb_days_interval):
    #  0 1 2 3 4 5 6 7 8 (index) / nb_days_interval = 3
    #  5 6 4 2 8 9 4 0 7 (valeurs)
    # faire la moyenne des trois valeurs à l'index et précedent l'index
    ''' Pour le démarrage prendre les valeurs les additionners puis les diviser par l'index +1 quand len(index) est
    inferieur à nb_days_interval sauf quand len(index) inférieur à 2 ; ou on prend juste la valeur et c'est tout. Ensuite
    sauvegarder une somme "s" des (valeurs) à chaque index rajouter la somme et quand index est >= nb_days_interval
    rajouter la somme suivante puis retirer la première valeur avant de diviser par nb_days_interval
    chaque somme S ainsi produite sera rajoutée à une variable 'averages' = [{'date':..date_str, 'value':..somme}]
    qui sera la variable retournée par la fonction "compute_moving_average_for_rates_data" '''

    # ma solus (fausse):
    '''for r in rates:
        while len(r) <= nb_days_interval:
            if len(r) < 1:
                s = r["value"]
                averages.append({'dates': r['date'], 'value' :s})
            if len(r) >= 1:
                s += r['value'] / len(r)
                averages.append({'dates': r['date'], 'value': s})
        if len(r) > nb_days_interval:
            s += r['value'] - len(r['value']) - nb_days_interval / nb_days_interval
            averages.append({'dates': r['date'], 'value': s})'''
    s = 0
    averages = []
    # solus cours
    for i in range(len(rates)):
        rate = rates[i]
        s += rate['value']
        a = 0
        if i >= nb_days_interval:
            s -= rates[ i -nb_days_interval]["value"]
            a = s / nb_days_interval
        else:
            a = s / (i + 1)
        averages.append({'date': rate['date'], 'value': a})

    return averages


def compute_buy_and_sell_points_from_ma(short_ma, long_ma, threshold_percent=0):
    buy_mode = True
    points = []

    # [('date_str', buy_mode)] # buy_mode = True (achat) / False(vente)
    for i in range(len(short_ma)):
        date_str = short_ma[i]["date"]
        sma_value = short_ma[i]["value"]
        lma_value = long_ma[i]["value"]
        mult = 1+ threshold_percent / 100
        if buy_mode:  # on cherche un point d'achat
            if sma_value > lma_value * mult:
                points.append((date_str, buy_mode))
                buy_mode = False
        else:
            if sma_value < lma_value / mult:
                points.append((date_str, buy_mode))
                buy_mode = True

    return points


def get_rate_value_for_date_str(rates, date_str):
    # cherche: la "value" du cours à une date donnée et la retourne, si pas trouvé retourne : None
    # ma solus (marche)
    for i in rates:
        if date_str == i["date"]:
            return i["value"]
    return None


def compute_buy_and_sell_currency(initial_wallet, rates, buy_and_sell_points):
    # itérer sur point d'achat et de vente ==> toujours terminer sur un point de vente
    # connaitre la valeur du cours à une date donnée (get_rate_value_for_date_str)
    # current_wallet = 0 // correspond au porte_feuille (argent)
    # shares = 0 // correspond au nombre de bitcoin

    # ma solus (marche)
    current_wallet = initial_wallet
    last_wallet = 0
    shares = 0

    if buy_and_sell_points[-1][1]:
        buy_and_sell_points = buy_and_sell_points[:-1]

    for points in buy_and_sell_points:
        value_at_date = get_rate_value_for_date_str(rates, points[0])
        if points[1]:  # buy_mode = True
            shares = current_wallet / value_at_date
            print("le", points[0], ":", round(current_wallet, 2), "EUR échangé contre : ", round(shares, 2), "BTC.")
            last_wallet = current_wallet
            current_wallet = 0
        else:  # buy_mode = False
            current_wallet = shares * value_at_date
            shares = 0
            print("le", points[0], ":", round(shares, 2), "BTC échangé contre :", round(current_wallet, 2), "EUR  ")
            if current_wallet > last_wallet:
                percent = (current_wallet-last_wallet)*100/last_wallet
                print(f"soit un gain de {round(percent,1)}%")
            else:
                percent = (last_wallet-current_wallet) * 100 / last_wallet
                print(f"soit une perte de {round(percent, 1)}%")
            print()

    return current_wallet  # final_wallet # retourne le portefeuille final
