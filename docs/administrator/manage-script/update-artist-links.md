````markdown
# Update artist external links from MusicBrainz

Funkwhale can automatically fetch external links for artists from MusicBrainz. This is useful for populating artist profiles with links to official websites, social media, and other platforms.

## How it works

When you create or sync an artist from MusicBrainz, external links are automatically fetched and stored. If you want to populate links for existing artists, you can use the `update_artist_links` management command to fetch links from MusicBrainz in bulk.

Links are stored as JSON and displayed on artist profiles with automatic icon and color detection based on the platform (Website, Bandcamp, YouTube, SoundCloud, etc.).

## Commands

### Update a single artist by ID

::::{tab-set}

:::{tab-item} Debian
:sync: debian

```bash
venv/bin/funkwhale-manage update_artist_links --artist-id <id>
```

:::

:::{tab-item} Docker
:sync: docker

```bash
docker compose run --rm api funkwhale-manage update_artist_links --artist-id <id>
```

:::
::::

### Update a single artist by name

::::{tab-set}

:::{tab-item} Debian
:sync: debian

```bash
venv/bin/funkwhale-manage update_artist_links --artist-name "Artist Name"
```

:::

:::{tab-item} Docker
:sync: docker

```bash
docker compose run --rm api funkwhale-manage update_artist_links --artist-name "Artist Name"
```

:::
::::

### Update all artists

::::{tab-set}

:::{tab-item} Debian
:sync: debian

```bash
venv/bin/funkwhale-manage update_artist_links --all
```

:::

:::{tab-item} Docker
:sync: docker

```bash
docker compose run --rm api funkwhale-manage update_artist_links --all
```

:::
::::

```{warning}
Running with the `--all` flag will process all artists in your database. This can take a significant amount of time and may hit MusicBrainz API rate limits. Consider running this in smaller batches if you have a large music library.
```

````
