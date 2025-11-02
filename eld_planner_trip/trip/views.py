from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# from eld_planner_trip.trip.utils.eld_generator import ELDGenerator
# from eld_planner_trip.trip.utils.route_calculator import RouteCalculator
# from eld_planner_trip.trip.utils.hos_calculator import HOSCalculator



from .utils.route_calculator import RouteCalculator
from .utils.hos_calculator import HOSCalculator
from .utils.eld_generator import ELDGenerator


@api_view(['POST'])
def calculate_trip(request):
    try:
        data = request.data
        current_location = data.get('currentLocation')
        pickup_location = data.get('pickupLocation')
        dropoff_location = data.get('dropoffLocation')
        current_cycle_used = float(data.get('currentCycleUsed', 0))

        # Validate inputs
        if not all([current_location, pickup_location, dropoff_location]):
            return Response(
                {'error': 'All location fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if current_cycle_used < 0 or current_cycle_used > 70:
            return Response(
                {'error': 'Current cycle must be between 0 and 70 hours'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate route
        route_calc = RouteCalculator()
        route_data = route_calc.calculate_route(
            current_location,
            pickup_location,
            dropoff_location
        )

        # Calculate HOS compliance
        hos_calc = HOSCalculator(current_cycle_used)
        hos_data = hos_calc.calculate_compliance(
            route_data['total_distance'],
            route_data['driving_time']
        )

        # Generate response
        response_data = {
            'totalDistance': round(route_data['total_distance'], 1),
            'drivingTime': round(route_data['driving_time'], 1),
            'totalTripTime': round(route_data['total_trip_time'], 1),
            'fuelStops': route_data['fuel_stops'],
            'restBreaks': hos_data['rest_breaks'],
            'hoursAvailable': hos_data['hours_available'],
            'totalHoursUsed': hos_data['total_hours_used'],
            'compliant': hos_data['compliant'],
            'mapUrl': route_data['map_url'],
            'eldLogUrl': f'/api/generate-eld-log/?trip_id={route_data["trip_id"]}',
            'stops': route_data['stops']
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def generate_eld_log(request):
    try:
        trip_id = request.GET.get('trip_id')
        # Generate ELD log PDF
        generator = ELDGenerator()
        pdf_url = generator.generate_log(trip_id)

        return Response({'pdfUrl': pdf_url}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
