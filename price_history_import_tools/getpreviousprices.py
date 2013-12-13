try:
    import simplejson as json
except ImportError:
    import json

import math
import MySQLdb
import MySQLdb.cursors
import sys

day_seconds = 60 * 60 * 24
current_highest_price = -1
daily_highest_prices = {}

con = MySQLdb.connect("localhost", "btcalltimehigh", "", "btcalltimehigh",
                      cursorclass=MySQLdb.cursors.SSCursor)

with con:

    cur = con.cursor()
    print "Executing MySQL query... ",
    sys.stdout.flush()
    cur.execute("SELECT * FROM trades ORDER BY time")
    print "done."
    row = cur.fetchone()

    while row != None:

        if row[2] > current_highest_price:
            if (current_highest_price != -1
                and daily_highest_prices[current_highest_price][1]
                > math.floor(row[1] / day_seconds) * day_seconds
                and daily_highest_prices[current_highest_price][1]
                < math.ceil(float(row[1]) / day_seconds) * day_seconds):
                del daily_highest_prices[current_highest_price]

            current_highest_price = row[2]
            daily_highest_prices[current_highest_price] = (row[4], row[1])

            print ("New all time high: $" + str(current_highest_price) + ", "
                   + str(row[1]) + ", " + row[4] + ".")

        row = cur.fetchone()

    print "Saving data to price_history.json... "
    sys.stdout.flush()
    file_handle = open("price_history.json", 'w')
    json.dump(daily_highest_prices, file_handle)
    file_handle.close()
    print "done."
