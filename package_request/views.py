import datetime
import uuid
from django.shortcuts import redirect, render
from package_request.forms import SENDER_FORM, RECEIVER_FORM, PACKAGE_FORM
from django.contrib import messages
from users.models import Customer, User, Driver
from package_request.models import Package, Route
from django.contrib.auth.decorators import login_required
from places import Places
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from django.utils.translation import get_language, gettext
from package_request.algorithm.aco3dvrp import VRP, Packer, ACO
from management.forms import ASSIGN_CLUSTER_FORM
from django.shortcuts import get_object_or_404



# !!!!!!!!!!!! GLOBAL VARIABLES !!!!!!!!!!!!!!!!

# stations addresses
stations_addr = [
                "No. 8號, Zhengzhou Rd, Zhongzheng District, Taipei City, 100",             # Taipei main train station
                "No. 100, Guolian 1st Rd, Hualien City, Hualien County, 970",               # Hualien main train station
                ]

# stations coordinates 
stations_coo = [
                (25.049033812357674, 121.51378218301954),
                (23.993489655177992, 121.60129912114395) 
                ]

# radius away from stations in km
radius = 10        

# !!!!!!!!!!!! END OF GLOBAL VARIABLES !!!!!!!!!!!!!!!!


# Create your views here.
@login_required
def sucess( request ):
    return render( request, "successful_request.html")


# returns tuple (bool, int)
# true if address is within the radius, false otherwise
# if within radius index points to the station index nearest to the address
def in_range_of_stations( address ):
    nearest_station = 0.0
    index = 0
    
    for x in stations_coo:
        dist = haversine(x, address)
        if dist <= 10.0 :
            return (True, index )
        elif dist < nearest_station:
            nearest_station = dist
        index += 1
            
    return ( False, index-1 )


def haversine(coord1: object, coord2: object):
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    import math
    print( 'haversine' )
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371000  # radius of earth (m)
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    km = meters / 1000.0  # output distance in kilometers

    km = round(km, 3)
    
    # print(f"Distance: {km} km")

    return km

@login_required(login_url='users:login')
def sender_form_handler(request):
    import json

    #print("Current language:", get_language())
    #print("Translation of 'senderphone':", gettext("senderphone"))

    if request.method == 'POST':
        form = SENDER_FORM(request.POST)

        if form.is_valid():
            raw = form.cleaned_data
            addr1 = raw['sender_address']
            coor = (0.0, 0.0)
            
            try:
                coor = (float(addr1[1]), float(addr1[2]))
            except IndexError:
                pass
            
            addr_stat = in_range_of_stations( coor )
            print("validation return:", addr_stat)
            
            if addr_stat[0] == False:
                messages.error(request, "Your address must be wihin 10 km of station: " + stations_addr[1] )
                return render(request, "step1.html", {'sender_form': SENDER_FORM(request.POST)} )
            
            # print( form.cleaned_data )
            request.session['sender_data'] = json.dumps(raw, default=str)
            request.session['sender_addr_stat'] = addr_stat
            
            return redirect('package_request_app:request_form_2_of_3')
        
        else:
            return render(request,"step1.html", {'sender_form': SENDER_FORM(request.POST)} )
    
    print( Customer.objects.get(user=request.user).address )
    print(  )
    sender_form_inst = {
                    'sender_phone' : Customer.objects.get(user=request.user).phone_number,
                    'sender_address' : Places( Customer.objects.get(user=request.user).address, 0, 0 )
                    }
    
    context = {
        'sender_form': SENDER_FORM(sender_form_inst),
    }
    
    return render(request,"step1.html", context=context)

@login_required(login_url='users:login')
def receiver_form_handler(request):
    import json
    
    if request.method == 'POST':
        r_form = RECEIVER_FORM(request.POST)

        if r_form.is_valid():
            r_raw = r_form.cleaned_data
            addr = r_raw['recipient_address']
            r_coor = (0.0, 0.0)
            
            try:
                r_coor = (float(addr[1]), float(addr[2]))
            except IndexError:
                pass

            r_addr_stat = in_range_of_stations( r_coor )
            temp_stat = request.session['sender_addr_stat']
            temp_stat2 = json.loads( json.dumps(r_addr_stat) )
            
            if r_addr_stat[0] == False:
                messages.error(request, "The receipient's address must be wihin 10 km of the station: " + stations_addr[1] )
                return render(request,"step2.html", {'receiver_form': RECEIVER_FORM(request.POST)} )
            
            elif temp_stat == temp_stat2:
                messages.error(request, "Sender address and receiver address are in range of the same station: " + stations_addr[1] )
                return render(request,"step2.html", {'receiver_form': RECEIVER_FORM(request.POST)} )
            
            request.session['receiver_data'] = json.dumps(r_raw, default=str)
            #del request.session['sender_addr_stat']
            
            return redirect('package_request_app:request_form_3_of_3')

        else:
            return render(request,"step2.html", {'receiver_form': RECEIVER_FORM(request.POST)} )
    
    context = {
        'receiver_form': RECEIVER_FORM(),
    }
    return render(request,"step2.html", context=context)


@login_required(login_url='users:login')
def package_form_handler(request):
    import json
    dollar_per_kilometer = 10 # NTD
    
    if request.method == 'POST':
        form = PACKAGE_FORM( request.POST )
        if form.is_valid():
            
            try:
                p_data = form.cleaned_data
                s_data = json.loads(request.session['sender_data'])
                r_data = json.loads(request.session['receiver_data'])
                s_addr = s_data['sender_address']
                r_addr = r_data['recipient_address']
                
                combined_data = { **s_data, **r_data, **p_data }
                package_obj = Package.objects.create( **combined_data )
                package_obj.customer = request.user.customer
                package_obj.sender_address = Places( s_addr[0], Decimal(s_addr[1]), Decimal(s_addr[2]) )
                package_obj.recipient_address = Places( r_addr[0], Decimal(r_addr[1]), Decimal(r_addr[2]) )
                
                Customer.objects.filter(user=request.user).update(
                    phone_number=package_obj.sender_phone, 
                    address=package_obj.sender_address
                    )
                print( package_obj.sender_address )
                print( package_obj.recipient_address )

                # check if the location is inside the radius
                req = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode=transit&key={}'.format(
                   package_obj.sender_address,
                   package_obj.recipient_address,
                   settings.PLACES_MAPS_API_KEY
                ))
                res = req.json()
                print(res['rows'])

                # distance = res['rows'][0]['elements'][0]['distance']['value'] # meters
                # duration = res['rows'][0]['elements'][0]['duration']['value'] # seconds
                distance = 1
                duration = 1              
                
                package_obj.distance = round(distance / 1000, 2) # kilometers
                package_obj.duration = int(duration / 60) # minutes
                package_obj.price = package_obj.distance * dollar_per_kilometer # NTD                
                package_obj.status = package_obj.STATUS_PENDING

                package_obj.save()
                
                del request.session['sender_data']
                del request.session['receiver_data']
                
                return redirect( 'package_request_app:successful')
            except Exception as e:
                print(e)
                messages.error(request, "Something went wrong, please try again")
                return redirect( 'package_request_app:request_form_1_of_3')
        
        else:
            return render( request, "step3.html", {'package_form': PACKAGE_FORM(request.POST)})
        
    return render( request, "step3.html", {'package_form': PACKAGE_FORM()})

@login_required(login_url='users:login')
def all_packages(request):
    import json
    
    package_list = Package.objects.filter(customer=request.user.customer, status__in=[Package.STATUS_PENDING, Package.STATUS_PICKING, Package.STATUS_DELIVERING])
    package_request_count = Package.objects.filter(customer=request.user.customer).count()
    return render(request, 'package_list.html', {'package_list': package_list, 'package_request_count': package_request_count})


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
    return render( request, "home.html" )

def landing_page( request ):
    return render( request, "../templates/index.html" )

# HERE BE DRAGONS
@login_required(login_url='users:login')
def all_jobs(request):
    
    if request.user.is_driver is not True :
        return render(request, '401.html')
    
    
    # print( Route.objects.all().count() )
    # if Route.objects.all().count() == 0:
    #     for i in range(0, 10):
    #         Route().save()
        
    routes = Route.objects.all()
    
    # google_maps_api_key = settings.PLACES_MAPS_API_KEY
    context = {
        # 'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'routes': routes,
    }
    return render(request, 'job_list.html', context)
    

@login_required(login_url='users:login')
def job_detail(request, id):
    if request.user.is_driver is not True :
        return render(request, '401.html')
    
    job = Package.objects.get(pk=id)
    google_maps_api_key = settings.PLACES_MAPS_API_KEY

    if not job:
        messages.error(request, 'Job is no longer available')
        return redirect('package_request_app:job_list')
    
    if request.method == 'POST':
        job.driver = request.user.driver
        job.status = Package.STATUS_PICKING
        job.save()
        messages.success(request, 'Job is successfully taken')
        return redirect('package_request_app:job_current')

    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'job': job,
    }
    return render(request, 'job_detail.html', context)

@login_required(login_url='users:login')
def current_job(request):
    
    if request.user.is_driver is not True :
        return render(request, '401.html')
    
    google_maps_api_key = settings.PLACES_MAPS_API_KEY
    driver = request.user.driver
    job = Package.objects.filter(
        driver=driver,
        status__in=[
            Package.STATUS_PICKING,
            Package.STATUS_DELIVERING,
        ]
    ).last()
    archived = Package.objects.filter(
        driver=driver,
        status__in=[
            Package.STATUS_COMPLETED,
        ]
    )

    if request.method == 'POST':
        if job.status == Package.STATUS_PICKING:
            job.status = Package.STATUS_DELIVERING
            job.save()
            messages.success(request, 'Job is successfully started')
            return redirect('package_request_app:job_current')
        elif job.status == Package.STATUS_DELIVERING:
            job.status = Package.STATUS_COMPLETED
            job.save()
            messages.success(request, 'Job is successfully completed')
        return redirect('package_request_app:job_completed')
    
    context = {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,
        'job': job,
        'archived': archived,
    }
    return render(request, 'current_job.html', context)

@login_required(login_url='users:login')
def completed_job(request):
    if request.user.is_driver is not True :
        return render(request, '401.html')
    
    return render(request, 'completed_job.html')

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
def cluster_route(request):
    if request.user.is_driver is not True :
        return render(request, '401.html')
    ### after integrating the algorithm get a route and render
    return render(request, 'cluster_route.html')

@login_required(login_url='users:login')
def package_history(request):
    import json
    if request.user.is_customer is not True :
        return render(request, '401.html')
    customer = request.user.customer
    package_history = Package.objects.filter(customer=customer, status__in=[Package.STATUS_COMPLETED,Package.STATUS_CANCELED])
    return render(request, 'package_history.html', {'package_history': package_history})

def unauthorized(request):
    return render(request, '401.html')

# @login_required(login_url='users:login')
def create_routes(request):
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
                    messages.error( request, "Route does not exist. It might be deleted already. Please try again." )
                try:
                    driver = get_object_or_404(Driver, username=form['driver_username'])
                except Exception as e:
                    messages.error( request, "Driver username does not match any active driver. Please check your input.")
                
                
                if cluster or driver is not None:
                    # if the input given is okay assign each parcel to the driver indicated
                    for parcel in cluster.parcels.all():
                        parcel.update( status = Package.STATUS_PICKING, driver=driver)
            else:
                # if input form is invalid  then show error message
                messages.error( request, "Invalid input format. Please check your data and submit again." )
                
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

            # Get the coordinates of the parcels
            # Add the depot as the first coordinate
            coordinates = [
                [float(str(parcel.sender_address).split(', ')[-2]),
                float(str(parcel.sender_address).split(', ')[-1])]
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
        return redirect('package_request_app:route_list')
    
    try:
        route_count = routes.count()
    except Exception as e:
        route_count = 0

    context = {
        'routes': routes,
        'route_count': route_count,
        'assign_form': ASSIGN_CLUSTER_FORM()
    }

    return render(request, 'clusters.html', context)

@login_required(login_url='users:login')
def job_details(request, id):
    if request.user.is_driver is not True :
        return render(request, '401.html')
    
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
    return render(request, 'job_details.html', context)