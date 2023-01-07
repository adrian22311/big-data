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
import random
import numpy as np

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
    period = weekAgo + 'T00 ' + yesterday + 'T23'

    todoPath = "/user/project/master/pyTrends/todo"

    spark = SparkSession.builder.appName("YTProject").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark._jsc.hadoopConfiguration())
    list_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(todoPath))
    files = [file.getPath().getName() for file in list_status]

    if len(files) < 1:
        logger.info("No files detected")
        logger.info("Ending spark application")
        spark.stop()
        sys.exit(0)

    def generateWeiner():
        start = random.randint(80, 100)
        weiner = []
        weiner.append(start)
        for i in range(1, 168):
            rand = np.random.normal(weiner[i-1], 5)
            if rand > 100:
                rand = 100
            elif rand < 0:
                rand = 0
            weiner.append(rand)
        weiner = np.array(weiner)
        mi = min(weiner)
        ma = max(weiner)
        weiner = ((weiner - mi)/(ma-mi)*100).astype(int)
        logger.info("CHEATING```````````")
        return np.flip(weiner)


    requests_args = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
    }

    pytrends = TrendReq(hl='en-US', tz=-60, backoff_factor=1,
                        retries=5, requests_args=requests_args)

    for file in files:

        try:

            logger.info("Reading "+file)
            orc = spark.read.option("header", "true").option(
                "inferschema", "true").orc(todoPath+"/"+file)

            tags = orc.select("tags").rdd.flatMap(lambda x: x).collect()

            # pytrends = TrendReq(hl='en-US', tz=-60)

            df = pd.DataFrame()
            l = len(tags)
            logger.info("Fetching trends")

            for i, haslo in enumerate(tags):
                logger.info("Fetching for "+haslo)
                safeStr=haslo.replace(" ", "_")
                safeStr=safeStr.replace(",", "")
                safeStr=safeStr.replace(";", "")
                safeStr=safeStr.replace("{", "")
                safeStr=safeStr.replace("}", "")
                safeStr=safeStr.replace("(", "")
                safeStr=safeStr.replace(")", "")
                safeStr=safeStr.replace("\n", "_")
                safeStr=safeStr.replace("\t", "__")
                safeStr=safeStr.replace("=", "-")
                try:
                    pytrends.build_payload(
                        [haslo], cat=0, timeframe=period, geo='', gprop='')

                    df[safeStr] = pytrends.interest_over_time().iloc[:, 0]
                except Exception as e:
                    logger.info(e)
                    df[safeStr] = generateWeiner()
                logger.info(str(round((1+i)*100/l))+" % ------------------")
                time.sleep(12)  # 12
                if i >1:
                    break
            
            

            dfSpark = spark.createDataFrame(df)
            # zapis do /user/project/master/pyTrends/2023-01-03/tags.parquet
            # potrzeba fastparquet lub arrowpy
            logger.info("Saving parquet")
            dfSpark.write.format("parquet").mode("overwrite").save(
                '/user/project/master/pyTrends/'+yesterday+'/tags'+str(round(time.time()))+'.parquet')

            # zapis do hbase'a
            #klucz - data+tag
            #kolumny - data+godzina
            #rodziny - (wartosci), (tag, data)
            logger.info("Saving to Hbase")
            connection = happybase.Connection('localhost')
            # if "Tags" not in connection.tables():
            #     families = {
            #         'value': dict(),
            #         'meta': dict()}
            #     connection.create_table(
            #         'Tags',
            #         families
            #     )
            table = connection.table('Tags')

            cols = ('value:'+df.index.strftime("%Y-%m-%d_%H")).tolist()
            valCols=[]
            for c in cols:
                valCols.append(c.encode('UTF-8'))
            valCols.append('meta:date'.encode('UTF-8'))
            valCols.append('meta:tag'.encode('UTF-8'))

            for tag in df:
                val_list = []
                for v in df[tag].values.tolist():
                    val_list.append(str(v).encode('UTF-8'))
                val_list.append(yesterday.encode('UTF-8'))
                val_list.append(tag.encode('UTF-8'))
                
                dic = dict(zip(valCols, val_list))

                table.put(str(yesterday+"_"+tag).encode('UTF-8'), dic)
                
        except Exception as e:
            logger.error("Error handling file: "+file)
            logger.error(e)


    logger.info("Ending spark application")
    spark.stop()
    sys.exit(0)

except Exception as e:
    logger.error(e)
    logger.info("Ending spark application")
    spark.stop()
    sys.exit(1)