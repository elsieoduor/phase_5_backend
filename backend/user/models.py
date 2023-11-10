from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
# Create your models here.


class UserProfileManager(BaseUserManager):
    def create_user(self, username, password, role, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, role, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, role, **extra_fields)
    
#User model defined with roles
class User(AbstractUser):
  USER = 'User'
  CHIEF = 'Chief'
  roleType = (
        (USER, 'User'),
        (CHIEF, 'Chief'),
    )
    
  name= models.CharField(max_length=20, blank=True)
  email = models.EmailField(unique=True)
  password= models.CharField(max_length=20, blank=True)
  username= None
  role = models.CharField(max_length=40, choices=roleType, blank=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []
  objects = UserProfileManager()
  groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
  user_permissions = models.ManyToManyField(
        Permission, related_name='custom_user_set', blank=True
    )

#Homes models defined
class ChildrenOrphanage(models.Model):
    name = models.CharField(max_length=100)
    mission = models.TextField()
    vision = models.TextField()
    values = models.TextField()
    needs = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='orphanage_imgs/',blank= True)
    visit = models.PositiveIntegerField(default=0, blank=True)

    needs_clothes = models.IntegerField(default=0, blank=True)
    needs_hygiene_supplies = models.IntegerField(default=0, blank=True)
    needs_food = models.IntegerField(default=0, blank=True)
    needs_money = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return f"{self.name}  is located at {self.location}"

#Donations model defined
class Donation(models.Model):
    ITEM_CHOICES = [
        ('clothes', 'Clothes'),
        ('hygiene', 'Hygiene Supplies'),
        ('food', 'Food'),
        ('money', 'Money'),
        
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    children_orphanage = models.ForeignKey(ChildrenOrphanage, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    donated_item = models.CharField(max_length=20, choices=ITEM_CHOICES, blank=True)

    def __str__(self):
        return f"{self.user}  has donated {self.amount}"

#Visit model defined
class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    children_orphanage = models.ForeignKey(ChildrenOrphanage, on_delete=models.CASCADE, related_name='home_visits')
    visit_date = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} has scheduled a visit for {self.visit_date}"

#Review model defined
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    children_orphanage = models.ForeignKey(ChildrenOrphanage, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField()
    date_reviewed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reviewed {self.children_orphanage.name} with a rating of {self.rating}"


