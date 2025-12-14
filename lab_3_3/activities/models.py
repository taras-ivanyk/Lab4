from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import F


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GENDER_CHOICES
    )

    weight_kg = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.0)]
    )
    height_cm = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.0)]
    )
    age = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(0)]
    )

    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(weight_kg__gte=0),
                name='profile_weight_kg_positive'
            ),
            models.CheckConstraint(
                check=models.Q(height_cm__gte=0),
                name='profile_height_cm_positive'
            ),
            models.CheckConstraint(
                check=models.Q(age__gte=0),
                name='profile_age_positive'
            ),
            models.CheckConstraint(
                check=models.Q(gender__in=['male', 'female', 'other']) | models.Q(gender__isnull=True),
                name='profile_gender_valid_choice'
            ),
        ]

    def __str__(self):
        return self.user.username


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('walking', 'Walking'),
        ('swimming', 'Swimming'),
        ('hiking', 'Hiking'),
        ('yoga', 'Yoga'),
        ('gym', 'Gym Workout'),
        ('crossfit', 'CrossFit'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPES,
        default='other'
    )

    duration_sec = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    distance_m = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    elevation_gain_m = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    height = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)


    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time < self.start_time:
                raise ValidationError(
                    "Дата фінішу (end_time) не може бути раніше дати старту (start_time)."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(duration_sec__gte=0),
                name='activity_duration_sec_positive'
            ),
            models.CheckConstraint(
                check=models.Q(distance_m__gte=0),
                name='activity_distance_m_positive'
            ),
            models.CheckConstraint(
                check=models.Q(elevation_gain_m__gte=0),
                name='activity_elevation_gain_m_positive'
            ),
            models.CheckConstraint(
                check=models.Q(end_time__gte=F('start_time')),
                name='activity_end_time_gte_start_time'
            ),
            # Додано обмеження для activity_type на рівні БД
            models.CheckConstraint(
                check=models.Q(activity_type__in=[
                    'running', 'cycling', 'walking', 'swimming',
                    'hiking', 'yoga', 'gym', 'crossfit', 'other'
                ]),
                name='activity_type_valid_choice'
            ),
        ]

    def __str__(self):
        return f"{self.activity_type.title()} by {self.user.username} on {self.start_time.date() if self.start_time else 'N/A'}"


class ActivityPoint(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="points")

    lat = models.FloatField()
    lon = models.FloatField()
    recorded_at = models.DateTimeField(null=True, blank=True)

    ele = models.FloatField(null=True, blank=True)
    speed = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)]
    )
    cadence = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(speed__gte=0),
                name='activitypoint_speed_positive'
            ),
            models.CheckConstraint(
                check=models.Q(cadence__gte=0),
                name='activitypoint_cadence_positive'
            ),
        ]

    def __str__(self):
        return f"Point at ({self.lat}, {self.lon})"


class Comment(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()

    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Activity {self.activity.id}"


class Kudos(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="kudos")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kudos_given")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('activity', 'user')

    def __str__(self):
        return f"Kudos from {self.user.username} to Activity {self.activity.id}"


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}"


class UserMonthlyStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_stats")
    year = models.IntegerField()
    month = models.IntegerField()

    total_distance_m = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)]
    )
    total_duration_sec = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ('user', 'year', 'month')
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_distance_m__gte=0),
                name='stats_distance_m_positive'
            ),
            models.CheckConstraint(
                check=models.Q(total_duration_sec__gte=0),
                name='stats_duration_sec_positive'
            ),
        ]

    def __str__(self):
        return f"Stats for {self.user.username} - {self.year}/{self.month}"