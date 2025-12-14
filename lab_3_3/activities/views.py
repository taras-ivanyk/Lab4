import pandas as pd
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .repositories import DataAccessLayer
from .services import ChartService, BenchmarkService


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DataAccessLayer()

    def _process_pandas_response(self, queryset, fields, stats_columns=None, group_by_col=None):
        if fields:
            data = list(queryset.values(*fields))
        else:
            data = list(queryset)

        df = pd.DataFrame(data)

        if df.empty:
            return Response({"message": "No data available", "statistics": {}})

        stats = {}
        if stats_columns:
            for col in stats_columns:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    stats[col] = {
                        "mean": df[col].mean(),
                        "median": df[col].median(),
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "std_dev": df[col].std()
                    }

        grouped_data = None
        if group_by_col and group_by_col in df.columns and stats_columns:
            grouped_df = df.groupby(group_by_col)[stats_columns].mean()
            grouped_data = grouped_df.to_dict()

        response_data = {
            "dataset": df.to_dict(orient="records"),
            "statistics": stats,
            "grouped_analysis": grouped_data
        }
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        qs = self.db.analytics.get_top_distance_users()
        return self._process_pandas_response(
            qs,
            fields=['username', 'total_distance'],
            stats_columns=['total_distance']
        )

    @action(detail=False, methods=['get'])
    def social_engagement(self, request):
        qs = self.db.analytics.get_social_activities()
        return self._process_pandas_response(
            qs,
            fields=['id', 'user__username', 'comments_count', 'kudos_count', 'engagement_score'],
            stats_columns=['engagement_score', 'comments_count', 'kudos_count']
        )

    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        qs = self.db.analytics.get_monthly_activity_stats()
        return self._process_pandas_response(
            qs,
            fields=None,
            stats_columns=['total_distance', 'avg_duration']
        )

    @action(detail=False, methods=['get'])
    def influencers(self, request):
        qs = self.db.analytics.get_influential_users()
        return self._process_pandas_response(
            qs,
            fields=['username', 'followers_count'],
            stats_columns=['followers_count']
        )

    @action(detail=False, methods=['get'])
    def activity_performance(self, request):
        qs = self.db.analytics.get_activity_type_performance()
        return self._process_pandas_response(
            qs,
            fields=None,
            stats_columns=['avg_distance', 'max_elevation']
        )

    @action(detail=False, methods=['get'])
    def user_levels(self, request):
        qs = self.db.analytics.get_user_activity_levels()
        return self._process_pandas_response(
            qs,
            fields=None,
            stats_columns=['activities_count'],
            group_by_col='status'
        )


class AnalyticsDashboard(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DataAccessLayer()

    def get(self, request):
        mode = request.GET.get('mode', 'plotly')

        if mode == 'benchmark':
            n_requests = int(request.GET.get('n_requests', 100))
            df_results = BenchmarkService.run_experiment(total_requests=n_requests)
            best_result = df_results.loc[df_results['duration'].idxmin()]
            chart = BenchmarkService.build_benchmark_chart(df_results)

            return render(request, 'activities/dashboard_benchmark.html', {
                'chart': chart,
                'n_requests': n_requests,
                'best_threads': best_result['threads'],
                'min_time': round(best_result['duration'], 3)
            })

        with self.db as db:
            data_sources = {
                'leaderboard': db.analytics.get_top_distance_users(),
                'social': db.analytics.get_social_activities(),
                'monthly': db.analytics.get_monthly_activity_stats(),
                'influencers': db.analytics.get_influential_users(),
                'types': db.analytics.get_activity_type_performance(),
                'levels': db.analytics.get_user_activity_levels(),
            }

        stats = {
            'avg_monthly_dist': 0,
            'max_monthly_dist': 0,
            'median_duration': 0
        }

        df_monthly = pd.DataFrame(data_sources['monthly'])
        if not df_monthly.empty:
            stats['avg_monthly_dist'] = round(df_monthly['total_distance'].mean(), 1)
            stats['max_monthly_dist'] = round(df_monthly['total_distance'].max(), 1)

        top_n = int(request.GET.get('top_n', 10))
        min_dist = float(request.GET.get('min_dist', 0))

        df_leaderboard = pd.DataFrame(data_sources['leaderboard'])
        if not df_leaderboard.empty:
            df_leaderboard = df_leaderboard[df_leaderboard['total_distance'] >= min_dist]
            df_leaderboard = df_leaderboard.head(top_n)
            data_sources['leaderboard'] = df_leaderboard.to_dict('records')

        if mode == 'bokeh':
            bokeh_data = ChartService.build_bokeh_charts(data_sources)
            return render(request, 'activities/dashboard_bokeh.html', {
                'current_top_n': top_n,
                'current_min_dist': min_dist,
                'stats': stats,
                'bokeh_script': bokeh_data['script'],
                'bokeh_divs': bokeh_data['divs'],
            })
        else:
            charts = ChartService.build_plotly_charts(data_sources)
            return render(request, 'activities/dashboard_plotly.html', {
                'charts': charts,
                'stats': stats,
                'current_top_n': top_n,
                'current_min_dist': min_dist,
            })