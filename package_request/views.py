from django.shortcuts import redirect, render
from package_request.forms import SENDER_FORM, RECEIVER_FORM, PACKAGE_FORM
from django.contrib import messages
from users.models import Customer
from package_request.models import Package
from django.contrib.auth.decorators import login_required
from places import Places
from decimal import Decimal



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

@login_required
def sender_form_handler(request):
    import json

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
                return render(request,"step1.html", {'sender_form': SENDER_FORM(request.POST)} )
            
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

@login_required
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


@login_required
def package_form_handler(request):
    import json
    
    if request.method == 'POST':
        form = PACKAGE_FORM( request.POST )
        if form.is_valid():
            
            p_data = form.cleaned_data
            s_data = json.loads(request.session['sender_data'])
            r_data = json.loads(request.session['receiver_data'])
            s_addr = s_data['sender_address']
            r_addr = r_data['recipient_address']
            
            combined_data = { **s_data, **r_data, **p_data }
            package_obj = Package.objects.create( **combined_data )
            package_obj.sender_id = request.user.customer
            package_obj.sender_address = Places( s_addr[0], Decimal(s_addr[1]), Decimal(s_addr[2]) )
            package_obj.recipient_address = Places( r_addr[0], Decimal(r_addr[1]), Decimal(r_addr[2]) )
            
            Customer.objects.filter(user=request.user).update(
                phone_number=package_obj.sender_phone, 
                address=package_obj.sender_address
                )
            print( package_obj.sender_address )
            print( package_obj.recipient_address )
            
            package_obj.save()
            
            del request.session['sender_data']
            del request.session['receiver_data']
            
            return redirect( 'package_request_app:successful')
        
        else:
            return render( request, "step3.html", {'package_form': PACKAGE_FORM(request.POST)})
        
    return render( request, "step3.html", {'package_form': PACKAGE_FORM()})

@login_required
def all_packages(request):
    import json
    
    package_list = Package.objects.filter( sender_id=request.user.customer )
        
    return render(request, 'package_list.html', {'package_list' : package_list})

def delete_request(request, id):
    delete_obj = Package.objects.get( pk=id )
    delete_obj.delete()
   
    return redirect ('package_request_app:package_list')


def home( request ):
    return render( request, "home.html" )