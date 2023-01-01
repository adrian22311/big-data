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