import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import plotly.express as px

def load_region_data():
    with open('data/provinces.geojson', 'rb') as f:
        regions = json.load(f)

    #df_areas = pd.read_csv('data/Разпределение по дата и по области.csv')
    df_areas = pd.read_csv('https://data.egov.bg/resource/download/cb5d7df0-3066-4d7a-b4a1-ac26525e0f0c/csv')

    df_areas.rename(columns = {'Дата' : 'date'}, inplace = True)
    df_areas['date'] = pd.to_datetime(df_areas['date'])
    df_population = pd.read_csv('data/region_population.csv', sep = '\t')

    cols= [k for k in df_areas.columns if '_ALL' in k]
    df_areas_all = df_areas.melt(id_vars = 'date', value_vars = cols, value_name = 'all_cases')
    df_areas_all['REG'] = df_areas_all['variable'].str[0:3]

    cols= [k for k in df_areas.columns if '_ACT' in k]
    df_areas_act = df_areas.melt(id_vars = 'date', value_vars = cols, value_name = 'active_cases')
    df_areas_act['REG'] = df_areas_act['variable'].str[0:3]

    df_areas_full = df_areas_act.merge(df_areas_all, on = ['date', 'REG'])

    df_areas_full = df_areas_full.merge(df_population, on= 'REG')

    df_areas_full['dt_str'] = df_areas_full['date'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df_areas_full.set_index('date', inplace = True)
    df_areas_full['active_cases_per_100k'] = round(df_areas_full['active_cases']/(df_areas_full['POPULATION']/100000),0)
    df_areas_full.drop(columns = ['variable_x', 'variable_y'], inplace = True)

      
    
    return df_areas_full, regions

def get_map(df_areas_full, regions):

    token = 'pk.eyJ1IjoiaTEyZmx5IiwiYSI6ImNrdGZwejk5aTBhbXoyb211cWswc3pjaHkifQ.j5ysSfwAGc267jYv3PGjlw'
    mapbox_style = 'outdoors'

    df_areas_map= df_areas_full.loc[df_areas_full.index.max()]
    fig  = px.choropleth_mapbox(df_areas_map,
                            geojson= regions,
                            locations='REG',
                            featureidkey="properties.nuts3",
                            color=df_areas_map['active_cases_per_100k'],
                            color_continuous_scale = 'reds',
                            range_color=[0,1000],
                            #hover_name = {'dt_str', 'POPULATION', 'active_cases_per_100k'},
                            hover_data = {'dt_str', 'POPULATION', 'active_cases', 'active_cases_per_100k'},
                            zoom=6, 
                            center={'lat':42.5 , 'lon':25.5 },
                            opacity=0.6,
                            animation_frame = 'dt_str'
                            )

    fig.update_layout(mapbox_style=mapbox_style, mapbox_accesstoken=token, legend=dict(y=0.95), coloraxis = dict(colorbar = dict(title = '')), title = 'Active Cases per 100k Population')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

def load_overall_data():
    #df_tests = pd.read_csv('data/Разпределение по видове тестове.csv')
    #df_overall = pd.read_csv('data/Обща статистика за разпространението.csv')
    df_tests = pd.read_csv('https://data.egov.bg/resource/download/0ce4e9c3-5dfc-46e2-b4ab-42d840caab92/csv')
    df_overall = pd.read_csv('https://data.egov.bg/resource/download/e59f95dd-afde-43af-83c8-ea2916badd19/csv')

    #transform test data
    df_date = df_tests.loc[:, ['Дата',
            'PCR тестове за денонощие','Установени случаи за денонощие чрез PCR',
        'Антигени тестове за денонощие', 'Установени случаи за денонощие чрез антиген',
        'Общо тестове за денонощие', 'Установени случаи за денонощие']]
    df_date.rename(columns = {'Дата' : 'date',
            'PCR тестове за денонощие': 'num_PCR','Установени случаи за денонощие чрез PCR': 'pos_PCR',
        'Антигени тестове за денонощие': 'num_AG', 'Установени случаи за денонощие чрез антиген': 'pos_AG',
        'Общо тестове за денонощие': 'num_tests', 'Установени случаи за денонощие': 'pos_tests'}, inplace = True)
    df_date['date'] = pd.to_datetime(df_date['date'])
    df_date.set_index('date', inplace = True)

    #transform overall data
    df_overall.rename(columns = {'Дата' : 'date', 'Направени тестове': 'tests_done', 'Тестове за денонощие': 'tests_today',
        'Потвърдени случаи': 'all_cases', 'Активни случаи': 'active_cases', 'Нови случаи за денонощие': 'new_cases',
        'Хоспитализирани': 'all_hospitalized', 'Новохоспитализирани': 'new_hospitalized', 'В интензивно отделение': 'icu',
        'Излекувани': 'healed', 'Излекувани за денонощие': 'healed_today', 'Починали': 'all_deaths',
        'Починали за денонощие': 'deaths_today'}, inplace = True)

    df_overall['date'] = pd.to_datetime(df_overall['date'])
    df_overall.set_index('date', inplace = True)

    df_date = df_overall.join(df_date, how = 'left')

    df_date['perc_PCR'] = round(df_date['pos_PCR']/df_date['num_PCR']*100,1)
    df_date['perc_AG'] = round(df_date['pos_AG']/df_date['num_AG']*100,1)
    df_date['perc_tests'] = round(df_date['pos_tests']/df_date['num_tests']*100,1)
    df_date['num_PCR_roll7'] = round(df_date['num_PCR'].rolling(7).mean(),0)
    df_date['pos_PCR_roll7'] = round(df_date['pos_PCR'].rolling(7).mean(),0)
    df_date['perc_PCR_roll7'] = round(df_date['pos_PCR_roll7']/df_date['num_PCR_roll7']*100,1)
    df_date['num_AG_roll7'] = round(df_date['num_AG'].rolling(7).mean(),0)
    df_date['pos_AG_roll7'] = round(df_date['pos_AG'].rolling(7).mean(),0)
    df_date['perc_AG_roll7'] = round(df_date['pos_AG_roll7']/df_date['num_AG_roll7']*100,1)
    df_date['num_tests_roll7'] = round(df_date['num_tests'].rolling(7).mean(),0)
    df_date['pos_tests_roll7'] = round(df_date['pos_tests'].rolling(7).mean(),0)
    df_date['perc_tests_roll7'] = round(df_date['pos_tests_roll7']/df_date['num_tests_roll7']*100,1)
    df_date['deaths_roll7'] = round(df_date['deaths_today'].rolling(7).mean(),0)
    df_date['new_cases_roll7'] = round(df_date['new_cases'].rolling(7).mean(),0)
    df_date['icu_roll7'] = round(df_date['icu'].rolling(7).mean(),0)
    df_date['all_hospitalized_roll7'] = round(df_date['all_hospitalized'].rolling(7).mean(),0)
    df_date['new_hospitalized_roll7'] = round(df_date['new_hospitalized'].rolling(7).mean(),0)
    df_date['healed_today_roll7'] = round(df_date['healed_today'].rolling(7).mean(),0)

    return df_date

def load_sexage():

    df_deaths_agesex = pd.read_csv('https://data.egov.bg/resource/download/18851aca-4c9d-410d-8211-0b725a70bcfd/csv')
    #df_deaths_agesex = pd.read_csv('data/Починали по пол и възрастови групи.csv')

    df_deaths_agesex.rename(columns = {'Дата' : 'date', 'Пол': 'sex', 'Възрастова група': 'age_group', 'Брой починали': 'deaths'}, inplace = True)
    df_deaths_agesex['date'] = pd.to_datetime(df_deaths_agesex['date'])
    df_deaths_agesex.set_index('date', inplace = True)
    df_deaths_agesex.replace('-', np.nan,inplace = True)
    sex = {'мъж' : 'male', 'жена' : 'female'}
    df_deaths_agesex['sex'] = df_deaths_agesex['sex'].map(sex)

    df_deaths_grsex = df_deaths_agesex.groupby(['date', 'sex']).sum()
    df_deaths_grsex = df_deaths_grsex.unstack()
    df_deaths_grsex = df_deaths_grsex.droplevel(level = 0, axis = 1)
    df_deaths_grsex.rename(columns = {'male': 'deaths_male', 'female': 'deaths_female'}, inplace = True)
    df_deaths_grsex.replace(np.nan, 0, inplace = True)
    df_deaths_grsex['deaths_male_roll7'] = round(df_deaths_grsex['deaths_male'].rolling(7).mean(),0)
    df_deaths_grsex['deaths_female_roll7'] = round(df_deaths_grsex['deaths_female'].rolling(7).mean(),0)
    df_deaths_grsex['delta'] = df_deaths_grsex['deaths_male'] - df_deaths_grsex['deaths_female']
    df_deaths_grsex['delta_roll7']= round(df_deaths_grsex['delta'].rolling(7).mean(),0)

    return df_deaths_agesex, df_deaths_grsex

def get_tests_statictics(df_date):

    OPACITY = 0.6

    fig = go.Figure()
    temp = df_date.loc['2020-12-20' : ].dropna(inplace = True)

    fig.add_trace(go.Scatter( x=temp.index, y=temp["perc_PCR_roll7"], name = 'PCR',
                            opacity = OPACITY,  line=dict(color='black', dash='dash')))
    fig.add_trace(go.Scatter( x=temp.index, y=temp["perc_AG_roll7"], name = 'AG', 
                            opacity = OPACITY,line=dict(color='black', dash='dot')))
    fig.add_trace(go.Scatter( x=temp.index, y=temp["perc_tests_roll7"], name = 'All', 
                            opacity = OPACITY,line=dict(color='black', dash='solid')))

    # Edit the layout
    fig.update_layout(  title='Positive Test Rate per Type (%)',
                        xaxis_title='Year 2021',
                        yaxis_title='Positive Rate (%)',
                        plot_bgcolor='white',
                        xaxis=dict(
                                    showline=True,
                                    showgrid=False,
                                    showticklabels=True,
                                    linecolor='rgb(0, 0, 0)',
                                    linewidth=1,
                                    ticks='outside',
                                    tickfont=dict(
                                        family='Calibri',
                                        size=14,
                                        color='rgb(82, 82, 82)'
                                    )),
                        yaxis=dict(
                                showgrid=False,
                                zeroline=False,
                                linecolor='rgb(0, 0, 0)',
                                showline=True,
                                showticklabels=True,
                        ))

    annotations = []
    
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
    ))
    

    annotations.append(dict(xref='paper', x=1.00, y=temp["perc_AG_roll7"].tail(1)[0],
                                    xanchor='left', yanchor='middle',
                                    text='AG-{}%'.format(temp["perc_AG_roll7"].tail(1)[0]),
                                    font=dict(family='Calibri',
                                                size=14),
                                    showarrow=False))

    annotations.append(dict(xref='paper', x=1.00, y=temp["perc_tests_roll7"].tail(1)[0],
                                    xanchor='left', yanchor='middle',
                                    text='All-{}%'.format(temp["perc_tests_roll7"].tail(1)[0]),
                                    font=dict(family='Calibri',
                                                size=14),
                                    showarrow=False))

    fig.update_layout(annotations = annotations)

    return fig

def get_chart(startdate, enddate, df_date, cols,  color, linestyle, name, title):

    OPACITY = 0.5

    fig = go.Figure()

    df_date = df_date.loc[startdate : enddate]
    #df_date = df_date.dropna(inplace = True)

    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter( x=df_date.index, y=df_date[col], name = name[i], 
                                opacity = OPACITY,  line=dict(color=color[i], dash=linestyle[i])))


    # Edit the layout
    fig.update_layout( title = title, xaxis = XAXIS,yaxis = YAXIS, legend = LEGEND,  plot_bgcolor='white')

    return fig

def get_age_hist(startdate, enddate,df_deaths_sexage, color):
    df_deaths_sexage = df_deaths_sexage.loc[startdate : enddate]
    df_deaths_agesex_group = df_deaths_sexage.groupby(['sex', 'age_group']).sum()
    df_deaths_agesex_group.reset_index(inplace = True)

    fig = go.Figure()
    fig = px.bar(df_deaths_agesex_group, x = 'age_group', y = 'deaths', color = 'sex', barmode="group",opacity = 0.6, pattern_shape="sex",
                color_discrete_map={
                    'male': color[0],
                    'female': color[1]})
    fig.update_layout( title = 'Deaths by Age Group', xaxis = XAXIS,yaxis = YAXIS, legend = LEGEND,  plot_bgcolor='white')

    return fig


XAXIS=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(0, 0, 0)',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Calibri',
                size=14,
                color='rgb(82, 82, 82)'
            ))
YAXIS=dict(
        showgrid=False,
        zeroline=False,
        linecolor='rgb(0, 0, 0)',
        showline=True,
        showticklabels=True,
        )

LEGEND=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
        )