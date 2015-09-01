from django.db import models, migrations
from django.contrib.auth.models import User
from shuffle.models import License


class Migration(migrations.Migration):
    def insert_default_licenses(apps, schema_editor):
        """ Inserts the default licenses. """
        License.objects.bulk_create([License(type=t[0]) for t in License.LICENSE_TYPE])

    def insert_initial_users(apps, schema_editor):
        """ Inserts initial users. """
        amelie_test_user = User(username='amelie@testing', first_name='Amelie', last_name='Müller',
                                email='amelie.testing@outofbits.com')
        amelie_test_user.set_password('the_cake_is_a_lie')
        amelie_test_user.save()

    dependencies = [
        ('shuffle', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_default_licenses),
        migrations.RunPython(insert_initial_users),
    ]
