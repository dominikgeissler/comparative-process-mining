# Generated by Django 3.2.9 on 2021-11-10 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='log_file',
            field=models.FileField(upload_to='logs'),
        ),
    ]