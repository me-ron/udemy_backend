from courses.models import Course
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_superuser(self, email, password, name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_author', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        if not extra_fields.get('is_author'):
            raise ValueError('Superuser must have is_author=True.')

        return self._create_user(email, password, name, **extra_fields)

    def create_author(self, email, password, name, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_author', True)

        if not extra_fields.get('is_author'):
            raise ValueError('Author must have is_author=True.')

        return self._create_user(email, password, name, **extra_fields)

    def _create_user(self, email, password, name, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=225, null=True, blank=True)
    email = models.EmailField(max_length=225, unique=True)  # Include EmailField for email validation
    paid_course = models.ManyToManyField(Course, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    def get_all_courses(self):
        courses = []
        for course in self.paid_course.all():
            courses.append(course.course_uuid)
        return courses