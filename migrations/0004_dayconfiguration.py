# Generated by Django 4.0.6 on 2023-03-26 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mikvah', '0003_appointment_textable'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('opening', models.TimeField()),
            ],
        ),
    ]
