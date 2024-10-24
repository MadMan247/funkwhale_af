"""
Populates the database with fake data
"""
import random

from funkwhale_api.music import factories


def create_data(count=25):
    acs = factories.ArtistCreditFactory.create_batch(size=count)
    for ac in acs:
        print("Creating data for", ac.artist)
        albums = factories.AlbumFactory.create_batch(
            artist_credit=ac, size=random.randint(1, 5)
        )
        for album in albums:
            factories.UploadFactory.create_batch(
                track__album=album,
                size=random.randint(3, 18),
                playable=True,
                in_place=True,
            )


if __name__ == "__main__":
    create_data()
