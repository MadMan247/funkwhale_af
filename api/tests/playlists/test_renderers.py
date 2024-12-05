from defusedxml import ElementTree as etree

from funkwhale_api.playlists import renderers, serializers


def test_generate_xspf_from_playlist(factories):
    playlist_track = factories["playlists.PlaylistTrack"]()
    playlist = playlist_track.playlist
    xspf_test = renderers.PlaylistXspfRenderer().render(
        serializers.PlaylistSerializer(playlist).data
    )
    tree = etree.fromstring(xspf_test)
    track1_title = playlist_track.track.title
    ns = {"xspf": "http://xspf.org/ns/0/"}
    assert playlist.name == tree.findtext("./xspf:title", namespaces=ns)
    assert track1_title == tree.findtext(
        "./xspf:trackList/xspf:track/xspf:title", namespaces=ns
    )
