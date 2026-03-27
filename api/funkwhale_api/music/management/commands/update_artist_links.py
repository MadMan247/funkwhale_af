from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.music.models import Artist


class Command(BaseCommand):
    help = "Update external links for artists from MusicBrainz"

    def add_arguments(self, parser):
        parser.add_argument(
            "--artist-id",
            type=int,
            help="Update a specific artist by ID",
        )
        parser.add_argument(
            "--artist-name",
            type=str,
            help="Update a specific artist by name (partial match)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Update all artists with MBIDs",
        )

    def handle(self, *args, **options):
        if options["artist_id"]:
            queryset = Artist.objects.filter(
                id=options["artist_id"], mbid__isnull=False
            )
        elif options["artist_name"]:
            queryset = Artist.objects.filter(
                name__icontains=options["artist_name"], mbid__isnull=False
            )
        elif options["all"]:
            queryset = Artist.objects.filter(mbid__isnull=False)
        else:
            raise CommandError("Please provide --artist-id, --artist-name, or --all")

        total = queryset.count()
        self.stdout.write(f"Found {total} artist(s) to update")

        updated = 0
        errors = 0

        for artist in queryset:
            try:
                raw_data = Artist.api.get(id=artist.mbid, includes=Artist.api_includes)[
                    "artist"
                ]
                cleaned_data = Artist.clean_musicbrainz_data(raw_data)

                for hook in Artist.import_hooks:
                    hook(artist, cleaned_data, raw_data)

                artist.refresh_from_db()
                links_count = artist.links.count()

                self.stdout.write(
                    self.style.SUCCESS(f"✓ {artist.name}: {links_count} link(s) found")
                )
                updated += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ {artist.name}: {str(e)}"))
                errors += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated} | Errors: {errors} | Total: {total}"
            )
        )
