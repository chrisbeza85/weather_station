from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData, Item, Student, Attendance, AttendanceRecord
from .forms import ItemForm, StudentForm
from .serializers import SensorDataSerializer
from django.utils import timezone
from datetime import timedelta
import json
import requests

ESP32_URL = 'http://172.16.60.91/relay'

def dashboard(request):
    return render(request, 'dashboard.html')


# A simple test view to check if the API is responding to GET requests
@api_view(['GET'])
def test_view(request):
    if request.method == 'GET':
        return Response({"message": "GET request successful"})

# A view to handle POST and GET requests for recording sensor data
@csrf_exempt
@api_view(['POST', 'GET'])
def record_data(request):
    if request.method == 'POST':
        # Deserialize the incoming data and validate it
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save valid data to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        # Fetch the latest 10 entries sorted by timestamp in descending order
        data = SensorData.objects.all().order_by('-timestamp')[:10]
        response_data = [
            {
                "temperature": entry.temperature,
                "humidity": entry.humidity,
                "timestamp": entry.timestamp,
            }
            for entry in data
        ]
        return Response({"data": response_data})

# A view to display sensor data on a web page
def display_data(request):
    data = SensorData.objects.all().order_by('-timestamp')  # Get all data sorted by timestamp
    return render(request, 'sensors/display_data.html', {'data': data})  # Render the data in a template

# A view to fetch the latest temperature and humidity data as JSON
def temperature_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.order_by('-timestamp').first()  # Get the latest data entry
        if latest_data:
            data = {
                'temperature': latest_data.temperature,
                'humidity': latest_data.humidity
            }
            return JsonResponse(data)  # Return the latest data as JSON
        return JsonResponse({'error': 'No data available'}, status=404)  # Return error if no data found
    return JsonResponse({'error': 'Method not allowed'}, status=405)  # Return error if method is not GET

# A view to render an environment display page
def display_environment(request):
    return render(request, 'environment.html')  # Render the environment template

# A view to get the last 10 sensor data entries and return them as JSON
@csrf_exempt
def get_sensor_data(request):
    if request.method == 'GET':
        data_entries = SensorData.objects.order_by('-timestamp')[:10]  # Fetch the latest 10 entries
        # Format the data into JSON
        data = {
            'data': [
                {
                    'timestamp': entry.timestamp.isoformat(),
                    'temperature': entry.temperature,
                    'humidity': entry.humidity,
                }
                for entry in data_entries
            ]
        }
        return JsonResponse(data)  # Return formatted data as JSON

# A view to fetch sensor data and return it as JSON
@csrf_exempt    
def fetch_sensor_data(request):
    if request.method == 'GET':
        # Fetch data entries as a list of dictionaries
        data = list(SensorData.objects.order_by('-timestamp').values('timestamp', 'temperature', 'humidity'))
        return JsonResponse({'data': data})  # Return the data as JSON
    return JsonResponse({'error': 'Method not allowed'}, status=405)  # Return error if method is not GET

# A view to get the latest data entry using Django REST framework
@csrf_exempt
@api_view(['GET'])
def latest_data(request):
    latest_entry = SensorData.objects.latest('timestamp')  # Fetch the most recent data entry
    serializer = SensorDataSerializer(latest_entry)  # Serialize the latest entry
    return Response(serializer.data)  # Return the serialized data as a response

# A view to fetch historical data based on the specified period
@csrf_exempt
@api_view(['GET'])
def history_data(request):
    period = request.query_params.get('period', 'last_3_minutes')  # Get the period parameter from the query
    if period == 'last_3_minutes':
        # Calculate the time threshold for the last 3 minutes
        time_threshold = timezone.now() - timedelta(minutes=3)
        # Filter data entries from the last 3 minutes
        data = SensorData.objects.filter(timestamp__gte=time_threshold).order_by('timestamp')
    else:
        # Fetch all data entries if no specific period is given
        data = SensorData.objects.all().order_by('timestamp')
    serializer = SensorDataSerializer(data, many=True)  # Serialize the data entries
    return Response(serializer.data)  # Return the serialized data

@csrf_exempt
def relay_control(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('state')

            if command == 'on':
                esp32_url = 'http://172.16.61.32:8077/relay/on'
            elif command == 'off':
                esp32_url = 'http://172.16.61.32:8077/relay/off'
            else:
                return JsonResponse({'error': 'Invalid command'}, status=400)

            response = requests.get(esp32_url)
            if response.status_code == 200:
                relay_state = command
            else:
                return JsonResponse({'error': 'Failed to communicate with ESP32'}, status=500)

            return JsonResponse({'state': relay_state}, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'OPTIONS':
        # CORS preflight handling
        response = JsonResponse({'status': 'preflight'})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    return JsonResponse({'error': 'Invalid method'}, status=405)

# View to list all items
def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

# View to add a new item
def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_form.html', {'form': form})

# View to edit an item
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form})

# View to delete an item
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)  # Get the item by primary key or show 404 if not found
    return render(request, 'inventory/item_detail.html', {'item': item})


def mark_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rfid_uid = data.get('rfid_uid')

        # Check if the student with this RFID UID exists
        try:
            student = Student.objects.get(rfid_uid=rfid_uid)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        # Mark attendance (either check-in or check-out)
        last_attendance = Attendance.objects.filter(student=student).last()
        if last_attendance and last_attendance.status == 'In':
            # If last status was "In", mark "Out"
            Attendance.objects.create(student=student, status='Out')
            return JsonResponse({'message': 'Check-out successful'})
        else:
            # Otherwise, mark "In"
            Attendance.objects.create(student=student, status='In')
            return JsonResponse({'message': 'Check-in successful'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-timestamp')
    return render(request, 'attendance/attendance_list.html', {'attendances': attendances})

def qr_scan(request):
    return render(request, 'inventory/qr_scan.html')

def qr_scan2(request):
    return render(request, 'students/qr_scan2.html')

def scan_item(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        try:
            # Try to find the item by its barcode
            item = Item.objects.get(barcode=barcode)
            # If found, redirect to the item details page
            return redirect('item_detail', pk=item.pk)
        except Item.DoesNotExist:
            # If the item is not found, render the item_not_found template
            return render(request, 'inventory/item_not_found.html')
    return render(request, 'inventory/scan_item.html')


def scan_qr_code(request):
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code')  # Get the scanned QR code from the request
        try:
            # Try to find the item by its QR code
            item = Item.objects.get(barcode=qr_code_data)
            # If found, redirect to the item details page
            return redirect('item_detail', pk=item.pk)
        except Item.DoesNotExist:
            # If the item is not found, render the item_not_found template
            return render(request, 'inventory/item_not_found.html')
    return render(request, 'inventory/qr_scan.html')

def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendance_history = AttendanceRecord.objects.filter(student=student).order_by('-date_time_attended')

    context = {
        'student': student,
        'attendance_history': attendance_history,
    }
    return render(request, 'students/student_detail.html', {'student': student})

# View to edit a student record
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})

# View to delete record
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})

# For adding or editing a student
def student_add_edit(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {'form': form, 'student': student})

def scan_student(request):
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code')  # Get the scanned QR code from the request
        try:
            # Try to find the item by its QR code
            student = Student.objects.get(student_number=qr_code_data)
            # If found, redirect to the item details page
            return redirect('student_detail', pk=student.pk)
        except Student.DoesNotExist:
            # If the item is not found, render the item_not_found template
            return render(request, 'students/item_not_found.html')
    return render(request, 'students/qr_scan2.html')

def scan_qr_codes(request):
    if request.method == "POST":
        qr_code_data = request.POST.get('qr_code')  # Get the scanned QR code from the request

        try:
            # Find the student by their student_number (QR code data)
            student = Student.objects.get(student_number=qr_code_data)
        except Student.DoesNotExist:
            # If student is not found, return JSON response with not_found status
            return JsonResponse({'status': 'not_found', 'url': '/item_not_found/'})

        # Get the latest attendance record for this student
        latest_record = AttendanceRecord.objects.filter(student=student).order_by('-date_time_attended').first()

        if latest_record and latest_record.date_time_clocked_out is None:
            # If the student is clocked in but not clocked out, clock them out
            latest_record.date_time_clocked_out = timezone.now()
            latest_record.save()
        else:
            # If no active clock-in, create a new attendance record to clock them in
            AttendanceRecord.objects.create(student=student, date_time_attended=timezone.now())

        # Return JSON response with success status and URL to redirect to student detail
        return JsonResponse({'status': 'success', 'url': f'/sensors/students/{student.pk}/'})

    # If it's not a POST request, redirect to the QR scan page
    return redirect('students:student_list')

def student_detail(request, pk):
    # Get the student by their primary key (pk)
    student = get_object_or_404(Student, pk=pk)
    
    # Fetch the attendance records for this student, ordered by latest clock-in time
    attendance_history = AttendanceRecord.objects.filter(student=student).order_by('-date_time_attended')

    # Pass the student and their attendance history to the template
    context = {
        'student': student,
        'attendance_history': attendance_history,
    }

    return render(request, 'students/student_detail.html', context)