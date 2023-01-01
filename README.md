Przy starcie polecam użyć `./bootstrap.sh` z katalogu projektu (podmienia on plik konfiguracyjny tak żeby nifi czytał zmienne ustawione w `./config/nifi_custom_properties.properties`)

Pobieranie danych `YT` jest ustawione tak żeby nie przekroczyło limitu, ale jeśli będzie wiele osób korzystać to wystarczy w `./config/nifi_custom_properties.properties` ustawić `nifi.google.youtube.api_key` na swój własny.

Struktura którą przyjąłem w hadoop'ie wygląda następująco:

```
└── user
    └── project
        └── master
            ├── youtubeVideoCategories
            │   └── *.orc
            └── youtubeVideos
                └── <yyyy-MM-dd>
                    └── *.orc
```

W nifi tworzone są też 2 tabele o nazwach: 
- youtubeVideoCategories
- youtubeVideos


W tabeli youtubeVideos w zmiennej `tags` tagi rodzielane są za pomocą średników `;` 






### Struktura tabeli w Hive

1. `default.youtubeVideos`

```
(
    id STRING
    ,publishedAt STRING
    ,channelId STRING
    ,description STRING
    ,channelTitle STRING
    ,tags STRING
    ,categoryId STRING
    ,defaultAudioLanguage STRING
    ,publicStatsViewable STRING
    ,viewCount INT
    ,likeCount INT
    ,commentCount INT
    ,fetchTime STRING
)
PARTITIONED by ( partition_dt STRING )
```

2. `default.youtubeVideoCategories`

```
(
    id STRING
    ,title STRING
    ,assignable STRING
    ,channelId STRING
    ,fetchTime STRING
)
```