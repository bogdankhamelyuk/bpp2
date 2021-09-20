# Generated by Django 3.2.7 on 2021-09-18 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_app', '0002_message_number_of_measure'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pressure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pressure', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
