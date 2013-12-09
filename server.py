"""A web application that records and displays the current and historic Bitcoin
all time high prices."""

import cherrypy
from config import CHERRYPY_CONFIG
import datetime
import thread
import time

try:
    import simplejson as json
except ImportError:
    import json

import math
import os
import urllib


class WebApp(object):
    """CherryPy web application."""

    time_format = "%d %b %Y %H:%M"

    def __init__(self, pricepoller, index_template_file):
        self._pricepoller = pricepoller

        # Read index template
        file_handle = open(index_template_file, 'r')
        self._index_template = file_handle.read()
        file_handle.close()

    def index(self):
        """Handle requests to / (main page)."""
        out = self._index_template

        # Get the current all time high price, market symbol and time
        all_time_high_price = self._pricepoller.get_all_time_high_price()
        all_time_high = self._pricepoller.price_history[all_time_high_price]
        all_time_high_symbol = all_time_high[0]
        all_time_high_time = all_time_high[1]
        all_time_high_time = datetime.datetime.fromtimestamp(all_time_high_time
                                                             )
        all_time_high_time = all_time_high_time.strftime(self.time_format)

        # Template in the current all time high price and time
        out = out.replace("{all_time_high_price}",
                          str(int(float(all_time_high_price))))
        out = out.replace("{all_time_high_symbol}", all_time_high_symbol)
        out = out.replace("{all_time_high_time}", all_time_high_time)

        # Build table of historic all time high prices
        prices_table = ""
        prices = sorted(self._pricepoller.price_history.keys(), reverse=True,
                        key=float)
        for price in prices:
            item = self._pricepoller.price_history[price]
            symbol = item[0]
            time_string = datetime.datetime.fromtimestamp(item[1])
            time_string = time_string.strftime(self.time_format)
            prices_table += "<tr>"
            prices_table += "<td>$" + str(int(float(price))) + "</td>"
            prices_table += "<td>" + time_string + "</td>"
            prices_table += "<td>" + symbol + "</td>"
            prices_table += "</tr>"
        out = out.replace("{all_time_high_prices_table}", prices_table)

        return out

    index.exposed = True


class PricePoller:
    """
    Mechanism for polling the Bitcoin price on USD markets and updating the
    Bitcoin all time high price data file every interval.

    data_filename: Path to a file where the Bitcoin all time high price data is
                   stored.
    interval: Seconds to wait before each poll.

    """

    def __init__(self, data_file, interval=900):
        self._data_file = data_file
        self._interval = interval

        # Load the dictionary of Bitcoin all time high prices from the data
        # file
        try:
            file_handle = open(data_file, 'r')
            self.price_history = json.load(file_handle)
            file_handle.close()
        except IOError, e:
            if e.errno != 2:
                raise
            self.price_history = {}

    def _save(self):
        """Save the price history dictionary to the data file in JSON
        format."""
        file_handle = open(self._data_file, 'w')
        json.dump(self.price_history, file_handle)
        file_handle.close()

    def _update_high(self, price, symbol, unixtime):
        """Update the price history dictionary with a new all time high price.
        This works such that there is a maximum of one all time high price item
        per day."""
        # Delete the current all time high price in the price history
        # dictionary if it was reached on the same day as the new all time high
        # price
        day_seconds = 60 * 60 * 24
        current_all_time_high_price = self.get_all_time_high_price()
        if (current_all_time_high_price != -1 and
            self.price_history[current_all_time_high_price][1]
            > math.floor(time.time() / day_seconds) * day_seconds):
            del self.price_history[current_all_time_high_price]

        # Add the price item to price history dictionary
        self.price_history[price] = (symbol, unixtime)

        # Save the updated price history dictionary to the data file
        self._save()

    def get_all_time_high_price(self):
        """Return the current all time high price."""
        try:
            return max(self.price_history.keys(), key=float)
        except ValueError:
            return -1

    def poll(self):
        """Poll the Bitcoin price and update self.price_history if a new all
        high has been reached."""
        # Get markets data from bitcoincharts.com
        api_url = "http://api.bitcoincharts.com/v1/markets.json"
        markets_data = json.load(urllib.urlopen(api_url))

        # Loop through all the USD markets and check if a new all time high
        # price has been reached, by looking at each market's highest trade
        # during the day
        for market in markets_data:
            if (market['high'] > float(self.get_all_time_high_price())
                and "USD" in market['symbol']
                and market['symbol'] != "localbtcUSD"):
                # New high, update price history dictionary
                self._update_high(market['high'], market['symbol'],
                                  time.time())

    def run(self):
        """A loop that calls self.poll before every interval."""
        while True:
            self.poll()
            time.sleep(self._interval)

# Start the application
if __name__ == "__main__":
    # Start the price poller in a separate thread
    module_dirname = os.path.dirname(os.path.abspath(__file__))
    pricepoller_data_file = os.path.join(module_dirname, "price_history.json")
    pricepoller = PricePoller(pricepoller_data_file)
    thread.start_new_thread(pricepoller.run, ())

    # Create web application instance
    webapp = WebApp(pricepoller, "Default.html")

    # Configure favicon.ico
    favicon_filename = os.path.join(module_dirname, "favicon.ico")
    favicon_ico = cherrypy.tools.staticfile.handler(filename=favicon_filename)
    webapp.favicon_ico = favicon_ico

    # Start the CherryPy server
    cherrypy.config.update(CHERRYPY_CONFIG)
    cherrypy.quickstart(webapp)
