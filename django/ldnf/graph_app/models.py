from django.db import models 
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    pressure = models.CharField(max_length=4) 
    timestamp = models.DateTimeField(auto_now_add=True)

    #def __unicode__(self):
    #    return "{0} {1}".format(self.pressure, self.timestamp)

    def __str__(self):
        return str(self.pressure)