from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("music", "0060_migrate_libraries_to_playlist"),
    ]
    operations = [
        migrations.RemoveField(
            model_name="library",
            name="description",
        ),
        migrations.RemoveField(
            model_name="library",
            name="followers_url",
        ),
    ]
