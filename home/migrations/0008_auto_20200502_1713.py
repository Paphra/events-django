# Generated by Django 2.2.12 on 2020-05-02 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20200502_0236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'verbose_name': 'Pesapal Payment', 'verbose_name_plural': 'Pesapal Payments'},
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='amount',
            new_name='Amount',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='description',
            new_name='Description',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='email',
            new_name='Email',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='first_name',
            new_name='FirstName',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='last_name',
            new_name='LastName',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='payment_status',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='payment_track_id',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='reference',
        ),
        migrations.AddField(
            model_name='booking',
            name='PhoneNumber',
            field=models.CharField(default='+56701822382', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='Reference',
            field=models.CharField(default='Reference', max_length=50, verbose_name='Pesapal Merchant Reference'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Event'),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('INVALID', 'Invalid')], default='PENDING', max_length=9),
        ),
        migrations.AddField(
            model_name='booking',
            name='tracking_id',
            field=models.CharField(blank=True, max_length=50, verbose_name='Pesapal Transaction Tracking ID'),
        ),
    ]
