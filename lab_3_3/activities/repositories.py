from django.contrib.auth.models import User
from .models import Activity
from django.db.models import Sum, Count, Avg, Max, F

from django.db.models import Case, When, Value, CharField
from django.db.models.functions import TruncMonth


class AnalyticsRepository:

    def get_top_distance_users(self):
        return User.objects.annotate(
            total_distance=Sum('activities__distance_m')
        ).filter(total_distance__gt=0).order_by('-total_distance').values('username', 'total_distance')[:10]

    def get_social_activities(self):
        return Activity.objects.annotate(
            comments_count=Count('comments', distinct=True),
            kudos_count=Count('kudos', distinct=True)
        ).annotate(
            engagement_score=F('comments_count') + F('kudos_count')
        ).filter(engagement_score__gt=0).order_by('-engagement_score').values(
            'user__username', 'comments_count', 'kudos_count', 'engagement_score'
        )

    def get_monthly_activity_stats(self):
        return Activity.objects.annotate(
            month=TruncMonth('start_time')
        ).values('month').annotate(
            total_activities=Count('id'),
            total_distance=Sum('distance_m'),
            avg_duration=Avg('duration_sec')
        ).order_by('month')

    def get_influential_users(self):
        return User.objects.annotate(
            followers_count=Count('followers')
        ).filter(followers_count__gte=2).order_by('-followers_count').values('username', 'followers_count')

    def get_activity_type_performance(self):
        return Activity.objects.values('activity_type').annotate(
            avg_distance=Avg('distance_m'),
            max_elevation=Max('elevation_gain_m'),
            record_count=Count('id')
        ).order_by('-avg_distance')

    def get_user_activity_levels(self):
        return User.objects.annotate(
            activities_count=Count('activities')
        ).annotate(
            status=Case(
                When(activities_count__gte=10, then=Value('Pro Athlete')),
                When(activities_count__gte=3, then=Value('Active')),
                default=Value('Beginner'),
                output_field=CharField(),
            )
        ).values('username', 'activities_count', 'status')
class DataAccessLayer:
    def __init__(self):
        self.analytics = AnalyticsRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass