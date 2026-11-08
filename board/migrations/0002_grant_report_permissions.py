
from django.db import migrations


def setup_moderator_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    db = schema_editor.connection.alias

    group, _ = Group.objects.using(db).get_or_create(
        name="Moderators"
    )

    for model_name in ("post", "postreport"):
        content_type, _ = ContentType.objects.using(db).get_or_create(
            app_label="board",
            model=model_name,
        )

        for action in ("view", "change"):
            permission, _ = Permission.objects.using(db).get_or_create(
                content_type=content_type,
                codename=f"{action}_{model_name}",
                defaults={
                    "name": f"Can {action} {model_name}"
                },
            )

            group.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(
            setup_moderator_permissions,
            migrations.RunPython.noop,
        ),
    ]
