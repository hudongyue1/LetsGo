# Generated by Django 3.0.7 on 2020-07-09 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0018_goods_frozen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.CharField(default=0, max_length=10),
        ),
    ]
