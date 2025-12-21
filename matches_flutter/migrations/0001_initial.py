import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fields', '0002_facility_remove_field_facilities_alter_field_rating_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time_slot', models.CharField(choices=[('10.00-11.00', '10.00 - 11.00'), ('11.00-12.00', '11.00 - 12.00'), ('12.00-13.00', '12.00 - 13.00'), ('13.00-14.00', '13.00 - 14.00')], max_length=20)),
                ('price', models.IntegerField(default=0)),
                ('current_players', models.IntegerField(default=1)),
                ('max_players', models.IntegerField(default=10)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fields.field')),
            ],
        ),
    ]
