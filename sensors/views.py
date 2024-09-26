from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData
from .serializers import SensorDataSerializer
from django.utils import timezone
from datetime import timedelta
import json
import requests

ESP32_URL = 'http://172.20.10.14:80/relay'

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
                esp32_url = 'http://172.20.10.14:80/relay/on'
            elif command == 'off':
                esp32_url = 'http://172.20.10.14:80/relay/off'
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
