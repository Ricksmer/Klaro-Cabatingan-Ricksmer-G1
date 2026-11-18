from django.db import migrations

POSITIONS = [('President', 1), ('Vice President', 2), ('Senator', 3)]


def add_positions(apps, schema_editor):
    Position = apps.get_model('politicians', 'Position')
    for name, rank in POSITIONS:
        Position.objects.get_or_create(name=name, defaults={'rank': rank})


def remove_positions(apps, schema_editor):
    Position = apps.get_model('politicians', 'Position')
    Position.objects.filter(name__in=[n for n, _ in POSITIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_positions, remove_positions),
    ]