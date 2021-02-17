from geopy import exc
import requests
import argparse
import geocoder
from configparser import ConfigParser
from geopy.geocoders import Nominatim
import sqlite3
from datetime import datetime
geolocator = Nominatim(user_agent="geoapiExercises")
import chalk

def get_city()->str:
    g = geocoder.ip('me')
    latlng = g.latlng
    location = geolocator.reverse(str(latlng[0])+","+str(latlng[1]))
    city = location.raw['address'].get('city')
    return city

parser = argparse.ArgumentParser(description='''
You need to pass --city for the city you wanted to get the weather forecast.Default is your current city.
You can also pass the number of days of forecast needed as --days.Default value is 1.
For eg: python3 day1.py --city Delhi --days 2
        python3 day1.py --city Delhi
        python3 day1.py --days 2
''',
epilog="Hope you will enjoy our services")
parser.add_argument("--city",help="The city for which you want to get the weather forecast",type=str,default=get_city())
parser.add_argument("--days",help="Number of days of forecast you want",type=int,default=1)
args = parser.parse_args()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn

def create_table(c):
    create_sql = """
        CREATE TABLE IF NOT EXISTS weatherdata (
            city string PRIMARY_KEY,
            weather text NOT NULL,
            temp REAL,
            date text
        )
    """
    try:
        c.execute(create_sql)
    except Exception as e:
        print("Error in creating table :", e)

def query_table(c,city,today_date):
    try:
        c.execute("SELECT * FROM weatherdata where city=? AND date=?",(city,today_date))
        rows = c.fetchall()
        print(rows)
        for row in rows:
            return row
    except Exception as e:
        return None


def get_weather_data(c, city, today_date):
    if(query_table(c, city, today_date)):
        print(query_table(c, city, today_date))
        print(chalk.blue('Got the value from db, did not made api call'))
        return 
    else:
        try:
            openweatherurl = 'https://api.openweathermap.org/data/2.5/weather/'
            q_params = {
                'q': city,
                'appid': '367734831231fafde06835375aa51401'
            }
            response = requests.get(url=openweatherurl, params=q_params)
            resp = response.json()
            try:

                c.execute("INSERT into weatherdata (city,weather,temp,date) VALUES(?,?,?,?)", (
                    city, resp['weather'][0]['description'], resp['main']['temp'], today_date))
            except Exception as e:
                print('Unable to save data into database: ', e)
                return
            print(f"Current temperature is : {resp['main']['temp']}")
            print(f"Description is : {resp['weather'][0]['description']}")
            return

        except Exception as e:
            print('Unable to get data from Internet. Please try after sometime. ', e)
            return
if __name__ =="__main__":
    print(chalk.green('Welcome to weather forecast application'))
    city = args.city
    days = args.days
    try:
        config = ConfigParser()
        config.read('secret.ini')
        secretkey = config.get('Weather','apikey')
        db_file = config.get('database','file')
    except Exception as e:
        print("Error in reading config")
    # Will try first with openweather api
    conn = create_connection(db_file)
    c = conn.cursor()
    create_table(c)
    today_date = datetime.today().strftime('%Y-%m-%d')
    get_weather_data(c,city,today_date)
    print(chalk.green('Hope you enjoyed our service.'))
    
