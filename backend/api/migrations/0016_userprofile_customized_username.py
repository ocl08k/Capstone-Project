# Generated by Django 5.1.1 on 2024-11-11 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_alter_userprofile_avatar_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='customized_username',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
