from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
from datetime import date, timedelta


def create_tag_file(filepath, outpath):
    spark = SparkSession.builder.appName("CreateTagFile").getOrCreate()
    df = spark.read.option("header", "true").option("inferschema", "true").orc(filepath). \
        withColumn("partition_dt", expr("""to_date(partition_dt)"""))
    new_df = df.select("partition_dt", "tags")
    new_df = new_df.withColumn("tags", expr("explode(split(tags, ';'))"))
    new_df = new_df.dropDuplicates()
    new_df.show()
    new_df.write.format("orc").save(outpath)


if __name__ == '__main__':
    yesterday = str(date.today() - timedelta(days=1))
    create_tag_file("/user/project/master/youtubeVideos/partition_dt=" +
                    yesterday, "/user/project/master/pyTrends/todo/tags_"+yesterday+".orc")
