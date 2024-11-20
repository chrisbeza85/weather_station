import random
import qrcode
import barcode
from io import BytesIO
from django.db import models
from django.core.files import File
from barcode.writer import ImageWriter
from django.utils import timezone

class SensorData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Temperature: {self.temperature}, Humidity: {self.humidity} at {self.timestamp}"

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    barcode = models.CharField(max_length=10, unique=True, blank=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = str(random.randint(100000000000, 999999999999))

        # Generate QR code based on the barcode
        qr = qrcode.make(self.barcode)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        self.qr_code.save(f'qr_{self.barcode}.png', File(qr_io), save=False)

        # Generate Barcode image
        ean = barcode.get('ean13', self.barcode, writer=ImageWriter())
        barcode_io = BytesIO()
        ean.write(barcode_io)
        self.barcode_image.save(f'barcode_{self.barcode}.png', File(barcode_io), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    student_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.student_number)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        self.qr_code.save(f'{self.student_number}_qr.png', File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.student_number})'


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=[('In', 'Check-in'), ('Out', 'Check-out')])

    def __str__(self):
        return f"{self.student.name} - {self.status} at {self.timestamp}"
    

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_time_attended = models.DateTimeField()
    date_time_clocked_out = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Attendance record for {self.student} on {self.date_time_attended}'