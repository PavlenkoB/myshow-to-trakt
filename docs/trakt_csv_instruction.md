Your CSV file should contain a header row followed by one row per item to import.

Поля
id
The ID can be a Trakt ID, IMDB ID, or TMDB ID. For TV shows it can also be a TVDB ID.

Prefix with the service name: trakt_id, imdb_id, tmdb_id, tvdb_id

type
Specifies what the ID refers to. Optional but recommended.

Values: movie ,episode ,show ,season

watched_at
optional
Date and time the item was watched. ISO 8601 format.

Can be "unknown" to import with an unknown watch date. Omit if only adding to watchlist.

watchlisted_at
optional
Date and time the item was added to your watchlist. ISO 8601 format.

Omit if only marking as watched.

rating
optional
Rating for the item. Must be a value from 1 to 10.

rated_at
optional
Date and time the item was rated. ISO 8601 format.

Only parsed if a rating is also present.

Приклад
imdb_id,type,watched_at,watchlisted_at,rating,rated_at
tt0068646,movie,2024-10-25T20:00:00Z,2024-10-01T10:00:00Z,7,2024-10-25T21:00:00Z
tt15239678,movie,,2024-04-30T11:00:00Z,,
tt4281724,movie,2024-01-12T02:00:00Z,,,
