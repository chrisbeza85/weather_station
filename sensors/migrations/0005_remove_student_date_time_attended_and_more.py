# Generated by Django 5.1.1 on 2024-10-14 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0004_student_attendance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='date_time_attended',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_time_clocked_out',
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_attended', models.DateTimeField()),
                ('date_time_clocked_out', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.student')),
            ],
        ),
    ]
