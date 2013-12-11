# Download the USD trade data CSV files from bitcoincharts.com using wget.
wget http://api.bitcoincharts.com/v1/csv/ -m -r -np -A *USD.csv -R localbtcUSD.csv,*.html -c -nd -P csvs
rm -fv `find csvs -type f -size 0`
