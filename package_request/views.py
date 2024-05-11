from notifications.models import Notification
from vincenty import vincenty
import datetime
import uuid
from django.shortcuts import redirect, render
from package_request.forms import SENDER_FORM, RECEIVER_FORM, PACKAGE_FORM, DRIVER_FILTER_QUERY_FORM
from django.contrib import messages
from stations.models import Station
from users.models import Customer, User, Driver
from package_request.models import Package, Route
from django.contrib.auth.decorators import login_required
from places import Places
from places.forms import PlacesField
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from django.utils.translation import get_language, gettext
from package_request.algorithm.aco3dvrp import VRP, Packer, ACO
from management.forms import ASSIGN_CLUSTER_FORM
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext
from notifications.views import update_context
from django.utils import timezone


# Create your views here.
@login_required
def sucess( request ):
    return render( request, "successful_request.html", context=update_context( request, {}))

def in_range_of_stations( address ):
    ''''
        returns tuple (bool, int)
        true if address is within the radius of station, false otherwise
        if within radius index points to the station index nearest to the address
    '''
    nearest_station = float(10000)
    station_id = uuid.uuid4()
    
    for station in Station.objects.filter( active=True ):
        # print( station.get_coordinates_as_float() )
        dist = vincenty(station.get_coordinates_as_float(), address)
        if dist <= station.radius :
            # return the station for which the sender is within range of
            return (True, station.id )
        elif dist < nearest_station:
            # updating nearest station that does not satisfy station radius
            nearest_station = dist
            station_id = station.id
            
    # returning the closest station near the senders location but within the nears station and sender's location does not satisfy station radius
    return ( False, station_id ) 

@login_required(login_url='users:login')
def sender_form_handler(request):
    import json
    
    if request.method == 'POST':
        form = SENDER_FORM(request.POST)
        
        # if user input is valid validate address within range and save as session for step 3 of 3
        if form.is_valid():
            raw = form.cleaned_data
            
            # validating sender address is within range of a station
            addr1 = raw['sender_address']
            coor = (float(addr1[1]), float(addr1[2]))
            addr_stat = in_range_of_stations( coor )
            
            # if not within range of any station indicate what station is near the inputed address and refill form
            if addr_stat[0] == False:
                try:
                    nearest_staiton=Station.objects.filter(id=addr_stat[1])[0]
                    messages.error(request, f'Your address must be wihin {nearest_staiton.radius}km of station: ' + nearest_staiton.address.place)
                except Exception as e:
                    print(e)
                    messages.error(request, gettext("You must be within our stations' range to send a parcel. Please see our locations page."))
                
                return render(request, "step1.html", context=update_context( request, {'sender_form': SENDER_FORM(request.POST)}) )
                    
            
            # print( form.cleaned_data )
            request.session['sender_data'] = json.dumps(raw, default=str)
            request.session['sender_addr_stat'] = (addr_stat[0], addr_stat[1].hex)
            
            return redirect('package_request_app:request_form_2_of_3')
        
        # if input is invalid refill the form
        else:
            messages.error(request, gettext('Invalid input. Please check your input and try again.'))
            return render(request,"step1.html", context=update_context( request, {'sender_form': SENDER_FORM(request.POST)}) )
    
    # prefilling the customer phone number
    sender_form_inst = { 'sender_phone' : Customer.objects.get(user=request.user).phone_number }
    
    context = {
        'sender_form': SENDER_FORM(sender_form_inst)
    }
    
    return render(request,"step1.html", context=update_context(request, context))

@login_required(login_url='users:login')
def receiver_form_handler(request):
    import json
    
    if request.method == 'POST':
        r_form = RECEIVER_FORM(request.POST)

        # if input is valid save form and move to step 3 of 3
        if r_form.is_valid():
            r_raw = r_form.cleaned_data
            
            # validating sender address is within range of a station
            addr = r_raw['recipient_address']
            r_coor = (float(addr[1]), float(addr[2]))
            r_addr_stat = in_range_of_stations( r_coor )
            temp_stat = request.session['sender_addr_stat']
            temp_stat = (temp_stat[0], uuid.UUID(temp_stat[1]))
            
            # if destination location is out of range of station. sender must fill the form again
            if r_addr_stat[0] == False:
                # showing error indicating the nearest station out of range
                try:
                    nearest_staiton=Station.objects.filter(id=r_addr_stat[1])[0]
                    messages.error(request, f'Sender address must be wihin {nearest_staiton.radius}km of station: ' + nearest_staiton.address.place)
                except Exception as e:
                    messages.error(request, gettext("Sender must be within our stations' range to send a package. Please see our locations page."))
            
                return render(request, "step2.html", context=update_context( request, {'receiver_form': RECEIVER_FORM(request.POST)}) )
            # a parcel destionation location must not be within the sender's station range, sender must fill the form again with a valid location for receiver
            if temp_stat == r_addr_stat:
                messages.error(request, gettext("Sender and receiver address should not be within the same station range.") )
                return render(request,"step2.html", context=update_context( request, {'receiver_form': RECEIVER_FORM(request.POST)}) )
            
            # saving receiver's info as session for step 3
            request.session['receiver_data'] = json.dumps(r_raw, default=str)
            return redirect('package_request_app:request_form_3_of_3')

        else:
            messages.error(request, gettext('Invalid input. Please check your input and try again.'))
            return render(request,"step2.html", context=update_context( request, {'receiver_form': RECEIVER_FORM(request.POST)}) )
    
    context = {
        'receiver_form': RECEIVER_FORM(),
    }
    return render(request,"step2.html", context=update_context( request, context))


@login_required(login_url='users:login')
def package_form_handler(request):
    import json
    dollar_per_kilometer = 10 # NTD
    
    if request.method == 'POST':
        form = PACKAGE_FORM( request.POST )
        
        # create new package if data is valid
        if form.is_valid():
            # obtaining input from step 1,2, and 3 to combine all
            p_data = form.cleaned_data
            s_data = json.loads(request.session['sender_data'])
            r_data = json.loads(request.session['receiver_data'])
            s_addr = s_data['sender_address']
            r_addr = r_data['recipient_address']
            
            
            # combinding data 
            combined_data = { **s_data, **r_data, **p_data }
            
            # creating object with combined data and updating addresses immediatly to avoid serialization error: decimalConversion
            package_obj = Package.objects.create( **combined_data )
            package_obj.sender_address = Places( s_addr[0], Decimal(s_addr[1]), Decimal(s_addr[2]) )
            package_obj.recipient_address = Places( r_addr[0], Decimal(r_addr[1]), Decimal(r_addr[2]) )

            distance = 1
            duration = 1             
            try:
                # obtaining distance matrix using google distance matrix api
                req = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode=transit&key={}'.format(
                   package_obj.sender_address,
                   package_obj.recipient_address,
                   settings.PLACES_MAPS_API_KEY
                ))
                
                res = req.json()
                print('matrix results:', res['rows'])

                # obtaining distance and duration
                distance = res['rows'][0]['elements'][0]['distance']['value'] # meters
                duration = res['rows'][0]['elements'][0]['duration']['value'] # seconds
            except Exception as e:
                print('matrix exception:', e)
                # deleting temporary input used to generate a package before going back to step 1
                try:
                    del request.session['sender_data']
                    del request.session['receiver_data']
                except Exception as e:
                    print('session removal exception 1:', e)
                    pass
                messages.error(request, gettext("Something went wrong. Please try again."))
                messages.error(request, gettext("Unable to determine the distance."))
                # return redirect( 'package_request_app:request_form_1_of_3', context=update_context( request, {}) )
            
            print( 'distance:', distance )
            print( 'duration:', duration )
            
            # updating fields for the  new package created
            package_obj.customer = request.user.customer
            package_obj.distance = round(distance / 1000, 2) # kilometers
            package_obj.duration = int(duration / 60) # minutes
            package_obj.price = package_obj.distance * dollar_per_kilometer # NTD               
            package_obj.status = package_obj.STATUS_PENDING
            package_obj.create_qrcode
            package_obj.save()
            
            # updating customer fields based on the package submited
            Customer.objects.filter(user=request.user).update( phone_number=package_obj.sender_phone, address=package_obj.sender_address )
            
            # deleting temporary input used to generate a package before redirecting
            try:
                del request.session['sender_data']
                del request.session['receiver_data']
            except Exception as e:
                print('session removal exception 2:', e)
                pass
            
            # redirecting to susccessful page
            return redirect( 'package_request_app:successful' )
        
        # rendering page again if input was invalid
        else:
            messages.error(request, gettext('Invalid input. Please check your input and try again.'))
            return render( request, "step3.html", context=update_context( request, {'package_form': PACKAGE_FORM(request.POST)}) )
        
    return render( request, "step3.html", context=update_context( request, {'package_form': PACKAGE_FORM()}) )

@login_required(login_url='users:login')
def all_packages(request):
    import json
    
    package_list = Package.objects.filter(customer=request.user.customer, status__in=[Package.STATUS_PENDING, Package.STATUS_PICKING, Package.STATUS_TRANSIT, Package.STATUS_DELIVERING])
    package_count = Package.objects.filter(customer=request.user.customer).count()
    print( package_count )
    
    for x in package_list:
        print( x.sender_address )
        print( x.recipient_address )
    return render(request, 'package_list.html', context=update_context( request, {'package_list': package_list, 'package_count': package_count}) )


@login_required(login_url='users:login-customer')
def delete_request(request, id):
    try:
        package = Package.objects.get(pk=id)
        package.status = Package.STATUS_CANCELED
        package.save()
        package.delete()
    except Package.DoesNotExist:
        pass
    
    return redirect('package_request_app:package_list')

@login_required(login_url='users:login')
def home( request ):
    
    # if not(request.user.is_driver) or not (request.user.is_customer):
    #     return render(request, 'package_request_app:401')
    
    context = {}
    
    return render( request, "home.html", context=update_context( request, context ))

def landing_page( request ):
    from django.contrib.auth.hashers import make_password

    # if database has no objects create intiial objects for stations, users, customers, and drivers

    if User.objects.all().count() == 0:
        User.objects.create(first_name='admin', last_name='admin', username='admin', email='admin@admin.com', password= make_password('admin'), is_superuser=True, is_staff=True)
        # create users
        domain='@swiftcourier.com'

        for i in range( 0, 3):
            username=f'customer{i}'
            email=f'{username}{domain}'
            new_user = User.objects.create(first_name=username, last_name=username, username=username, email=email, password= make_password('user1234!'), is_customer=True )
            
            username=f'driver{i}'
            email=f'{username}{domain}'
            new_user = User.objects.create(first_name=username, last_name=username, username=username, email=email, password= make_password('user1234!'), is_driver=True )
            
            
        print( 'New users created:')
        for x in User.objects.all():
            print( x )
        
    return render( request, "index.html" )
# HERE BE DRAGONS
@login_required(login_url='users:login')
def all_jobs(request):
    if request.user.is_driver is not True:
        return render(request, '401.html', context=update_context( request, {}) )
    
    filtered_routes = Route.objects.filter(status=Route.STATUS_UNASSIGNED)
    driver = Driver.objects.get(user=request.user)

    if driver.address is not None:
        for station in Station.objects.all():
            if station.dist((float(driver.address.latitude), float(driver.address.longitude))) <= station.radius:
                filtered_routes = Route.objects.filter(parcels__sender_address__icontains=station)
                driver_location = station.alias
    else:
        filtered_routes = Route.objects.all()
    
    if request.method == 'POST':
        form = DRIVER_FILTER_QUERY_FORM(request.POST)
        
        if form.is_valid():
            location = form.cleaned_data['station']
            
            if location != 'None':
                if driver.address is None:
                    try:
                        driver.address = get_object_or_404(Station, alias=location).address
                        driver.save()
                    except:
                        pass
    
                filtered_routes = Route.objects.filter(parcels__sender_address__icontains=location)
                
                if not filtered_routes.exists():
                    messages.error(request, "No routes found based on the selected criteria.")

    
    context = {
        'routes': filtered_routes,
        'query_form': DRIVER_FILTER_QUERY_FORM(),
        'active_tab' : 'routes'
    }
    return render(request, 'job_list.html', context=update_context( request, context))

def select_packages(request):
    if not request.user.is_driver:
        return render(request, '401.html', context=update_context( request, {}) )
    
    driver = Driver.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Get all the package ids that the driver selected
        selected_packages = request.POST.getlist('select_packages')
        print(selected_packages)
        
        # Driver can select their own packages
        if selected_packages:
            
            # Retrieve the selected parcels
            parcels = Package.objects.filter(package_id__in=selected_packages, status=Package.STATUS_PENDING)
            parcels.update(status=Package.STATUS_ASSIGNED, driver=driver)
            print( "parcels selected")
            for x in parcels:
                print( x )
            
            messages.success(request, gettext("Packages successfully selected!"))
            return redirect('package_request_app:select_packages')

    parcels = Package.objects.filter(status=Package.STATUS_PENDING)
    context = {
        'parcels': parcels,
        'active_tab': 'individual'
    }
    return render(request, 'select_packages.html', context=update_context( request, context) )

@login_required(login_url='users:login')
def job_detail(request, id):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}) )
    
    job = Package.objects.get(pk=id)
    google_maps_api_key = settings.PLACES_MAPS_API_KEY

    if not job:
        messages.error(request, gettext('Job is no longer available.'))
        return redirect('package_request_app:job_list')
    
    if request.method == 'POST':
        job.driver = request.user.driver
        job.status = Package.STATUS_PICKING
        job.save()
        messages.success(request, gettext('Job is successfully taken.'))
        return redirect('package_request_app:job_current')

    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'job': job,
    }
    return render(request, 'job_detail.html', context=update_context( request, context) )

@login_required(login_url='users:login')
def current_job(request):
    print( "in current job views!" )
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}) )

    driver = Driver.objects.get(user=request.user)
    driver_packages = Package.objects.filter(driver=driver, status=Package.STATUS_ASSIGNED)
    driver_route = Route.objects.filter(driver=driver, status= Route.STATUS_ASSIGNED)
    parcels = Package.objects.filter(driver=driver, status__in=[Package.STATUS_PICKING, Package.STATUS_TRANSIT, Package.STATUS_DELIVERING])
    
    all_transiting = all(parcel.status == Package.STATUS_TRANSIT for parcel in parcels)
    print(all_transiting)
    if request.method == 'POST':
        
        selected_packages = request.POST.getlist('select_packages')
        packages = driver_packages.filter(package_id__in=selected_packages)
        
        # verify packages in Pakcages to not belong to unassigned routes
        # If in unassigned routes, delete unassigned route
        unassign_routes = Route.objects.filter(status= Route.STATUS_UNASSIGNED)
        to_delete = unassign_routes.filter(parcels__in=packages)
        to_delete.delete()
          
        # Create route
        print('attempting to create routes')
            
        # Coordinates of the depot
        if packages.count():
            depot = packages[0].get_sender_station().get_coordinates_as_float()
            depot = [depot[0], depot[1]]

        # Get all the parcels
        parcels = packages
            
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
        capacity = [99999, 99999, 99999, 99999]

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

        mssg = 'Your parcel will be picked up soon.'
        for route in routes:
            route.station = route.parcels.first().get_sender_station()
            route.status = Route.STATUS_ASSIGNED
            route.driver = driver
            route.save()
            route.parcels.update(status=Package.STATUS_PICKING)
            notifications = [ Notification.objects.create(message=mssg, type=Notification.TYPE_PICKING, parcel=p, user=p.customer.user) for p in route.parcels.all() ]
            [n.notify_picking('assigned', 'picking') for n in notifications]
            
    all_parcels = []
    for route in driver_route:
        parcels_in_route = route.parcels.all()
        all_parcels.extend(parcels_in_route)
        
    parcels_price = sum(parcel.price for parcel in all_parcels)

    num_packages = len(all_parcels)
    context = {
        'active_tab' : 'pickup',
        'driver_packages' : driver_packages,
        'driver_route' : driver_route,
        'all_parcels' : all_parcels,
        'parcels_price': parcels_price,
        'all_transiting': all_transiting,
        'num_packages': num_packages
    }
    return render(request, 'current_job.html', context=update_context( request, context) )

@login_required(login_url='users:login-customer')
def delete_route(request, id):
    try:
        route = Route.objects.get(pk=id)
        parcels_in_route = route.parcels.all()
       
        for parcel in parcels_in_route:
            parcel.status = Package.STATUS_ASSIGNED
            parcel.save()

        route.delete()
    except Route.DoesNotExist:
        pass
    
    return redirect('package_request_app:job_current')

@login_required(login_url='users:login')
def complete_route(request, id):
    
    route = Route.objects.get(pk=id)
    route.status = Route.STATUS_COMPLETED
    route.save()
    messages.success( request, gettext("You have completed the route!"))
    return redirect('package_request_app:job_history')

# @login_required(login_url='users:login')
# def job_deliver(request):
#     if request.user.is_driver is not True :
#         return render(request, '401.html')
    
#     driver = Driver.objects.get(user=request.user)
#     driver_packages = Package.objects.filter(driver=driver, status=Package.STATUS_DELIVERING)

#     if request.method == 'POST':
#         messages.success(request, gettext('Do something here'))

#     context = {
#         'active_tab' : 'deliver',
#         'driver_packages' : driver_packages,
#     }
#     return render(request, 'job_deliver.html', context)

@login_required(login_url='users:login')
def job_deliver(request):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}))
    
    driver = Driver.objects.get(user=request.user)
    driver_packages = Package.objects.filter(driver=driver, status__in=[Package.STATUS_DELIVERING])
    driver_route = Route.objects.filter(driver=driver)
    print(driver_route)
    
    if request.method == 'POST':
        
        selected_packages = request.POST.getlist('select_packages')
        packages = driver_packages.filter(package_id__in=selected_packages)
        
        # verify packages in Packages to not belong to unassigned routes
        # If in unassigned routes, delete unassigned route
        unassign_routes = Route.objects.filter(status= Route.STATUS_UNASSIGNED)
        to_delete = unassign_routes.filter(parcels__in=packages)
        to_delete.delete()
          
        # Create route
        print('attempting to create routes')
            
        # Coordinates of the depot
        if packages.count():
            depot = packages[0].get_sender_station().get_coordinates_as_float()
            depot = [depot[0], depot[1]]

        # Get all the parcels
        parcels = packages
            
        # detecting if no packages avalable to cluster
        if parcels.count() == 0 :
            messages.error( request, gettext("Unable to create new Routes. No available Parcels."))
            return redirect( 'management:routes' )

        # Get the coordinates of the parcels
        # Add the depot as the first coordinate
        coordinates = [
            [float(parcel.recipient_address.latitude),
            float(parcel.recipient_address.longitude)]
            for parcel in parcels
        ]
        coordinates.insert(0, depot)

        # Set the capacity of the couriers
        capacity = [99999, 99999, 99999, 99999]

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

        mssg = 'Your parcel will be picked up soon.'
        for route in routes:
            route.station = route.parcels.first().get_recipient_station()
            route.status = Route.STATUS_TO_DELIVER
            route.driver = driver
            route.save()
            route.parcels.update(status=Package.STATUS_DELIVERING)
            notifications = [ Notification.objects.create(message=mssg, type=Notification.TYPE_PICKING, parcel=p, user=p.customer.user) for p in route.parcels.all() ]
            [n.notify_picking('assigned', 'delivering') for n in notifications]
        
    context = {
        'active_tab' : 'deliver',
        'driver_packages' : driver_packages,
        'driver_route' : driver_route
    }
    return render(request, 'job_deliver.html', context=update_context( request, context) )

@login_required(login_url='users:login')
def completed_job(request):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}))
    
    return render(request, 'completed_job.html', context=update_context( request, {}))

@login_required(login_url='users:login')
def job_history(request):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}))
    driver = Driver.objects.get(user=request.user)
    routes  = Route.objects.filter(driver=driver, status=Route.STATUS_COMPLETED)

    for route in routes:
        driver_packages = route.parcels.all()
    
    parcels_price = sum(parcel.price for parcel in driver_packages)
    print(routes)
    
    all_parcels = []
    for route in routes:
        parcels_in_route = route.parcels.all()
        all_parcels.extend(parcels_in_route)
        
    num_packages = len(all_parcels)
    context = {
       'routes': routes,
       'driver': driver,
       'driver_packages' : driver_packages,
       'num_packages' : num_packages,
       'parcels_price' : parcels_price
    }
    
    return render(request, 'job_history.html', context=update_context( request, context))

@csrf_exempt
@login_required(login_url='users:login')
def api_all_jobs(request):
    jobs = list(Package.objects.filter(status=Package.STATUS_PENDING).values())
    for job in jobs:
        job['sender_latitude'] = float(str(job['sender_address']).split(', ')[-2])
        job['sender_longitude'] = float(str(job['sender_address']).split(', ')[-1])
        job['sender_address'] = ', '.join(str(job['sender_address']).split(', ')[:-2])
        job['recipient_latitude'] = float(str(job['recipient_address']).split(', ')[-2])
        job['recipient_longitude'] = float(str(job['recipient_address']).split(', ')[-1])
        job['recipient_address'] = ', '.join(str(job['recipient_address']).split(',')[:-3])
    return JsonResponse({
        'success': True,
        'jobs': jobs,
    })
    
@login_required(login_url='users:login')
def cluster_route(request, id):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}))
    
    route = Route.objects.get(pk=id)
    google_maps_api_key = settings.PLACES_MAPS_API_KEY
    
    coor = [ p.get_sender_coor() for p in route.parcels.all() ]
    
    print( route.get_formatted_route())
    
    
    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'coor': coor,
        'route': route,
    }
    return render(request, 'cluster_route.html', context=update_context( request, context))

@login_required(login_url='users:login')
def cluster_route_deliver(request):
    if request.user.is_driver is not True :
        return render(request, '401.html')

    driver = request.user.driver
    if Route.objects.filter(driver=driver, status=Route.STATUS_TO_DELIVER).count() == 0:
        messages.error(request, gettext('No route to deliver'))
        return redirect('package_request_app:job_deliver')
    driver_route = Route.objects.filter(driver=driver, status=Route.STATUS_TO_DELIVER).last()
    jobs = driver_route.parcels.filter(status=Package.STATUS_DELIVERING).values()
    google_maps_api_key = settings.PLACES_MAPS_API_KEY
    
    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'driver_route': driver_route,
        'jobs': jobs,
    }
    return render(request, 'cluster_route_deliver.html', context=update_context( request, context))

@login_required(login_url='users:login')
def take_photo(request, id):
    job = Package.objects.filter(
        pk=id,
        driver=request.user.driver,
        status=Package.STATUS_DELIVERING
    ).last()
    if not job:
        messages.error(request, gettext('Job is no longer available'))
        return redirect('package_request_app:cluster_route_deliver')
    context = {
        'job': job,
    }
    return render(request, 'job_deliver_camera.html', context=update_context( request, context))

@csrf_exempt
@login_required(login_url='users:login')
def api_take_photo(request, id):
    driver=request.user.driver
    job = Package.objects.filter(
        pk=id,
        driver=driver,
        status=Package.STATUS_DELIVERING
    ).last()

    jobs = Package.objects.filter(
        driver=driver,
        status=Package.STATUS_DELIVERING
    ).values()
    
    if job.status == Package.STATUS_DELIVERING:
        route = Route.objects.filter(driver=driver, status=Route.STATUS_TO_DELIVER).last()

        # change the status of the job in the route to completed
        job.delivered_photo = request.FILES['delivered_photo']
        job.delivered_at = timezone.now()
        job.status = Package.STATUS_COMPLETED
        job.save()

        # if all jobs in the route are completed, change the status of the route to completed
        # if route.parcels.filter(status=Package.STATUS_DELIVERING).count() == 0:
        #     route.status = Route.STATUS_COMPLETED
        #     route.save()
        #     messages.success(request, gettext('Route completed!'))

        # loop through all the jobs in the route and check if all are completed
        # if all jobs are completed, change the status of the route to completed
        completed = True
        for job in jobs:
            if job['status'] == Package.STATUS_DELIVERING:
                completed = False
                break
        if completed:
            route.status = Route.STATUS_COMPLETED
            route.save()
            messages.success(request, gettext('Route completed!'))

    return JsonResponse({
        'success': True,
    })

@login_required(login_url='users:login')
def package_history(request):
    import json
    # if request.user.is_customer is not True :
    #     return render(request, '401.html', context=update_context( request, {}) )
    if request.user.is_customer:
        customer = request.user.customer
        package_history = Package.objects.filter(customer=customer, status__in=[Package.STATUS_COMPLETED,Package.STATUS_CANCELED])
    elif request.user.is_driver:
        driver = request.user.driver
        package_history = Package.objects.filter(driver=driver, status__in=[Package.STATUS_COMPLETED])
    context = {'package_history': package_history}
    return render(request, 'package_history.html', context=update_context(request, context ))

def unauthorized(request):
    return render(request, '401.html', context=update_context( request, {}))


@login_required(login_url='users:login')
def job_details(request, id):
    if request.user.is_driver is not True :
        return render(request, '401.html', context=update_context( request, {}) )
    
    # job = Package.objects.get(pk=id)
    route = Route.objects.get(pk=id)
    google_maps_api_key = settings.PLACES_MAPS_API_KEY

    # if not job:
    #     messages.error(request, 'Job is no longer available')
    #     return redirect('package_request_app:job_list')
    
    # if request.method == 'POST':
    #     job.driver = request.user.driver
    #     job.status = Package.STATUS_PICKING
    #     job.save()
    #     messages.success(request, 'Job is successfully taken')
    #     return redirect('package_request_app:job_current')

    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        # 'job': job,
        'route': route,
    }
    return render(request, 'job_details.html', context=update_context( request, context) )

# #section that gives the driver the option to choose
# #between delivering or picking up packages
# @login_required(login_url='users:login')
# def job_type_selection(request):
#     print(request.session['job_type'])

#     #check if there is a job type
#     if 'job_type' in request.session:
#         print("I am here")

#     if request.user.is_driver is not True :
#         return render(request, '401.html')
#     return render(request, 'job_type_selection.html')        
@login_required(login_url='users:login')
def job_scanner_pickup(request):
    user = request.user
    driver = user.driver
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        package = Package.objects.get(package_id=package_id)
        print('DATA:', package_id)
        print('DATA:', package.status)
        if package.status == Package.STATUS_PICKING:
            package.status = Package.STATUS_TRANSIT
            package.driver = driver
            package.save()
            return redirect('package_request_app:success_or_fail')
        else:
            messages.error(request, 'This package has already been taken')
    return render(request, 'job_scanner_pickup.html', context=update_context( request, {}) )

@login_required(login_url='users:login')
def job_scanner(request):
    user = request.user
    driver = user.driver
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        package = Package.objects.get(package_id=package_id)
        print('DATA:', package_id)
        if package.status == Package.STATUS_TRANSIT:
            package.status = Package.STATUS_DELIVERING
            package.driver = driver
            package.save()
            return redirect('package_request_app:success_or_fail')
        else:
            messages.error(request, 'This package has already been taken')
    return render(request, 'job_scanner.html', context=update_context( request, {}) )

@login_required(login_url='users:login')
def success_or_fail(request):
    return render(request, 'success_or_fail.html',context=update_context( request, {}) )