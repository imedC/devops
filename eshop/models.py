from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save




class Profile(models.Model):
    TN = '221'
    FR ='75'
    US ='233'
    pays = (
        (TN, 'Tunisie'),
        (FR, 'France'),
        (US, 'USA'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(blank=True)
    street = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, choices=pays,default=FR,blank=True)
    mobile = models.IntegerField(blank=True,null=True)
    #bd = models.FileField(blank=True, null=True)
    job = models.CharField(max_length=200,blank=True)

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs['username'])
        return self.model.objects(user=user.id)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

post_save.connect(create_user_profile, sender=User)