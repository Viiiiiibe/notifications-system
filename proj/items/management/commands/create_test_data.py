from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from items.models import Item

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Create test users and items: users alice and bob (password "password") and '
        'a superuser admin (password "password"). Also grants model permissions to alice and bob.'
    )

    def handle(self, *args, **options):
        u1, created = User.objects.get_or_create(username='alice')
        if created:
            u1.set_password('password')
        u1.is_staff = True
        u1.save()

        u2, created = User.objects.get_or_create(username='bob')
        if created:
            u2.set_password('password')
        u2.is_staff = True
        u2.save()

        admin_username = 'admin'
        admin_password = 'password'
        admin, created = User.objects.get_or_create(username=admin_username)
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(admin_password)
        admin.save()

        Item.objects.get_or_create(name='Item A', defaults={'status': 'new', 'owner': u1})
        Item.objects.get_or_create(name='Item B', defaults={'status': 'processing', 'owner': u1})
        Item.objects.get_or_create(name='Item C', defaults={'status': 'done', 'owner': u2})

        ct = ContentType.objects.get_for_model(Item)
        codenames = ['add_item', 'change_item', 'delete_item', 'view_item']
        for codename in codenames:
            try:
                perm = Permission.objects.get(codename=codename, content_type=ct)
            except Permission.DoesNotExist:
                continue
            u1.user_permissions.add(perm)
            u2.user_permissions.add(perm)

        u1.save()
        u2.save()

        self.stdout.write(self.style.SUCCESS(
            'Created/updated users: alice, bob (password="password"); admin (superuser, password="password").\n'
            'Items created and model permissions granted to alice and bob (if permissions exist).'
        ))
