from django.shortcuts import redirect, render
from users.models import User, Customer, Driver
from package_request.models import Package, Route
from stations.models import Station
from datetime import datetime, timedelta
from delivery_system.settings import TIME_ZONE
from django.utils import timezone

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
    
    print( len(pack) )
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

def clusters(request):  
    return render( request, "clusters.html" )


def assign_cluster( request, route_id, driver_username ):
    route=Route.objects.get( id=route_id )
    driver=Driver.objects.get(user__username=driver_username)
    if route and driver is not None:
        for parcel in route.parcels:
            parcel( status=Package.STATUSES.STATUS_PICKING, driver=driver )
    
    # error
    # return to  the previous page (routes or cluster's details)
            
    
    return redirect('package_request_app:route_list')
    