#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import matplotlib.pyplot as plt


# In[2]:


#Setting our application name
appname = "ChangeColumnNames"
 
#Create spark session
spark = SparkSession.builder.appName(appname).getOrCreate()


# In[3]:


main_table_path = "/user/project/master/youtubeVideosTemp"
fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
list_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(main_table_path))
partitions = [file.getPath().getName() for file in list_status]
partitions


# In[4]:


struct1 = StructType([
    StructField("id", StringType(), False),
    StructField("publishedAt", StringType(), True),
    StructField("channelId", StringType(), True),
    StructField("description", StringType(), True),
    StructField("channelTitle", StringType(), True),
    StructField("tags", StringType(), True),
    StructField("categoryId", StringType(), True),
    StructField("defaultAudioLanguage", StringType(), True),
    StructField("publicStatsViewable", StringType(), True),
    StructField("viewCount", IntegerType(), True),
    StructField("likeCount", IntegerType(), True),
    StructField("commentCount", IntegerType(), True),
    StructField("fetchTime", StringType(), True),
    StructField("partition_dt", StringType(), False)
])


# In[5]:


for partition in partitions:
    files_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(f"{main_table_path}/{partition}"))
    files = [file.getPath().getName() for file in files_status]
    for file in files:
        df = spark.read.schema(struct1).orc(f"{main_table_path}/{partition}/{file}")
        change = False
        
        for column in df.columns:
            if column != column.lower():
                change = True
                break
        
        if change:        
            new_df = df.selectExpr("id", "publishedAt as published_at", "channelId as channel_id", "description", "channelTitle as channel_title", "tags", "categoryId as category_id", 
                                   "defaultAudioLanguage as default_audio_language", "publicStatsViewable as public_stats_viewable", "viewCount as view_count", "likeCount as like_count", 
                                   "commentCount as comment_count", "fetchTime as fetch_time", "partition_dt")
        else:
            new_df = df
        new_df.write.option("header", True).orc(f"/user/project/master/youtubeVideosTemp2/{partition}/{file}", mode="overwrite", compression="none")


# In[6]:


main_table_path = "/user/project/master/youtubeVideosTemp2"
fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
list_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(main_table_path))
partitions = [file.getPath().getName() for file in list_status]
partitions


# In[7]:


conf = spark._jsc.hadoopConfiguration()
Path = spark._jvm.org.apache.hadoop.fs.Path
FileUtil = spark._jvm.org.apache.hadoop.fs.FileUtil


# In[9]:


for partition in partitions:
    files_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(f"{main_table_path}/{partition}"))
    files_orc = [file.getPath().getName() for file in files_status]
    for orc in files_orc:
        copy_files = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(f"{main_table_path}/{partition}/{orc}"))
        copy_files = [file.getPath().getName() for file in copy_files if file.getPath().getName() != "_SUCCESS"]
        for copy_file in copy_files:
            src_path = Path(f"/user/project/master/youtubeVideosTemp2/{partition}/{orc}/{copy_file}")
            dest_path = Path(f"/user/project/master/youtubeVideos/{partition}/{orc}")
            FileUtil.copy(src_path.getFileSystem(conf), 
                  src_path,
                  dest_path.getFileSystem(conf),
                  dest_path,
                  True, conf)


# In[10]:


df = spark.read.orc("/user/project/master/youtubeVideos")
df


# In[11]:


df.show()


# In[12]:


df.count()

