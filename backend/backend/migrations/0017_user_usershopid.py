# Generated by Django 3.0.4 on 2020-04-25 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_auto_20200425_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='UserShopID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='backend.Shop'),
        ),
    ]
