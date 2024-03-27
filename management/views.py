from django.contrib import messages
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
import requests
from management.forms import ASSIGN_CLUSTER_FORM
from package_request.algorithm.aco3dvrp import VRP, Packer, ACO
from users.models import User, Customer, Driver
from package_request.models import Package, Route
from stations.models import Station
from datetime import datetime, timedelta
from delivery_system.settings import TIME_ZONE
from django.utils import timezone
from stations.forms import STATIONS_FORM
from places import Places
from places.fields import PlacesField 
from decimal import Decimal
from django.utils.translation import gettext_lazy as _, gettext


# Create your views here.


# try except helper
def exception_handler( object_queryset ) -> int:
    return  object_queryset.count() if object_queryset is not None  else int(0)

def admin_dashboard(request):
    # for users card
    all_users = exception_handler( User.objects.all() )
    active = exception_handler( User.objects.filter(is_active=True ) )
    inactive = exception_handler( User.objects.filter(is_active=False ) )
    customers = exception_handler( Customer.objects.all() )
    drivers = exception_handler( Driver.objects.all() )
    
    # for packages card
    all_p = exception_handler( Package.objects.all() )
    pending_p = exception_handler( Package.objects.filter( status=Package.STATUS_PENDING) )
    picking_p = exception_handler( Package.objects.filter( status=Package.STATUS_PICKING) )
    delivering_p = exception_handler( Package.objects.filter( status=Package.STATUS_DELIVERING) )
    completed_p = exception_handler( Package.objects.filter( status=Package.STATUS_COMPLETED) )
    cancelled_p = exception_handler( Package.objects.filter( status=Package.STATUS_CANCELED) )
    
    # for cluster card
    all_clusters = exception_handler( Route.objects.all() )
    
    # for stations card
    all_stations = exception_handler( Station.objects.all() )
    
    
    pack = Package.objects.filter( status=Package.STATUS_PENDING )
    
    # print( len(pack) )
    for p in pack:
        print( p.order_date )
    # top 5 drivers by number of delivered packages
    print( timezone.now()-timezone.timedelta(days=30) )
    
    active_drivers = Driver.objects.filter( user__is_driver=True, user__is_active=True )
    drivers_stats = [ ( d.driver_id, d.username, exception_handler(Package.objects.filter( status=Package.STATUS_COMPLETED, order_date__gt= (  timezone.now()-timezone.timedelta(days=30) ), driver=d)) ) for d in active_drivers ]
    drivers_stats.sort( key=lambda drivers_stats: drivers_stats[2], reverse=True )
    drivers_stats = drivers_stats[:5]
    
    context = {
        'total_users': all_users,  
        'active_users': active, 
        'inactive_users': inactive,
        'customers_users': customers,
        'drivers_users': drivers,
        'all_p': all_p,
        'pending_p': pending_p,
        'picking_p': picking_p,
        'delivering_p': delivering_p,
        'completed_p': completed_p,
        'cancelled_p': cancelled_p,
        'all_clusters': all_clusters,
        'all_stations': all_stations,
        'top_5_drivers': drivers_stats,
    }
    
    return render(request, 'admin_dashboard.html', context=context)
    
    

# @login_required(login_url='users:login')
def create_assign_routes(request):
    # if request.user.is_driver is not True :
    #     return render(request, '401.html')
    routes = Route.objects.all()
    if request.method == 'POST':
        # assign route to driver if assign cluster is in request
        if 'assign_cluster' in request.POST:
            print('attempting to assign cluster')
            form = ASSIGN_CLUSTER_FORM(request.POST)
            # validating the form 
            if form.is_valid():
                cluster = driver = None
                try:
                    clstr = uuid.UUID(form.cleaned_data['cluster_id'])
                    cluster = get_object_or_404(Route, id=clstr)
                except  Exception as e:
                    messages.error( request, _("Route does not exist. It might be deleted already. Please try again.") )
                try:
                    driver = get_object_or_404(Driver, username=form.cleaned_data['driver_username'])
                except Exception as e:
                    messages.error( request, _("Driver username does not match any active driver. Please check your input."))
                
                
                if cluster and driver is not None:
                    # if the input given is okay assign each parcel to the driver indicated
                    for parcel in cluster.parcels.all():
                        # parcel.update( status = Package.STATUS_PICKING, driver=driver)
                        Package.objects.filter(package_id = parcel.package_id).update(status = Package.STATUS_PICKING, driver=driver)
                    
                    # to update the route's list we get a new instance of all the active clusters
                    return redirect( 'management:routes' )

            else:
                # if input form is invalid  then show error message
                messages.error( request, _("Invalid input format. Please check your data and submit again.") )
                
        elif 'create_routes' in request.POST:
            print('attempting to create routes')
            # Coordinates of the depot
            depot = [25.048848712153227, 121.51374971086004]

            # Check if there are any existing routes
            # If there are, delete them
            if Route.objects.exists():
                Route.objects.all().delete()

            # Get all the parcels
            parcels = Package.objects.filter(status=Package.STATUS_PENDING)
            
            
            # detecting if no packages avalable to cluster
            if parcels.count() == 0 :
                messages.error( request, _("Unable to create new Routes. No available Parcels."))
                return redirect( 'management:routes' )

            # Get the coordinates of the parcels
            # Add the depot as the first coordinate
            coordinates = [
                [float(parcel.sender_address.latitude),
                float(parcel.sender_address.longitude)]
                for parcel in parcels
            ]
            coordinates.insert(0, depot)

            # Set the capacity of the couriers
            capacity = [17, 14, 17, 100]

            # Set the dimensions and weight of the parcels
            items = [
                [float(parcel.width),
                float(parcel.height),
                float(parcel.depth),
                float(parcel.estimate_package_weight_value)]
                for parcel in parcels
            ]

            # Get the distance and duration matrix
            distance_matrix = []
            # Google Maps API configuration
            API_key=settings.PLACES_MAPS_API_KEY
            base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
            origins = [[f'{coordinates[i][0]},{coordinates[i][1]}'] for i in range(len(coordinates))]
            destinations = origins.copy()

            # Get the distance and duration matrix
            for i in range(0, len(origins), 6):
                chunk_origins = origins[i:i+6]

                for i in range(0, len(destinations), 6):
                    chunk_destinations = destinations[i:i+6]

                    params = {
                        'origins': '|'.join([','.join(origin) for origin in chunk_origins]),
                        'destinations': '|'.join([','.join(destination) for destination in chunk_destinations]),
                        'key': API_key
                    }

                    response = requests.get(url=base_url, params=params)
                    data = response.json()
                    
                    for k, _ in enumerate(chunk_origins):
                        distance_matrix.append([])

                        for l, _ in enumerate(chunk_destinations):
                            status = data['rows'][k]['elements'][l]['status']

                            if status == 'OK':
                                distance = data['rows'][k]['elements'][l]['distance']['value']

                                distance_matrix[-1].append(distance)
                            else:
                                distance_matrix[-1].append(-1)
        
            vrp = VRP(coordinates, distance=None)
            packer = Packer(capacity, items, n_decimals=3)
            aco = ACO(vrp, packer, n_ants=1, max_iter=1,
                    alpha=1.0, beta=3.0, rho=0.1,
                    pheromone=1.0, phe_deposit_weight=1.0)

            best_tour, best_distance = aco.ACS()

            print('Here is the best tour:')
            print(best_tour)
            print(best_distance)

            # Delete all existing routes
            # Route.objects.all().delete()

            # Initialize a list to store created route instances
            routes = list([])

            # Iterate through the best_tour
            for _, location in enumerate(best_tour):
                if location == 0:
                    # Create a new route instance for each depot
                    route = Route.objects.create()
                    routes.append(route)  # Add the route to the list
                else:
                    # Retrieve the parcel associated with the current location
                    parcel = parcels[location - 1]

                    # Associate the parcel with the last created route (assuming the first route is already created)
                    routes[-1].parcels.add(parcel)

            # Save all route instances after adding parcels
            for route in routes:
                route.save()
        return redirect('management:routes')
    
    
    context = {
        'routes': routes,
        'route_count': len(routes),
        'assign_form': ASSIGN_CLUSTER_FORM()
    }

    return render(request, 'clusters.html', context)


def admin_stations(request):
    
    if request.method == "POST":
        form = STATIONS_FORM( request.POST )
        if( form.is_valid() ):
            # data = form.cleaned_data()
            if 'edit_station' in request.POST:
                try:
                    station = get_object_or_404( Station, id=form.cleaned_data['id'])
                    station.alias=form.cleaned_data['alias']
                    station.address=PlacesField().to_python(form.cleaned_data['address'])
                    station.active=form.cleaned_data['active']
                    station.radius=radius = form.cleaned_data['radius']
                    station.save()
                    messages.success(request, _('Station has been edited successfully.'))
                except Exception as e:
                    messages.error( request, _('Invalid Station ID. Please check your input and try again.') )
            elif 'add_station' in request.POST:
                alias = form.cleaned_data['alias']
                address = PlacesField().to_python(form.cleaned_data['address'])
                active = form.cleaned_data['active']
                radius = form.cleaned_data['radius']
                try:
                    Station.objects.create( alias=alias, address=address, active=active, radius=radius ).save()
                    messages.success(request, _('New station has been added successfully.'))
                except Exception as e:
                    messages.error( request, _('We encountered an issue while creating the staion. Please try again.') )
            else:
                messages.error( request, _('Invalid action. Please Try again.') )
            
            return redirect( 'management:admin_stations' )
        else:
            messages.error( request, _('Invalid input. Please check your input and try again.') )
            return redirect( 'management:admin_stations' )
    

    stations = Station.objects.filter(active=True).union(Station.objects.filter(active=False))
    context={ 
        'stations': stations,
        'stations_count': stations.count(),
        'station_form': STATIONS_FORM(),
    }
    
    return render( request, 'admin_stations.html', context=context)