from django.shortcuts import redirect, render
from package_request.forms import SENDER_FORM, RECEIVER_FORM, PACKAGE_FORM
from django.contrib import messages
from users.models import Customer
from package_request.models import Package
from django.contrib.auth.decorators import login_required
from places import Places
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from django.utils.translation import get_language, gettext


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
            del request.session['sender_addr_stat']
            
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
    
    package_list = Package.objects.filter( customer=request.user.customer )
    package_request_count = Package.objects.filter(customer=request.user.customer).count()
    return render(request, 'package_list.html', {'package_list': package_list, 'package_request_count': package_request_count})


@login_required(login_url='users:login-customer')
def delete_request(request, id):
    delete_obj = Package.objects.get( pk=id )
    delete_obj.delete()
   
    return redirect ('package_request_app:package_list')

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
    
    google_maps_api_key = settings.PLACES_MAPS_API_KEY
    context = {
    'GOOGLE_MAPS_API_KEY': google_maps_api_key,
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
    if request.user.is_customer is not True :
        return render(request, '401.html')
    customer = request.user.customer
    package_history = Package.objects.filter(customer=customer, status=Package.STATUS_COMPLETED)
    return render(request, 'package_history.html', {'package_history': package_history})

def unauthorized(request):
    return render(request, '401.html')