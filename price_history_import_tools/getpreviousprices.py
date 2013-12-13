try:
    import simplejson as json
except ImportError:
    import json

import math
import MySQLdb as mdb

day_seconds = 60 * 60 * 24
current_highest_price = -1
daily_highest_prices = {}

con = mdb.connect("localhost", "btcalltimehigh", "", "btcalltimehigh")

with con:

    cur = con.cursor()
    cur.execute("SELECT * FROM trades ORDER BY time")
    row = cur.fetchone()

    while row != None:

        if row[2] > current_highest_price:
            if (current_highest_price != -1
                and daily_highest_prices[current_highest_price][1]
                > math.floor(row[1] / day_seconds) * day_seconds
                and daily_highest_prices[current_highest_price][1]
                < math.ceil(row[1] / day_seconds) * day_seconds):
                del daily_highest_prices[current_highest_price]

            current_highest_price = row[2]
            daily_highest_prices[current_highest_price] = (row[1], row[4])

        row = cur.fetchone()

    file_handle = open("price_history.json", 'w')
    json.dump(daily_highest_prices, file_handle)
    file_handle.close()
