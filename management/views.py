from django.shortcuts import render
from users.models import User, Customer, Driver
from package_request.models import Package, Route
from stations.models import Station
from datetime import datetime, timedelta
from delivery_system.settings import TIME_ZONE
from django.utils import timezone

# Create your views here.

def admin_dashboard(request):
    
    # for users card
    all_users = User.objects.all().count()
    active = User.objects.filter(is_active=True ).count()
    inactive = User.objects.filter(is_active=False ).count()
    customers = Customer.objects.all().count()
    drivers = Driver.objects.all().count()
    
    # for packages card
    all_p = Package.objects.all().count()
    pending_p = Package.objects.filter( status=Package.STATUS_PENDING).count()
    picking_p = Package.objects.filter( status=Package.STATUS_PICKING).count()
    delivering_p = Package.objects.filter( status=Package.STATUS_DELIVERING).count()
    completed_p = Package.objects.filter( status=Package.STATUS_COMPLETED).count()
    cancelled_p = Package.objects.filter( status=Package.STATUS_CANCELED).count()
    
    # for cluster card
    all_clusters = Route.objects.all().count()
    
    # for stations card
    all_stations = Station.objects.all().count()
    
    
    pack = Package.objects.filter( status=Package.STATUS_PENDING )
    print( len(pack) )
    for p in pack:
        print( p.order_date )
    # top 5 drivers by number of delivered packages
    print( timezone.now()-timezone.timedelta(days=30) )
    
    active_drivers = Driver.objects.filter( user__is_driver=True, user__is_active=True )
    drivers_stats = [ ( d.driver_id, d.username, Package.objects.filter( status=Package.STATUS_COMPLETED, order_date__gt= (  timezone.now()-timezone.timedelta(days=30) ), driver=d).count()) for d in active_drivers ]
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