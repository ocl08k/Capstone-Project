# Generated by Django 5.1.1 on 2024-10-27 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_userprofile_parentchildrelation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email_report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.PositiveIntegerField()),
            ],
        ),
    ]
