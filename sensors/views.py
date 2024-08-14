from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData
from .serializers import SensorDataSerializer

@api_view(['GET'])
def test_view(request):
    if request.method == 'GET':
        return Response({"message": "GET request successful"})

@api_view(['POST', 'GET'])
def record_data(request):
    if request.method == 'POST':
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
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
    
def display_data(request):
    data = SensorData.objects.all().order_by('-timestamp')
    return render(request, 'sensors/display_data.html', {'data': data})

#@csrf_exempt
#@require_http_methods(["GET", "POST"])
#def temperature_data(request):
 #   if request.method == 'GET':
  #      # Fetch the latest 10 sensor data entries
   #     data = SensorData.objects.all().order_by('-timestamp')[:10]
    #    response_data = [
     #       {
      #          "temperature": entry.temperature,
       #         "humidity": entry.humidity,
        #        "timestamp": entry.timestamp,
         #   }
         #   for entry in data
        #]
        #return JsonResponse({"data": response_data})

    #elif request.method == 'POST':
     #   try:
      #      # Parse JSON data
       #     data = json.loads(request.body)
        #    temperature = data.get('temperature')
         #   humidity = data.get('humidity')

          #  if temperature is not None and humidity is not None:
           #     SensorData.objects.create(temperature=temperature, humidity=humidity)
            #    return JsonResponse({'status': 'success'}, status=201)
            #else:
             #   return JsonResponse({'error': 'Invalid data'}, status=400)
        #except json.JSONDecodeError:
         #   return JsonResponse({'error': 'Invalid JSON'}, status=400)

# views.py



def temperature_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.order_by('-timestamp').first()
        if latest_data:
            data = {
                'temperature': latest_data.temperature,
                'humidity': latest_data.humidity
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'No data available'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def display_environment(request):
    return render(request, 'environment.html')


from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from datetime import datetime, timedelta

def get_sensor_data(request):
    if request.method == 'GET':
        # Get the last 10 sensor data entries
        data_entries = SensorData.objects.order_by('-timestamp')[:10]
        
        # Prepare data
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

        return JsonResponse(data)
    
def fetch_sensor_data(request):
    if request.method == 'GET':
        data = list(SensorData.objects.order_by('-timestamp').values('timestamp', 'temperature', 'humidity'))
        return JsonResponse({'data': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)