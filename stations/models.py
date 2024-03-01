import uuid
from django.db import models
from places.fields import PlacesField

# Create your models here.

class Station(models.Model):
    station_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name =  models.CharField(max_length=25)
    address = PlacesField(blank=True, verbose_name=("station address"))
    station_radius = models.IntegerField(default=1, choices=((i,i) for i in range(1, 20)), verbose_name=("station radius (Km)"))
    
    class Meta:
        db_table = "Stations"
        
    def __str__(self):
        return f"{self.station_id}, {self.name}"