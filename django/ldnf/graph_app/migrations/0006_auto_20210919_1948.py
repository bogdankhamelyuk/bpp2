# Generated by Django 3.2.7 on 2021-09-19 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_app', '0005_alter_pressure_pressure'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Time',
        ),
        migrations.AddField(
            model_name='pressure',
            name='timestamp',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='pressure',
            name='pressure',
            field=models.FloatField(default=0.0),
        ),
    ]