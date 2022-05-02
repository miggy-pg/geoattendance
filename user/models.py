from random import choices
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from captiveportal import settings


class Attendance(models.Model):
    User = settings.AUTH_USER_MODEL

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="connected")
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Attendance"


class UserManager(BaseUserManager):
    def create_user(self, user_idnumber, password=None):
        if not user_idnumber:
            raise ValueError("Error message: Please enter your ID Number")
        if not password:
            raise ValueError("Error message: Password field is empty")

        user = self.model(
            user_idnumber = user_idnumber,    
        )
        user.set_password(password) #change user password
        user.save(using = self._db)
        return user

    def create_staffuser(self, user_idnumber, password):
        user = self.create_user(
            user_idnumber = user_idnumber,
            password = password,   
        )
        user.staff= True
        user.save(using = self._db)
        return user

    def create_superuser(self, user_idnumber, password):
        user = self.create_user(
            user_idnumber = user_idnumber,
            password = password,   
        )
        user.admin = True
        user.staff = True
        user.save(using = self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_idnumber = models.CharField(
        unique=True, 
        max_length=15, 
        verbose_name='ID Number', 
        error_messages={'unique': ("ID Number already exists.")}
        )
    email = models.EmailField(
        max_length=65, 
        verbose_name= 'Email', 
        error_messages={'unique': ("Email already exists.")}
        )
    user_fname = models.CharField(
        max_length= 40, 
        blank=False, 
        null=False, 
        verbose_name='First Name'
        )
    user_lname = models.CharField(
        max_length= 40, 
        blank=False, 
        null=False, 
        verbose_name='Last Name'
        )
    GENDER_CHOICES =(
        ("Male", "Male"), 
        ("Female", "Female"), 
    )
    user_gender = models.CharField(
        max_length=30, 
        choices=GENDER_CHOICES, 
        verbose_name="Gender"
        )
    college = models.CharField(
        max_length=50,
        default="College of Computer Studies", 
        blank=False, 
        null=False
        )
    COURSE_CHOICES =(
        ("BSIT", "BS in Information Technology"), 
        ("BSIS", "BS in Information System"),
        ("BSCA", "BS in Computer Application"), 
        ("BSCS", "BS in Computer Science"), 
    )
    course = models.CharField(
        max_length=50, 
        choices=COURSE_CHOICES, 
        blank=False
    )
    FIRST_YEAR = 1
    SECOND_YEAR = 2
    THIRD_YEAR = 3
    FOURTH_YEAR = 4
    OTHERS = 5

    YEAR_CHOICES =(
        (FIRST_YEAR, '1'),
        (SECOND_YEAR, '2'),
        (THIRD_YEAR, '3'),
        (FOURTH_YEAR, '4'),
        (OTHERS, 'Others'),
    )
    yearlevel = models.IntegerField(
        choices=YEAR_CHOICES, 
        verbose_name="Year Level",
        null=True
    )
    active = models.BooleanField(default=True) #can login
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False) #superuser
    session_date = models.DateTimeField(auto_now=True)
    date_joined = models.DateField(auto_now_add=True)
    timein = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        null=True,
        verbose_name="Time in"
    )
    timeout = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        null=True,
        verbose_name="Time out"
    )
    timein_status = models.CharField(
        max_length=50,
        null=True
    )
    timeout_status = models.CharField(
        max_length=50,
        null=True
    )
    status = models.CharField(
        max_length=50,
        null=True
    )
    present = models.BooleanField(default=False)
    ip = models.CharField(
        max_length=50,
        null=True
    )
    USERNAME_FIELD = 'user_idnumber' #username
    REQUIRED_FIELDS = [] 

    objects = UserManager()

    def __str__(self):
        return self.user_fname

    def get_full_name(self):
        if self.user_fname:
            return self.user_fname + ' ' + self.user_lname
        return self.email

    def get_short_name(self):
        return self.user_fname

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    
    def has_perm(self, perm, obj=None):
        return True
 
    def has_module_perms(self, app_label):
        return True

    @property
    def is_active(self):
        return self.active








    
    




