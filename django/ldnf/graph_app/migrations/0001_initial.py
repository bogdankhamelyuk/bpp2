# Generated by Django 3.2.7 on 2021-09-18 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pressure', models.CharField(max_length=4)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
