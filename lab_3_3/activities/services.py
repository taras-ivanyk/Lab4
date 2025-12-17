import pandas as pd
import plotly.express as px
from plotly.offline import plot
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from math import pi
import time
import concurrent.futures
from django.db import connection
from django.contrib.auth.models import User


class ChartService:
    @staticmethod
    def get_queryset_as_df(queryset):
        return pd.DataFrame(list(queryset))

    @staticmethod
    def build_plotly_charts(data):
        charts = {}

        df = pd.DataFrame(data.get('leaderboard', []))
        if not df.empty:
            charts['leaderboard'] = plot(
                px.bar(df, x='username', y='total_distance', title="Топ користувачів",
                       color='total_distance', color_continuous_scale='Viridis'),
                output_type='div')

        df = pd.DataFrame(data.get('social', []))
        if not df.empty:
            df['label'] = df['user__username']
            charts['social'] = plot(
                px.scatter(df, x='comments_count', y='kudos_count', size='engagement_score',
                           color='engagement_score', hover_name='label', title="Соціальна взаємодія"),
                output_type='div')

        df = pd.DataFrame(data.get('monthly', []))
        if not df.empty:
            charts['monthly'] = plot(
                px.line(df, x='month', y='total_distance', markers=True, title="Дистанція по місяцях"),
                output_type='div')

        df_dist = pd.DataFrame(data.get('leaderboard', []))
        if not df_dist.empty:
            charts['influencers'] = plot(
                px.histogram(df_dist, x='total_distance', nbins=10,
                             title="Розподіл дистанцій",
                             labels={'total_distance': 'Дистанція (км)', 'count': 'Кількість'},
                             color_discrete_sequence=['#ef553b']),
                output_type='div')

        df = pd.DataFrame(data.get('types', []))
        if not df.empty:
            charts['types'] = plot(
                px.bar(df, x='avg_distance', y='activity_type', orientation='h',
                       title="Середня дистанція за типом", color='avg_distance'),
                output_type='div')

        df = pd.DataFrame(data.get('levels', []))
        if not df.empty:
            path = ['status']
            if 'username' in df.columns:
                path.append('username')

            charts['levels'] = plot(
                px.sunburst(df, path=path, values='activities_count',
                            title="Рівні активності"),
                output_type='div')

        return charts

    @staticmethod
    def build_bokeh_charts(data):
        plots = {}

        df = pd.DataFrame(data.get('leaderboard', []))
        if not df.empty:
            df = df.sort_values('total_distance', ascending=True)
            p = figure(y_range=df['username'].tolist(), height=350, title="🏆 Топ користувачів",
                       toolbar_location="right", tools="pan,wheel_zoom,reset,save")
            p.hbar(y='username', right='total_distance', height=0.8, source=ColumnDataSource(df),
                   line_color='white', fill_color="#4c72b0")
            p.xgrid.grid_line_color = None
            p.add_tools(HoverTool(tooltips=[("Користувач", "@username"), ("Дистанція", "@total_distance{0.0} м")]))
            plots['leaderboard'] = p

        df = pd.DataFrame(data.get('social', []))
        if not df.empty:
            p = figure(title="💬 Соціальна взаємодія", height=350,
                       x_axis_label='Коментарі', y_axis_label='Лайки (Kudos)',
                       toolbar_location="right", tools="pan,wheel_zoom,reset,box_select")
            p.circle('comments_count', 'kudos_count', size=12, source=ColumnDataSource(df),
                     color="navy", alpha=0.6, fill_color="#2b8cbe")
            p.add_tools(HoverTool(tooltips=[("Користувач", "@user__username"), ("Score", "@engagement_score")]))
            plots['social'] = p

        df = pd.DataFrame(data.get('monthly', []))
        if not df.empty:
            p = figure(title="📅 Динаміка по місяцях", x_axis_type='datetime', height=350,
                       toolbar_location="above", tools="pan,wheel_zoom,reset")
            src = ColumnDataSource(df)
            p.line(x='month', y='total_distance', line_width=3, color="#e6550d", source=src)
            p.circle(x='month', y='total_distance', size=8, color="#e6550d", fill_color="white", source=src)
            p.add_tools(HoverTool(tooltips=[("Дата", "@month{%F}"), ("Дистанція", "@total_distance м")],
                                  formatters={'@month': 'datetime'}))
            plots['monthly'] = p

            df = pd.DataFrame(data.get('leaderboard', []))
            if not df.empty:
                import numpy as np

                hist, edges = np.histogram(df['total_distance'], bins=10)

                hist_df = pd.DataFrame({
                    'top': hist,
                    'left': edges[:-1],
                    'right': edges[1:]
                })
                hist_df['interval'] = [f"{int(l)}-{int(r)}м" for l, r in zip(hist_df['left'], hist_df['right'])]

                p = figure(title="📊 Розподіл дистанцій", height=350,
                           toolbar_location="above", tools="pan,wheel_zoom,reset")

                p.quad(top='top', bottom=0, left='left', right='right', source=ColumnDataSource(hist_df),
                       fill_color="#ef553b", line_color="white", alpha=0.8)

                p.y_range.start = 0
                p.xaxis.axis_label = 'Дистанція (м)'
                p.yaxis.axis_label = 'Кількість користувачів'

                p.add_tools(HoverTool(tooltips=[("Діапазон", "@interval"), ("К-сть", "@top")]))

                plots['influencers'] = p

        df = pd.DataFrame(data.get('types', []))
        if not df.empty:
            p = figure(y_range=df['activity_type'].tolist(), height=350, title="🏃 Середня дистанція (Тип)",
                       toolbar_location=None, tools="")
            p.hbar(y='activity_type', right='avg_distance', height=0.9, source=ColumnDataSource(df),
                   line_color='white', fill_color="#756bb1")
            p.add_tools(HoverTool(tooltips=[("Тип", "@activity_type"), ("Сер. дистанція", "@avg_distance{0.0} м")]))
            plots['types'] = p

        df = pd.DataFrame(data.get('levels', []))
        if not df.empty:
            if 'status' in df.columns:
                df_grouped = df.groupby('status')['activities_count'].sum().reset_index()
            else:
                df_grouped = df


            total = df_grouped['activities_count'].sum()
            if total > 0:
                df_grouped['angle'] = df_grouped['activities_count'] / total * 2 * pi
            else:
                df_grouped['angle'] = 0

            df_grouped['color'] = ["#31a354", "#fd8d3c", "#74c476"][:len(df_grouped)]  # Кольори вручну або палітра

            p = figure(height=350, title="📊 Активність (Статуси)", toolbar_location=None,
                       tools="hover", tooltips="@status: @activities_count", x_range=(-0.5, 0.5))

            p.annular_wedge(x=0, y=0, inner_radius=0.2, outer_radius=0.4,
                            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                            line_color="white", fill_color='color', legend_field='status',
                            source=ColumnDataSource(df_grouped))
            p.axis.visible = False
            p.grid.grid_line_color = None
            plots['levels'] = p

        script, divs = components(plots)
        return {'script': script, 'divs': divs}

class BenchmarkService:
    @staticmethod
    def _db_task():
        try:
            return User.objects.count()
        finally:
            connection.close()

    @staticmethod
    def run_experiment(total_requests=100):
        results = []
        thread_counts = [1, 2, 4, 8, 10, 16, 32]

        for workers in thread_counts:
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(BenchmarkService._db_task) for _ in range(total_requests)]
                for future in concurrent.futures.as_completed(futures):
                    pass

            end_time = time.time()
            duration = end_time - start_time

            results.append({
                'threads': workers,
                'duration': duration,
                'requests_per_sec': total_requests / duration
            })

        return pd.DataFrame(results)

    @staticmethod
    def build_benchmark_chart(df):
        if df.empty:
            return "<div>No Data</div>"

        fig = px.line(df, x='threads', y='duration', markers=True, title='Time vs Threads')
        return plot(fig, output_type='div')