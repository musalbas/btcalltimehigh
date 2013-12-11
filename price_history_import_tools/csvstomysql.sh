# Merge all of the trade data CSV files in the csvs directory into a single MySQL table (table 'trades' in mysql://btcalltimehigh@localhost/btcalltimehigh).
mysql -u btcalltimehigh -e "USE btcalltimehigh; DROP TABLE trades;" > /dev/null
mysql -u btcalltimehigh -e "USE btcalltimehigh; CREATE TABLE trades(id INT NOT NULL AUTO_INCREMENT, time INT NOT NULL, price FLOAT NOT NULL, volume FLOAT NOT NULL, market VARCHAR(12) NOT NULL, PRIMARY KEY(id));"

for f in $(find csvs -name "*.csv")
do

    bn=`basename $f`

    printf "Formatting "
    printf $f
    printf "... "

    cat $f | sed -e "s/$/,${bn%%.csv}\"/" -e "s/^/\"/" -e "s/,/\",\"/g" > /tmp/trades.csv
    printf "done.\n"

    printf "Importing "
    printf $f
    printf " to MySQL database... "

    mysqlimport --fields-enclosed-by="\"" --fields-terminated-by=, --columns "time,price,volume,market" --local -u btcalltimehigh btcalltimehigh /tmp/trades.csv | sed -e "s/$/, done./"

done

rm -f /tmp/trades.csv
