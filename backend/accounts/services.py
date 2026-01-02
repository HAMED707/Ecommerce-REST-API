from .models import Users
from django.contrib.auth import authenticate

def create_user_account(username, email, first_name=None, last_name=None, password=None,
                        phone_number=None, gender=None, date_of_birth=None, profile_picture=None):
    # create user instance
    user = Users(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        gender=gender,
        date_of_birth=date_of_birth,
        profile_picture=profile_picture,
    )

    if password:
        user.set_password(password)  # hash the password

    user.save()
    return user

def authenticated(username, password):
    # returns user obj or None
    user = authenticate(username=username, password=password)
    return user

