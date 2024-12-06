import uuid
from django.db import migrations, models
from django.urls import reverse

from funkwhale_api.federation import utils
import django.db.models.deletion


def get_user_actor(apps, schema_editor):
    MyModel = apps.get_model("history", "Listening")
    for row in MyModel.objects.all():
        actor = row.user.actor
        row.actor = actor
        row.save(update_fields=["actor"])


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model("history", "Listening")
    for row in MyModel.objects.all():
        unique_uuid = uuid.uuid4()
        while MyModel.objects.filter(uuid=unique_uuid).exists():
            unique_uuid = uuid.uuid4()

        fid = utils.full_url(
            reverse("federation:music:listenings-detail", kwargs={"uuid": unique_uuid})
        )
        row.uuid = unique_uuid
        row.fid = fid
        row.save(update_fields=["uuid", "fid"])


def get_user_actor(apps, schema_editor):
    MyModel = apps.get_model("history", "Listening")
    for row in MyModel.objects.all():
        actor = row.user.actor
        row.actor = actor
        row.save(update_fields=["actor"])


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0003_listening_source"),
        ("federation", "0028_auto_20221027_1141"),
    ]

    operations = [
        migrations.AddField(
            model_name="listening",
            name="actor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="listenings",
                to="federation.actor",
            ),
        ),
        migrations.AddField(
            model_name="listening",
            name="fid",
            field=models.URLField(
                max_length=500,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="listening",
            name="url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="listening",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="listening",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="listening",
            name="fid",
            field=models.URLField(
                unique=True,
                db_index=True,
                max_length=500,
            ),
        ),
        migrations.RunPython(get_user_actor, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="listening",
            name="user",
        ),
        migrations.AlterField(
            model_name="listening",
            name="actor",
            field=models.ForeignKey(
                blank=False,
                null=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="listenings",
                to="federation.actor",
            ),
        ),
    ]
