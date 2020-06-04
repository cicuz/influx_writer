# influx_writer

Some code for uploading data from a `sqlite3` file into an `influx` database; it checks for the most recent timestamp in the latter, and queries the former only for more recent data. It's used as a `cron` job in a raspberry pi to store weather data in a consumable way.