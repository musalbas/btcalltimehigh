with con:
        cur = con.cursor()
        print "Sending query..."
        cur.execute("SELECT * FROM trades ORDER BY time LIMIT 30")
        print "Query sent."
        row = cur.fetchone()

        # While row is not empty
        while row != None:
                #print "Loop: " + str(loop_number)
                #loop_number = loop_number + 1
                print row
                # If the price found on the frow is bigger than the currently recorded highest price
                if row[2] > current_highest_price:
                        # If this is not the first row AND the day of the price in the row is the next day of the price
                        if (current_highest_price != -1 and daily_highest_prices[current_highest_price][1] > math.floor((row[1] /day_seconds) * day_seconds)):
                                # Delete the recorded highest price of that day
                                del daily_highest_prices[current_highest_price]
                        # Overwrite the price of the row
                        current_highest_price = row[2]
                        # Add the highest price into the dictionary
                        daily_highest_prices[current_highest_price] = (row[1], row[4])
                        # Print out the highest price
                        print daily_highest_prices
                # Get the next row
                row = cur.fetchone()


