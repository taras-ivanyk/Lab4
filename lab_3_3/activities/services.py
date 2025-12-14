import pandas as pd
import plotly.express as px
from plotly.offline import plot
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from math import pi


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
                px.bar(df, x='username', y='total_distance', title="Топ користувачів", color='total_distance'),
                output_type='div')

        df = pd.DataFrame(data.get('social', []))
        if not df.empty:
            df['label'] = df['user__username']
            charts['social'] = plot(
                px.scatter(df, x='comments_count', y='kudos_count', size='engagement_score', color='engagement_score',
                           hover_name='label', title="Соціальна взаємодія"), output_type='div')

        df = pd.DataFrame(data.get('monthly', []))
        if not df.empty:
            charts['monthly'] = plot(
                px.line(df, x='month', y='total_distance', markers=True, title="Дистанція по місяцях"),
                output_type='div')

        df = pd.DataFrame(data.get('influencers', []))
        if not df.empty:
            charts['influencers'] = plot(
                px.pie(df, names='username', values='followers_count', title="Частка підписників"), output_type='div')

        df = pd.DataFrame(data.get('types', []))
        if not df.empty:
            charts['types'] = plot(
                px.bar(df, x='avg_distance', y='activity_type', orientation='h', title="Середня дистанція за типом"),
                output_type='div')

        df = pd.DataFrame(data.get('levels', []))
        if not df.empty:
            charts['levels'] = plot(
                px.sunburst(df, path=['status', 'username'], values='activities_count', title="Рівні активності"),
                output_type='div')

        return charts

    @staticmethod
    def build_bokeh_charts(data):
        plots = {}

        df = pd.DataFrame(data.get('leaderboard', []))
        if not df.empty:
            p = figure(x_range=df['username'].tolist(), height=350, title="Топ користувачів", toolbar_location=None,
                       tools="")
            p.vbar(x='username', top='total_distance', width=0.9, source=ColumnDataSource(df), line_color='white',
                   fill_color="#4c72b0")
            p.xgrid.grid_line_color = None
            p.add_tools(HoverTool(tooltips=[("User", "@username"), ("Dist", "@total_distance")]))
            plots['leaderboard'] = p

        df = pd.DataFrame(data.get('social', []))
        if not df.empty:
            p = figure(title="Соціальна взаємодія", height=350, x_axis_label='Comments', y_axis_label='Kudos')
            p.scatter('comments_count', 'kudos_count', size=10, source=ColumnDataSource(df), color="navy", alpha=0.5)
            p.add_tools(HoverTool(tooltips=[("User", "@user__username"), ("Score", "@engagement_score")]))
            plots['social'] = p

        df = pd.DataFrame(data.get('monthly', []))
        if not df.empty:
            p = figure(title="Дистанція по місяцях", x_axis_type='datetime', height=350)
            src = ColumnDataSource(df)
            p.line(x='month', y='total_distance', line_width=2, source=src)
            p.scatter(x='month', y='total_distance', size=8, source=src, fill_color="white")
            p.add_tools(HoverTool(tooltips=[("Date", "@month{%F}"), ("Dist", "@total_distance")],
                                  formatters={'@month': 'datetime'}))
            plots['monthly'] = p

        df = pd.DataFrame(data.get('influencers', []))
        if not df.empty:
            d = df.copy()
            s = d['followers_count'].sum()
            d['angle'] = d['followers_count'] / s * 2 * pi if s > 0 else 0
            d['color'] = [Category20c[20][i % 20] for i in range(len(d))] if len(d) > 2 else ["#3182bd", "#6baed6"][
                :len(d)]
            p = figure(height=350, title="Частка підписників", toolbar_location=None, tools="hover",
                       tooltips="@username: @followers_count", x_range=(-0.5, 1.0))
            p.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', legend_field='username', source=ColumnDataSource(d))
            p.axis.visible = False
            p.grid.grid_line_color = None
            plots['influencers'] = p

        df = pd.DataFrame(data.get('types', []))
        if not df.empty:
            p = figure(y_range=df['activity_type'].tolist(), height=350, title="Середня дистанція за типом",
                       toolbar_location=None, tools="")
            p.hbar(y='activity_type', right='avg_distance', height=0.9, source=ColumnDataSource(df), line_color='white',
                   fill_color="#cab2d6")
            p.add_tools(HoverTool(tooltips=[("Type", "@activity_type"), ("Avg Dist", "@avg_distance")]))
            plots['types'] = p

        script, divs = components(plots)
        return {'script': script, 'divs': divs}