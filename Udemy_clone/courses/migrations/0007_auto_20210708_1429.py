# Generated by Django 3.1.5 on 2021-07-08 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20210703_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='length',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
    ]
