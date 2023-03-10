import pandas as pd
import geopandas
import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
from datetime import datetime

st.set_page_config( layout='wide' ) #para que a tabela se ajuste na pádina toda
@st.cache( allow_output_mutation=True ) #para garantir que a saída seja mutável
def get_data( path ):
    data = pd.read_csv( path )

    return data


@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url )

    return geofile


# get data
path = "kc_house_data.csv"
data = get_data( path )

# get geofile
#url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

url = "Zip_Codes.geojson"

geofile = get_geofile( url )

#add new features
    #preço por metro quadrado
data['price_m2'] = data['price'] / data['sqft_lot']

# -----------------------------
# DATA OVERVIEW
# -----------------------------

# criar um filtro de coluna
f_attributes = st.sidebar.multiselect( 'Enter columns', ['price', 'bedrooms', 'bathrooms', 'sqft_living',
       'sqft_lot', 'floors', 'waterfront', 'view', 'condition', 'grade',
       'sqft_above', 'sqft_basement', 'yr_built', 'yr_renovated', 'zipcode',
       'lat', 'long', 'sqft_living15', 'sqft_lot15', 'price_m2'] )

# criar filtro da região
f_zipcode = st.sidebar.multiselect( 'Enter zipcode', data['zipcode'].unique() )

st.title( 'Data Overview' )


# attributes + zipcode = selecionar colunas e linhas
if ( f_zipcode != [] ) & ( f_attributes != [] ):
    aux = data.loc[ data['zipcode'].isin( f_zipcode), ['id', 'zipcode'] + f_attributes ]

# zipcode = selecionar linhas
elif( ( f_zipcode != [] ) & ( f_attributes == [] ) ):
    aux = data.loc[ data['zipcode'].isin( f_zipcode), : ]

# attributes = selecionar solunas
elif ((f_zipcode == []) & (f_attributes != [])):
    aux = data.loc[ :, ['id', 'zipcode'] + f_attributes ]

# 0 + 0 = retornar dataset original
else:
    aux = data.copy()

st.write( aux.head(6) )

# arrumando tamanho das colunas
c1, c2 = st.columns((1, 1))

# AVERAGE METRICS
if ('price' in aux.columns) & ('sqft_living' in aux.columns) & ('price_m2' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df2 = aux[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df3 = aux[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = aux[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    m1 = pd.merge(df1, df2, on='zipcode', how='inner')
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')

elif ('price' not in aux.columns) & ('sqft_living' not in aux.columns) & ('price_m2' not in aux.columns):
    df = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()

elif ('price' not in aux.columns) & ('sqft_living' in aux.columns) & ('price_m2' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = aux[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    m2 = pd.merge(df1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')
elif ('price' not in aux.columns) & ('sqft_living' in aux.columns) & ('price_m2' not in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df3, on='zipcode', how='inner')
elif ('price' not in aux.columns) & ('sqft_living' not in aux.columns) & ('price_m2' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df4 = aux[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df4, on='zipcode', how='inner')

elif ('sqft_living' not in aux.columns) & ('price' in aux.columns) & ('price_m2' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = aux[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    m2 = pd.merge(df1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')
if ('sqft_living' not in aux.columns) & ('price' in aux.columns) & ('price_m2' not in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df3, on='zipcode', how='inner')
elif ('sqft_living' not in aux.columns) & ('price' not in aux.columns) & ('price_m2' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df4 = aux[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df4, on='zipcode', how='inner')

elif ('price_m2' not in aux.columns) & ('price' in aux.columns) & ('sqft_living' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = aux[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    m2 = pd.merge(df1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')
elif ('price_m2' not in aux.columns) & ('price' not in aux.columns) & ('sqft_living' in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df3 = aux[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df3, on='zipcode', how='inner')
elif ('price_m2' not in aux.columns) & ('price' in aux.columns) & ('sqft_living' not in aux.columns):
    df1 = aux[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df4 = aux[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    # juntar tudo em uma tabela unica
    df = pd.merge(df1, df4, on='zipcode', how='inner')

else:
    st.write( 'Select more filters' )

c1.header( 'Average values' )
c1.dataframe( df, height=600 ) #mostrando na primeira coluna

# DESCRIPTIVE STATISTICS
num_attributes = df.select_dtypes( include=['int64', 'float64'])
media = pd.DataFrame( num_attributes.apply( np.mean ) )
mediana = pd.DataFrame( num_attributes.apply( np.median) )
std = pd.DataFrame( num_attributes.apply( np.std ) )

max_ = pd.DataFrame( num_attributes.apply( np.max ) )
min_ = pd.DataFrame( num_attributes.apply( np.min ) )

df5 = pd.concat([max_, min_, media, mediana, std], axis=1 ).reset_index()
df5.columns = ['attributes', 'max', 'min', 'mean', 'median', 'std']

c2.header('Descriptive statistics')
c2.dataframe( df5, height=600 ) #mostrando na segunda coluna

# -----------------------------------------------------------------------------------------
# REGION OVERVIEW
# -----------------------------------------------------------------------------------------

# ---------PORTFOLIO DENSITY MAP
# mapa em que o CEO consiga ver a quantidade de móveis por região

st.title( 'Region Overview' )

c1, c2 = st.columns( ( 1, 1), gap="large")
c1.header( 'Portfolio Density' )

# attributes + zipcode = selecionar colunas e linhas
if ( f_zipcode != [] ):
    aux2 = data.loc[ data['zipcode'].isin( f_zipcode)]
else:
    aux2 = data.sample(10000, replace=True)

#Base Map - Folium

density_map = folium.Map( location=[aux2['lat'].mean(), aux2['long'].mean() ],
                                    default_zoom_start=15)

marker_cluster = MarkerCluster().add_to( density_map ) # com essa biblioteca conseguimos adicionar marcadores

for name, row in aux2.iterrows():
    folium.Marker( [ row['lat'], row['long'] ],
                popup='Sold by R${0} on: {1} Features: {2} sqf, {3} bedroooms, {4} bathrooms, year built: {5}'.format(
                    row['price'] if 'price' in data.columns else 'none',
                    row['date'] if 'date' in data.columns else 'none',
                    row['sqft_living'] if 'sqft_living' in data.columns else 'none',
                    row['bedrooms'] if 'bedrooms' in data.columns else 'none',
                    row['bathrooms'] if 'bathrooms' in data.columns else 'none',
                    row['yr_built'] if 'yr_built' in data.columns else 'none'
                    ) ).add_to( marker_cluster )
with c1:
    folium_static( density_map, width=500, height=500 )


# ---------PRICE DENSITY MAP
c2.header( 'Price Density' )

# attributes + zipcode = selecionar colunas e linhas
if ( f_zipcode != [] ):
    aux3 = data.loc[ data['zipcode'].isin( f_zipcode)]
else:
    aux3 = data.sample(10000, replace=True)

df7 = aux3[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
df7.columns = ['ZIP', 'PRICE']

#df = data.sample(1000)

geofile = geofile[geofile['ZIP'].isin( df7['ZIP'].tolist() )]

region_price_map = folium.Map( location=[data['lat'].mean(),
                                    data['long'].mean() ],
                                    default_zoom_start=15)

# Para criar as regiões - cloropleth

region_price_map.choropleth( data=df7,
                             geo_data = geofile,
                             columns=['ZIP', 'PRICE'],
                             key_on='feature.properties.ZIP',
                             fill_color='YlOrRd',
                             fill_opacity= 0.7,
                             line_opacity= 0.2,
                             legend_name='AVG PRICE')
                            #o parâmetro key_on é o que vai fazer o meu arquivo conectar com o geofile
    #geofiles são arquivos json com o lat e long por região, achamos na internet facilmente

with c2:
    folium_static( region_price_map, width=500, height=500 )

# --------------------------------------------------
# DISTRIBUIÇÃO DOS IMÓVEIS POR CATEGORIAS COMERCIAIS
# --------------------------------------------------
st.sidebar.title('Commercial Options')
st.title('Commercial Attributes')

data['date'] = pd.to_datetime( data['date'] ).dt.strftime('%Y-%m-%d') #colocando em formato de data

# ---------AVERAGE PRICE PER YEAR BUILT
#year filter
min_year_built = int( data['yr_built'].min() )
max_year_built = int( data['yr_built'].max() )

st.sidebar.subheader( 'Select Max Year Built' )
f_year_built = st.sidebar.slider( 'Year Built', min_year_built, max_year_built, max_year_built)

st.header( 'Average Price per Year Built' )

#date filtering
df = data.loc[data['yr_built'] < f_year_built]
df = df[['yr_built', 'price']].groupby( 'yr_built' ).mean().reset_index()

#plot
fig = px.line( df, x='yr_built', y='price' )
st.plotly_chart( fig, use_container_width=True ) #gráfico mais largo com width

# ---------AVERAGE PRICE PER DAY
st.header( 'Average price per day' )
st.sidebar.subheader( 'Select max date' )

#day filter
min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
max_date = datetime.strptime( data['date'].max(), '%Y-%m-%d' )

f_date = st.sidebar.slider( 'Date', min_date, max_date, max_date)

#data filtering
data['date'] = pd.to_datetime( data['date'] )
df = data.loc[data['date'] < f_date]
df = df[['date', 'price']].groupby( 'date' ).mean().reset_index()

#para entender se estou comparando data com data
#st.write( type( f_date ) )
#st.write( type( data['date'][0] ) )

#plot
fig = px.line( df, x='date', y='price' )
st.plotly_chart( fig, use_container_width=True ) #gráfico mais largo com width


# ---------PRICE DISTRIBUTION
# histograma
st.header( 'Price Distribution' )
st.sidebar.subheader( 'Select Max Price' )

# filters
min_price = int( data['price'].min() )
max_price = int( data['price'].max() )
avg_price = int( data['price'].mean() )

f_price = st.sidebar.slider('Price', min_price, max_price, avg_price)

df = data.loc[data['price'] < f_price]

# data plot
fig = px.histogram( df, x='price', nbins=50 ) #nbins são quantas barras eu quero no meu histograma
st.plotly_chart( fig, use_container_width=True)

# --------------------------------------------------
# DISTRIBUIÇÃO DOS IMÓVEIS POR CATEGORIAS FÍSICAS
# --------------------------------------------------

st.sidebar.title( 'Attributes Options' )
st.title( 'House Atributtes' )

#filters
f_bedrooms = st.sidebar.selectbox( 'Max number of bedrooms',
                                    data['bedrooms'].sort_values().unique(),
                                    index=int(pd.DataFrame(data['bedrooms'].sort_values().unique()).idxmax()) )
f_bathrooms = st.sidebar.selectbox( 'Max number of bathrooms',
                                    data['bathrooms'].sort_values().unique(),
                                    index=int(pd.DataFrame(data['bathrooms'].sort_values().unique()).idxmax()))
f_floors = st.sidebar.selectbox( 'Max number of floors',
                                    data['floors'].sort_values().unique(),
                                    index=int(pd.DataFrame(data['floors'].sort_values().unique()).idxmax()))
f_waterview = st.sidebar.checkbox( 'Only houses with water view')

c1, c2 = st.columns( 2 )

# ---------HOUSE PER BEDROOMS
c1.header( 'Houses per bedrooms' )
df = data[ data['bedrooms'] < f_bedrooms ]
fig = px.histogram(df, x='bedrooms', nbins=19 )
c1.plotly_chart( fig, use_container_width=True )

# ---------HOUSE PER BATHROOMS
c2.header( 'Houses per bathrooms' )
df = data[ data['bathrooms'] < f_bathrooms ]
fig = px.histogram(df, x='bathrooms', nbins=19 )
c2.plotly_chart( fig, use_container_width=True )

c1, c2 = st.columns( 2 )

# ---------HOUSE PER FLOOR
c1.header('Houses per floor')
df = data[data['floors'] < f_floors]
fig = px.histogram(df, x='floors', nbins=19 )
c1.plotly_chart( fig, use_container_width=True )

# ---------HOUSE PER WATERVIEW
c2.header('Houses per waterview')
if f_waterview:
    df = data[data['waterfront'] == 1]
else:
    df = data.copy()
fig = px.histogram(df, x='waterfront', nbins=10 )
c2.plotly_chart( fig, use_container_width=True )












