from django.db import models
import uuid

# Create your models here.

class QA(models.Model):
    question = models.TextField(max_length=255)
    answer = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "QAs"
        
    def __str__(self) -> str:
        return f'{self.id}\n{self.id,}'
    