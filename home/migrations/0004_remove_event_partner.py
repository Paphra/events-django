# Generated by Django 2.2.12 on 2020-04-30 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20200430_0901'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='partner',
        ),
    ]
