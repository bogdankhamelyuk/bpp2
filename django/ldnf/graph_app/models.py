from django.db import models 
from django.contrib.auth import get_user_model

User = get_user_model()

class Pressure(models.Model):
    pressure = models.FloatField(default=.0) 
    timestamp = models.FloatField(default=.0)
    #timestamp = models.DateTimeField(auto_now_add=True)
    #number_of_measure = models.IntegerField(default=0)
    #def __unicode__(self):
    #    return "{0} {1}".format(self.pressure, self.timestamp)
    #def __str__(self):
    #    return str(self.pressure)


######## obsolete: ##########
#class Time(models.Model):
#    timestamp = models.FloatField()
#    def __str__(self):
#        return str(self.timestamp)
#
