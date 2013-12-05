"""Web server which displays the Bitcoin all time high prices on USD
markets."""

import thread
import time

try:
    import simplejson as json
except ImportError:
    import json

import urllib
import web

class PricePoller:
    """
    Mechanism for polling the Bitcoin price on USD markets and updating the
    Bitcoin all time high price data file every interval.

    data_filename: Path to a file where the Bitcoin all time high price data is
                   stored.
    interval: Seconds to wait before each poll.

    """

    def __init__(self, data_file, interval=900):
        self.data_file = data_file
        self.interval = interval

        # Dictionary of Bitcoin all time high prices
        self.price_history = {}

    def _poll(self):
        """Poll the Bitcoin price and update self.price_history if a new all
        high has been reached."""
        # Get markets data from bitcoincharts.com
        api_url = "http://api.bitcoincharts.com/v1/markets.json"
        markets_data = json.load(urllib.urlopen(api_url))

        # Loop through all the USD markets and check if a new all time high
        # price has been reached, by looking at each market's highest trade
        # during the day
        for market in markets_data:
            if markets_data['high'] > self.get_all_time_high():
            # New high, update self.price_history
            self._update_high(markets_data['high'], markets_data['symbol'],
                              time.time())

    def _update_high(price, symbol, time):
        """Update self.price_history with a new all time high price. This works
        such that there is a maximum of one all time high price item per day."""
        # Delete the current all time high price in self.price_history if it
        # was reached on the same day as the new all time high price
        day_seconds = 60 * 60 * 24
        current_all_time_high = self.get_all_time_high()
        if (self.price_history[current_all_time_high][1]
            > math.floor(time.time() / day_seconds) * day_seconds):
            del self.price_history[current_all_time_high]

        # Add price item to self.price_history
        self.price_history[price] = (symbol, time)

    def get_all_time_high(self):
        """Return the current all time high price."""
        return max(self.price_history.keys(), key=int)

class homepage:
    """Website homepage. Called by the web.py framework."""

    def GET(self):
        """Handle GET requests."""
        return "sup?"

# Setup web.py URL mapping
urls = (
    '/', 'homepage',
)

# Start web.py application
app = web.application(urls, globals())
if __name__ == "__main__":
    app.run()
