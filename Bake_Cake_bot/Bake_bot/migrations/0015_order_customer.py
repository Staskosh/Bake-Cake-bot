# Generated by Django 3.2.7 on 2021-10-30 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bake_bot', '0014_merge_20211030_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Имя Покупателя'),
        ),
    ]
