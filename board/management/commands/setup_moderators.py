from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Create the Moderators group with view and change post permissions."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions = [
            Permission.objects.get(
                content_type__app_label="board",
                content_type__model="post",
                codename=codename,
            )
            for codename in ("view_post", "change_post")
        ]

        group, created = Group.objects.get_or_create(name="Moderators")
        group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Moderators group configured with view/change post permissions."
            )
        )
