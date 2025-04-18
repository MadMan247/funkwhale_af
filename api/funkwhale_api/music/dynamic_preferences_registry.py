from django.forms import widgets
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

music = types.Section("music")
quality_filters = types.Section("quality_filters")


@global_preferences_registry.register
class MaxTracks(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "transcoding_enabled"
    verbose_name = "Transcoding enabled"
    help_text = (
        "Enable transcoding of audio files in formats requested by the client. "
        "This is especially useful for devices that do not support formats "
        "such as Flac or Ogg, but the transcoding process will increase the "
        "load on the server."
    )
    default = True


@global_preferences_registry.register
class MusicCacheDuration(types.IntPreference):
    show_in_api = True
    section = music
    name = "transcoding_cache_duration"
    default = 60 * 24 * 7
    verbose_name = "Transcoding cache duration"
    help_text = (
        "How many minutes do you want to keep a copy of transcoded tracks "
        "on the server? Transcoded files that were not listened in this interval "
        "will be erased and retranscoded on the next listening."
    )
    field_kwargs = {"required": False}


@global_preferences_registry.register
class MbidTaggedContent(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "only_allow_musicbrainz_tagged_files"
    verbose_name = "Only allow Musicbrainz tagged files"
    help_text = (
        "Requires uploaded files to be tagged with a MusicBrainz ID. "
        "Enabling this setting has no impact on previously uploaded files. "
        "You can use the CLI to clear files that don't contain an MBID or "
        "or enable quality filtering to hide untagged content from API calls. "
    )
    default = False


@global_preferences_registry.register
class MbGenreTags(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "musicbrainz_genre_update"
    verbose_name = "Prepopulate tags with MusicBrainz Genre "
    help_text = (
        "Will trigger a monthly update of the tag table "
        "using Musicbrainz genres. Non-existing tag will be created and "
        "MusicBrainz Ids will be added to the tags if "
        "they match the genre name."
    )
    default = True


@global_preferences_registry.register
class MbSyncTags(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "sync_musicbrainz_tags"
    verbose_name = "Sync MusicBrainz to to funkwhale objects"
    help_text = (
        "If uploaded files are tagged with a MusicBrainz ID, "
        "Funkwhale will query MusicBrainz server to add tags to "
        "the track, artist and album objects."
    )
    default = False


# quality_filters section. Note that the default False is not applied in the fronted
# (the filter will onlyu be use if set to True)
@global_preferences_registry.register
class BitrateFilter(types.ChoicePreference):
    show_in_api = True
    section = quality_filters
    name = "bitrate_filter"
    verbose_name = "Upload Quality Filter"
    default = "low"
    choices = [
        ("low", "Allow all audio qualities"),
        ("medium", "Medium : Do not allow low quality"),
        ("high", "High : only allow high and very-high audio qualities"),
        ("very_high", "Very High : only allow very-high audio quality"),
    ]
    help_text = (
        "The main page content can be filtered based on audio quality. "
        "This will exclude lower quality, higher qualities are never excluded. "
        "Quality Table can be found in the docs."
    )
    field_kwargs = {"choices": choices, "required": False}


@global_preferences_registry.register
class HasMbid(types.BooleanPreference):
    show_in_api = True
    section = quality_filters
    name = "has_mbid"
    verbose_name = "Musicbrainz Ids filter"
    help_text = "Should we filter out metadata without Musicbrainz Ids ?"
    default = False


@global_preferences_registry.register
class Format(types.MultipleChoicePreference):
    show_in_api = True
    section = quality_filters
    name = "format"
    verbose_name = "Allowed Audio Format"
    default = (["aac", "aif", "aiff", "flac", "mp3", "ogg", "opus"],)
    choices = [
        ("ogg", "ogg"),
        ("opus", "opus"),
        ("flac", "flac"),
        ("aif", "aif"),
        ("aiff", "aiff"),
        ("aac", "aac"),
        ("mp3", "mp3"),
    ]
    help_text = "Which audio format to allow"


@global_preferences_registry.register
class AlbumArt(types.BooleanPreference):
    show_in_api = True
    section = quality_filters
    name = "has_cover"
    verbose_name = "Album art Filter"
    help_text = "Only Albums with a cover will be displayed in the home page"
    default = False


@global_preferences_registry.register
class Tags(types.BooleanPreference):
    show_in_api = True
    section = quality_filters
    name = "has_tags"
    verbose_name = "Tags Filter"
    help_text = "Only content with at least one tag will be displayed"
    default = False


@global_preferences_registry.register
class ReleaseDate(types.BooleanPreference):
    show_in_api = True
    section = quality_filters
    name = "has_release_date"
    verbose_name = "Release date Filter"
    help_text = "Only content with a release date will be displayed"
    default = False


@global_preferences_registry.register
class JoinPhrases(types.StringPreference):
    show_in_api = True
    section = music
    name = "join_phrases"
    verbose_name = "Join Phrases"
    help_text = (
        "Used by the artist parser to create multiples artists in case the metadata "
        "is a single string. BE WARNED, changing the order or the values can break the parser in unexpected ways. "
        "It's MANDATORY to escape dots and to put doted variation before because the first match is used "
        r"(example : `|feat\.|ft\.|feat|` and not `feat|feat\.|ft\.|feat`.). ORDER is really important "
        "(says an anarchist). To avoid artist duplication and wrongly parsed artist data "
        "it's recommended to tag files with Musicbrainz Picard. "
    )
    default = (
        r"featuring | feat\. | ft\. | feat | with | and | & | vs\. | \| | \||\| |\|| , | ,|, |,|"
        r" ; | ;|; |;| versus | vs | \( | \(|\( |\(| Remix\) |Remix\) | Remix\)| \) | \)|\) |\)| x |"
        "accompanied by | alongside | together with | collaboration with | featuring special guest |"
        "joined by | joined with | featuring guest | introducing | accompanied by | performed by | performed with |"
        "performed by and | and | featuring | with | presenting | accompanied by | and special guest |"
        "featuring special guests | featuring and | featuring & | and featuring "
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class DefaultJoinPhrases(types.StringPreference):
    show_in_api = True
    section = music
    name = "default_join_phrase"
    verbose_name = "Default Join Phrase"
    help_text = (
        "The default join phrase used by artist parser"
        "For example: `artists = [artist1, Artist2]` will be displayed has : artist1.name, artis2.name"
        "Changing this value will not update already parsed artists"
    )
    default = ", "
    widget = widgets.Textarea
    field_kwargs = {"required": False}
