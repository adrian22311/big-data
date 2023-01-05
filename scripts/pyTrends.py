from pytrends.request import TrendReq
import pandas as pd
import time
import happybase
from pyspark.sql import SparkSession
from datetime import date, timedelta
import os
import sys
import logging
import pyarrow as pa
import pyarrow.parquet as pq

# Logging configuration
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

try:

    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    weekAgo = str(date.today() - timedelta(days=7))
    period = weekAgo + 'T00 ' + today+'T00'
    name = "tags"  # jaka nazwa

    path = "/user/project/master/youtubeVideos/"+yesterday+"/test.orc"

    # pyspark hive
    # kilka plików
    # z wczoraj tagi
    # zapis do /user/project/master/pyTrends/2023-01-03/tags.parquet
    # potem do hbase'a

    # spark session
    spark = SparkSession.builder.appName(
        "YTProject").enableHiveSupport().getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    logger.info("Querying Hive for tags")
    # orc = spark.read.orc(path)
    # logger.info(orc)

    spark.sql("show tables").show()
    lista = spark.sql(
        'select distinct explode(split(tags, ";")) from youtubevideos').collect()

    # lista = []
    # for t in tags:
    #     splitted = t.split(";")
    #     lista.extend(splitted)

    # usun duplikaty
    #lista = [*set(lista)]

    logger.info("Previewing tags")
    logger.info(lista)

    # end Spark session

    pytrends = TrendReq(hl='en-US', tz=-60)

    df = pd.DataFrame()

    for haslo in lista:
        pytrends.build_payload(
            [haslo], cat=0, timeframe=period, geo='', gprop='')  # switch to const hours
        df[haslo] = pytrends.interest_over_time().iloc[:, 0]
        time.sleep(12)  # 12

    df = spark.createDataFrame(df)
    # zapis do /user/project/master/pyTrends/2023-01-03/tags.parquet
    # potrzeba fastparquet lub arrowpy
    df.write.format("parquet").mode("overwrite").save(
        '/user/project/master/pyTrends/'+yesterday+'/tags.parquet')
    # zapisujemy na HDFS, który jest dostępny lokalnie

    # zapis do hbase'a
    #klucz - data+tag
    #kolumny - data+godzina
    #rodziny - (wartosci), (tag, data)

    connection = happybase.Connection('localhost')
    if "Tags" not in connection.tables():
        families = {
            'value': dict(),
            'meta': dict()}
        connection.create_table(
            'Tags',
            families
        )
    table = connection.table('Tags')

    valCols = list('value:'+df.index.strftime("%Y-%m-%d_%H"))
    valCols.append('meta:date')
    valCols.append('meta:tag')

    d = dict(zip(valCols, val_list))

    for tag in df:
        val_list = df[tag].values.tolist()
        val_list.append(yesterday)
        val_list.append(tag)

        table.put(str(day+" "+tag), dict(zip(valCols, val_list)))

    logger.info("Ending spark application")
    spark.stop()
    sys.exit(0)

except Exception as e:
    logger.error(e)
    logger.info("Ending spark application")
    spark.stop()
    sys.exit(1)
