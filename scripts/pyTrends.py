from pytrends.request import TrendReq
import pandas as pd
import time
from pyspark.sql import SparkSession
from datetime import date, timedelta
from os import listdir
from os.path import isfile, join


yesterday = str(date.today() - timedelta(days=1))
name = "tags"  # jaka nazwa

# wybierz pliki .orc
path = "/user/projekt/master/youtubeVideos/"+yesterday
files = [f for f in listdir(path) if isfile(
    join(path, f)) and f.endswith('.orc')]

# spark session
spark = SparkSession.builder.appName(
    "YTProject").enableHiveSupport().getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
logger.info("Starting spark application")
logger.info("Reading ORC Files")

# tagi do listy
for f in files:
    tags = spark.read.orc(f).tags.values.tolist()
    lista = []
    for t in tags:
        temp = t.split(";")
        for tag in temp:
            lista.append(tag)

# usun duplikaty
lista = [*set(lista)]

logger.info("Previewing tags")
logger.info(lista)

# end Spark session
logger.info("Ending spark application")
spark.stop()


pytrends = TrendReq(hl='en-US', tz=-60)

df = pd.DataFrame()

for haslo in lista:
    pytrends.build_payload(
        [haslo], cat=0, timeframe='now 7-d', geo='', gprop='')
    df[haslo] = pytrends.interest_over_time().iloc[:, 0]
    time.sleep(12)  # 12

# potrzeba fastparquet lub arrowpy
df.to_parquet(path+"/"+name+".parquet")  # sciezka
