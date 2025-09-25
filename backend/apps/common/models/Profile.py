from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class ProfileModel(models.Model):
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )
    # Add additional profile fields here as needed

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Profile Extra Info"
        verbose_name_plural = "Profile Extra Infos"


@receiver(post_save, sender=User)
def create_or_update_user_profile(
    sender,
    instance,  # The `created` parameter in the
    # `create_or_update_user_profile` function is a
    # boolean value that indicates whether a new
    # instance of the `User` model was created or an
    # existing one was updated when the `post_save`
    # signal is triggered.
    created,
    **kwargs,
):
    if created:
        ProfileModel.objects.create(user=instance)
    else:
        # Save the profile if it exists
        try:
            instance.profile.save()
        except ProfileModel.DoesNotExist:
            ProfileModel.objects.create(user=instance)
