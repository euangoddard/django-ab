from django.db.models.base import Model
from django.db.models.fields import CharField
from django.db.models.fields import IntegerField


class ABTest(Model):
    
    name = CharField(unique=True, max_length=50)
    
    times_a_presented = IntegerField(default=0)
    
    times_b_presented = IntegerField(default=0)
    
    times_a_chosen = IntegerField(default=0)
    
    times_b_chosen = IntegerField(default=0)
    
    class Meta(object):
        verbose_name = "AB Test"
        verbose_name_plural = "AB Tests"
        ordering = ("name", )
    
    def __unicode__(self):
        return self.name