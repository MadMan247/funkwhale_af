# Federation settings

If you want federation to work the API need to be opened. By default it is not. Look for `API Requires authentication` in the instance settings.

## Get federation content

You can fetch remote content locally in various ways :

- Using remote object urls and pasting them the search bar.
- Fetching remote actors (paste their url into the search bar, this will fetch their public activities).
- Following whole instances.
- Automatically following instances.

### Instance level following

If you want to get all public activities from an instance you can follow it. You can find a Follow button in the domain detail page. A list of domain can be accessed in admin area, in the moderation menu.

You can also automatically follow all known Funkwhale instances. This feature can be enabled in the admin settings. The pod will automatically follow the domain it finds. Domain discovery task is triggered at the beginning of each month. If you are in a hury you can manually trigger the task using the django shell :

```{warning}
This tasks are heavy. They trigger a lot of networks requests and might block your worker until they complete. They will also make you pod known to a lot of instance, increasing the traffic on your pod.
```

```
docker compose run --rm api python manage.py shell
tasks.discover_domains_from_known_ones.delay()
tasks.discover_domains_from_funkwhale_audio.delay()
tasks.follow_all_domains.delay()
```

### Managing load

When fetching remote data the server will parse various ActivityPub collections. They can be very big. You can increase or decrease the `FEDERATION_COLLECTION_MAX_PAGES` in the admin settings if you wish more of less content to be fetch.

```{note}
This only affect fetching/scanning remote collections for past activities. New Activities should reach you pod anyways so this is useful when you discover a new domain or when you just setup your pod.
```
