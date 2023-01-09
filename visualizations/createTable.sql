CREATE EXTERNAL TABLE IF NOT EXISTS default.youtubeVideos (
	id STRING, 
    title STRING,
	published_at STRING,
	channel_id STRING,
	description STRING,
	channel_title STRING,
	tags STRING,
	category_id STRING,
	default_audio_language STRING,
	public_stats_viewable STRING,
	view_count INT,
	like_count INT,
	comment_count INT,
	fetch_time STRING
)
PARTITIONED by ( partition_dt STRING )
STORED as ORC 
LOCATION '/user/project/master/youtubeVideos'
tblproperties ("orc.compress"="NONE");
MSCK Repair Table youtubeVideos;


CREATE EXTERNAL TABLE IF NOT EXISTS default.youtubeVideosNew (
	id STRING, 
    title STRING,
	published_at STRING,
	channel_id STRING,
	description STRING,
	channel_title STRING,
	tags STRING,
	category_id STRING,
	default_audio_language STRING,
	public_stats_viewable STRING,
	view_count INT,
	like_count INT,
	comment_count INT,
	fetch_time STRING
)
PARTITIONED by ( partition_dt STRING )
STORED as ORC 
LOCATION '/user/project/master/youtubeVideosNew'
tblproperties ("orc.compress"="NONE");
MSCK Repair Table youtubeVideosNew;

CREATE EXTERNAL TABLE IF NOT EXISTS default.youtubeVideoCategories (
	id STRING,
    title STRING,
    assignable STRING,
	channel_id STRING,
	fetch_time STRING
)
STORED as ORC 
LOCATION '/user/project/master/youtubeVideoCategories'
tblproperties ("orc.compress"="NONE");
MSCK Repair Table youtubeVideoCategories;

CREATE VIEW IF NOT EXISTS ytVideosConverted AS
SELECT 	id, title, cast(published_at as timestamp) as published_at,
	channel_id, description, channel_title,
	split(tags, ";") as tags, category_id, default_audio_language,
	public_stats_viewable, view_count, like_count, comment_count,
	cast(fetch_time as timestamp) as fetch_time, to_date(partition_dt) as partition_dt
FROM youtubeVideos;