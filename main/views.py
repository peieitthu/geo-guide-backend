from rest_framework.decorators import api_view
import requests
from django.conf import settings
from rest_framework.response import Response
from django.http import JsonResponse

def get_google_map_api_key():
    return settings.__getattr__('GOOGLE_MAP_API_KEY')

def get_weather_api_key():
    return settings.__getattr__('WEATHER_API_KEY')

@api_view(['GET'])
def nearby_location_list(request):
    if request.method == 'GET':
        lat = request.query_params['lat']
        log = request.query_params['log'] 
        distance = int(request.query_params['distance'])
        type = request.query_params.get('type', '')
        nextPageToken = request.query_params.get('nextpage_token', '')
              
        params = {
            "location": f"{lat},{log}",
            "type": type,
            "pagetoken": nextPageToken,
            "key": get_google_map_api_key(),
        }
        
        if(distance >= 10000):
            params["radius"] = distance

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            places = data["results"]
            lastPage = False 
            
            if "next_page_token" in data:
                nextPageToken = data["next_page_token"]
            else:
                nextPageToken = ''
                lastPage = True
            
            viewmodel_list = []
            for place in places:                
                
                nearby_location = {
                    'place_id': place.get('place_id', ''),
                    'name': place.get('name', ''),
                    'icon': place.get('icon', ''),
                    'vicinity': place.get('vicinity', ''),
                    'business_status': place.get('business_status', ''),
                    'rating': place.get('rating', 0),
                    'types': place.get('types', ['']),
                    'open_now': place.get('opening_hours', {}).get('open_now', False),
                }
                
                viewmodel_list.append(nearby_location)

            return Response(data = {"nextpage_token": nextPageToken, "last_page": lastPage, "locations": viewmodel_list})
        else:
            raise Exception(f"Error fetching places: {response.status_code}")


@api_view(['GET'])
def location_detail_view(request):
        place_id = request.query_params["placeId"]
        mapApiKey = get_google_map_api_key()
        url = f'https://maps.googleapis.com/maps/api/place/details/json?key={mapApiKey}&place_id={place_id}'
        
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') == 'OK':
            result = data['result']

            # Extract the desired information from the API response
            shop_info = {
                'place_id': result.get('place_id', ''),
                'name': result.get('name', ''),
                'logo_or_image': result.get('icon', ''),
                'lat_lng': result.get('geometry', {}).get('location', {}),
                'phoneNo': result.get('formatted_phone_number', ''),
                'address': result.get('formatted_address', ''),
                'rating': result.get('rating', ''),
                'open_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'open_now':result.get('opening_hours', {}).get('open_now', False),
                'top_reviews': result.get('reviews', [])[:5],
                'types': result.get('types', [])
            }

            return JsonResponse(shop_info)
        else:
            return JsonResponse({'error': 'Could not retrieve shop details'})

@api_view(['Get'])
def weather_status(request):
    weather_api_key = get_weather_api_key();
    
    url = f'https://dataservice.accuweather.com/currentconditions/v1/246562';
    params = {'apikey': weather_api_key}
    
    try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            result = response.json()
            weather_data = result[0]
            
            weather_info = {
                'weatherText': weather_data.get('WeatherText', ''),
                'precipitationType': weather_data.get('PrecipitationType', ''),
                'weatherIcon': weather_data.get('WeatherIcon', ''),
                'isDayTime': weather_data.get('IsDayTime', False),
                'temperature_metric': weather_data.get('Temperature', []).get('Metric', [])
            }
            
            return JsonResponse(weather_info)
    except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to fetch weather data'}, status=500)

    