# Generated by Django 3.0.7 on 2020-07-07 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0007_auto_20200707_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goods',
            name='goodSta',
        ),
    ]
