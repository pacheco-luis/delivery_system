from django.contrib import messages
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
import requests
from management.forms import ASSIGN_CLUSTER_FORM, PACKAGE_QUERY_FILTER, SEARCH_PARCEL, SEARCH_USER_FORM, USERS_QUERY_FILTER, EDIT_USER_FORM
from package_request.algorithm.aco3dvrp import VRP, Packer, ACO
from users.models import User, Customer, Driver
from package_request.models import Package, Route
from stations.models import Station
from django.utils import timezone
from stations.forms import STATIONS_FORM
from places.fields import PlacesField 
from django.utils.translation import gettext
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.


# try except helper
def exception_handler( object_queryset ) -> int:
    return  object_queryset.count() if object_queryset is not None  else int(0)

@login_required(login_url='management:admin_login')
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
    
    

@login_required(login_url='management:admin_login')
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
                except Exception as e:
                    messages.error( request, gettext("Route does not exist. It might be deleted already. Please try again.") )
                try:
                    driver = get_object_or_404(Driver, username=form.cleaned_data['driver_username'])
                except Exception as e:
                    messages.error( request, gettext("Driver username does not match any active driver. Please check your input."))
                
                
                if cluster and driver is not None:
                    # if the input given is okay assign each parcel to the driver indicated
                    for parcel in cluster.parcels.all():
                        # parcel.update( status = Package.STATUS_PICKING, driver=driver)
                        Package.objects.filter(package_id = parcel.package_id).update(status = Package.STATUS_PICKING, driver=driver)
                    
                    # to update the route's list we get a new instance of all the active clusters
                    return redirect( 'management:routes' )

            else:
                # if input form is invalid  then show error message
                messages.error( request, gettext("Invalid input format. Please check your data and submit again.") )
                
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
                messages.error( request, gettext("Unable to create new Routes. No available Parcels."))
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
                try:
                    route.station = Package.get_sender_station() if route.parcels[0].status == Package.STATUS_PENDING else Package.get_sender_station()
                except Exception as e:
                    messages.error(request, 'unable to set a station to route')
                    print( 'unable to set a station to route' )

                route.save()
        return redirect('management:routes')
    
    print( 'routes:',routes.count() )
    context = {
        'routes': routes,
        'route_count': routes.count(),
        'assign_form': ASSIGN_CLUSTER_FORM()
    }

    return render(request, 'clusters.html', context)

@login_required(login_url='management:admin_login')
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
                    messages.success(request, gettext('Station has been edited successfully.'))
                except Exception as e:
                    messages.error( request, gettext('Invalid Station ID. Please check your input and try again.') )
            elif 'add_station' in request.POST:
                alias = form.cleaned_data['alias']
                address = PlacesField().to_python(form.cleaned_data['address'])
                active = form.cleaned_data['active']
                radius = form.cleaned_data['radius']
                try:
                    Station.objects.create( alias=alias, address=address, active=active, radius=radius ).save()
                    messages.success(request, gettext('New station has been added successfully.'))
                except Exception as e:
                    messages.error( request, gettext('We encountered an issue while creating the staion. Please try again.') )
            else:
                messages.error( request, gettext('Invalid action. Please Try again.') )
            
            return redirect( 'management:admin_stations' )
        else:
            messages.error( request, gettext('Invalid input. Please check your input and try again.') )
            return redirect( 'management:admin_stations' )
    

    stations = Station.objects.filter(active=True).union(Station.objects.filter(active=False))
    print( 'stations:', stations.count() )
    context={ 
        'stations': stations,
        'stations_count': stations.count(),
        'station_form': STATIONS_FORM(),
    }
    
    return render( request, 'admin_stations.html', context=context)


# function to display all users in management template
@login_required(login_url='management:admin_login')
def admin_all_users(request):
    
    # class to extract and send only required fields from users to users page in management
    class temp_user():
        # initializing the object with an instance of User model
        def __init__(self, user : User) -> None:
            role = ''
            if user.is_customer: role = 'Customer'
            elif user.is_driver: role = 'Driver'
            elif user.is_superuser: role = 'Admin'
            elif user.is_manager: role='Manager'
            elif user.is_staff: role='Staff'
                
            self.username = user.username
            self.role = role
            self.status = 'active' if user.is_active else  'inactive'
            self.date_joined = user.date_joined
    
    # variables and forms that will me filled if necessary depending on the method by user
    all_users = User.objects.all()
    users = list()
    user_filter_form = USERS_QUERY_FILTER()
    edit_user_form = EDIT_USER_FORM()
    
    # detecting if request is get 
    if request.method == 'GET':
        # detecting if request is to get users based on filter form
        if 'get_users' in request.GET:
            form = USERS_QUERY_FILTER( request.GET )
            if form.is_valid() :
                user_type = form.cleaned_data['Users']
                # querying based on the filter value from the form
                if user_type != 'All Users' :
                    q_object = Q(**{user_type:True})
                    all_users = User.objects.filter( q_object  )
            else:
                messages.error( request, gettext('Invalid query. Please try again.') )
        
        # detecting if user is searching by username
        elif 'search_user' in request.GET:
            form = SEARCH_USER_FORM(request.GET)
            if form.is_valid():
                # attempting to obtain user (IF USER EXISTS) and values to render into edit form in template
                try:
                    queried_user = get_object_or_404( User, username=form.cleaned_data['username_search'])
                    queried_user = temp_user(queried_user)
                    edit_user_form.initial['username'] = queried_user.username
                    edit_user_form.initial['role'] = queried_user.role
                    edit_user_form.initial['active'] = queried_user.status
                    edit_user_form.initial['joined'] = queried_user.date_joined.fromisoformat(queried_user.date_joined.__str__()).strftime("%B %d, %Y, %I:%M %p")

                except Exception as e:
                    messages.error( request, gettext('User not found.') )
            else:
                messages.error( request, gettext('Invalid input. Please try again.') )
    
    # detecting if request is to post
    elif request.method == 'POST':
        if 'edit_user' in request.POST:
            edit_form = EDIT_USER_FORM(request.POST)
            if edit_form.is_valid():
                # attempting to search and edit the user by username in post request
                try:
                    updated_user = get_object_or_404( User, username = edit_form.cleaned_data['username'] )
                    updated_user.is_active = True if edit_form.cleaned_data['active'] else False
                    updated_user.save()
                    
                except Exception as e:
                    messages.error( request, gettext('We encountered an issue while editing the user. Please try again.') )
    
    # converting all users into temp_user object to limit the data rendered in template
    for user in all_users:
        users.append( temp_user(user) )

    context = {
        'filter_form': user_filter_form,
        'users': users,
        'edit_user_form': edit_user_form,
        'search_user_form': SEARCH_USER_FORM()
    }
    
    return render( request, 'users.html', context=context )


@login_required(login_url='management:admin_login')
def admin_packages(request):
    class Display_Parcel():
        def __init__(self, parcel: Package) -> None:
            if parcel is not None:
                self.id = parcel.package_id
                self.sender = parcel.customer.user.username
                self.phone = parcel.customer.phone_number
                self.date = parcel.order_date
                self.status = parcel.status
                
    parcels = Package.objects.all()
    parcels_count = 0
    current_packages = 'All packages'
    package_filter_form = PACKAGE_QUERY_FILTER()
    search_parcel_form = SEARCH_PARCEL()

    if request.method == "GET":
        if 'get_packages' in request.GET:
            package_filter_form = form = PACKAGE_QUERY_FILTER(request.GET)
            if form.is_valid():
                status = form.cleaned_data['status']
                if status != 'select a status' :
                    current_packages = status
                    parcels = Package.objects.filter( status=status  )
                
        if 'search_package' in request.GET:
            search_parcel_form = form = SEARCH_PARCEL(request.GET)
            if form.is_valid():
                id = form.cleaned_data['id_search']
                try:
                    searched = get_object_or_404( Package, package_id=uuid.UUID(id))
                except Exception as e:
                    messages.error( request, "No such package exists")

    parcels_count = parcels.count()
    parcels = [Display_Parcel(parcel=parcel) for parcel in parcels]
    
    context = {
        'search_parcel': search_parcel_form,
        'package_filter': package_filter_form,
        'parcels': parcels,
        'current_packages': current_packages,
        'parcels_count': parcels_count
    }
    
    return render( request, 'admin_packages.html', context=context )


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('management:admin_dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email=email, is_superuser=True, is_staff=True)
            user = authenticate(request, email=email, password=password)
        except:
            messages.error(request, gettext('Account not registered as admin.'))
            return redirect('users:admin_login')

        if user is not None:
            login(request, user)
            request.session['sname'] = email
            return redirect('management:admin_dashboard')
        else:
            messages.error(request, gettext('Username and password do not match.'))
            return redirect('users:admin_login')
    
    return render(request, 'admin_login.html', )