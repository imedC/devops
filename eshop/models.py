from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save




class Profile(models.Model):
    # MONSIEUR= 'Monsieur'
    # MADEMOISELLE= 'Mlle'
    # DOCTEUR= 'Dr'
    # Title = (
    #     (MONSIEUR, 'Monsieur'),
    #     (MADEMOISELLE, 'Mademoiselle'),
    #     (DOCTEUR, 'Docteur'),
    # )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(blank=True)
    #cover = models.FileField(blank=True)
    #bio = models.ManyToManyField(max_length=500, blank=True)
    street = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=200, blank=True)
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