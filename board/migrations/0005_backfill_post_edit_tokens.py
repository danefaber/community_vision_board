
import uuid

from django.db import migrations


def backfill_edit_tokens(apps, schema_editor):
    Post = apps.get_model("board", "Post")

    for post in Post.objects.filter(edit_token__isnull=True).iterator():
        post.edit_token = uuid.uuid4()
        post.save(update_fields=["edit_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0004_alter_post_edit_token"),
    ]

    operations = [
        migrations.RunPython(
            backfill_edit_tokens,
            migrations.RunPython.noop,
        ),
    ]
