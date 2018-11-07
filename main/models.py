from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

from main import upload_filenames, validators


class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, english_full_name, phone, institute):
        try:
            validate_password(password)
        except ValidationError:
            raise ValidationError('گذرواژه انتخاب شده به اندازه کافی امن نیست.')
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            institute=institute,
            english_full_name=english_full_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, first_name, last_name, english_full_name, phone, institute):
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            institute=institute,
            english_full_name=english_full_name,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    english_full_name = models.CharField(max_length=32)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=16, validators=[validators.phone_number_validator])
    institute = models.CharField(max_length=64)
    team = models.ForeignKey('Team', on_delete=models.DO_NOTHING, related_name='members', blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'social_id', 'institute']

    def __str__(self):
        return self.get_full_name()

    def get_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'english_full_name': self.english_full_name,
            'institute': self.institute,
            'phone': self.phone,
            'sent_invitations': [invitation.get_dict() for invitation in self.sent_invitations.all()],
            'received_invitations': [invitation.get_dict() for invitation in self.received_invitations.all()],
        }


class Team(models.Model):
    name = models.CharField(max_length=16, unique=True, validators=[validators.team_name_validator])
    logo = models.ImageField(upload_to=upload_filenames.team_logo, default='default_team_logo.png')

    def get_member1(self):
        return self.members.all()[0] if self.members.count() > 0 else None

    def get_member2(self):
        return self.members.all()[1] if self.members.count() > 1 else None

    def get_member3(self):
        return self.members.all()[2] if self.members.count() > 2 else None

    def __str__(self):
        return self.name

    def get_dict(self):
        return {
            'name': self.name,
            'logo': self.logo.url,
            'members': [member.email for member in self.members.all()[:3]]
        }


class TeamInvitation(models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    STATUS_OPTIONS = (PENDING, ACCEPTED, REJECTED)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=8, choices=((s, s) for s in STATUS_OPTIONS), default=PENDING)

    def __str__(self):
        return '{} for {}'.format(self.receiver, self.team)

    def get_dict(self):
        return {
            'id': self.pk,
            'sender': self.sender,
            'receiver': self.receiver,
            'team': self.team,
            'status': self.status,
        }


class Settings(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    value = models.TextField(max_length=8192)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'