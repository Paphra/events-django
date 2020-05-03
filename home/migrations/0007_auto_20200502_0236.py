# Generated by Django 2.2.12 on 2020-05-01 23:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_auto_20200501_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='clearance',
            field=models.IntegerField(choices=[(0, 'Uncleared'), (1, 'Cleared')], default=0),
        ),
        migrations.AddField(
            model_name='booking',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='discount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.IntegerField(choices=[(0, 'Unpaid'), (1, 'Paid')], default=0),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_track_id',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='booking',
            name='seats',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='booking',
            name='ticket_no',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='booking',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]