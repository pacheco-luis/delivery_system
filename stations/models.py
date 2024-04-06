import uuid
from django.db import models
from places.fields import PlacesField
from django.core.validators import MinValueValidator
from vincenty import vincenty

# Create your models here.

class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, unique=True, editable=False)
    alias =  models.CharField(max_length=25)
    address = PlacesField(blank=False, verbose_name=("station address"))
    radius = models.IntegerField(default=10, choices=((i,i) for i in range(1, 20)), verbose_name=("station radius (Km)"),)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "Stations"
        
    def __str__(self):
        return f"{self.id}, {self.alias}"
    
    def as_json(self):
        return  {
                    'id': str(self.id),
                    'alias': str(self.alias),
                    'address': str( self.address),
                    'radius': str(self.radius)+'km',
                    'active': bool(self.active)
                }
        
    def get_address(self):
        return self.address.place
    
    def get_coordinates(self):
        return f'{self.address.latitude}, {self.address.longitude}'
    
    def get_coordinates_as_float(self):
        return (float(self.address.latitude), float(self.address.longitude))
    
    def dist(self, other_address):
        return vincenty(self.get_coordinates_as_float(), other_address)

