import ee 
from ee_plugin import Map 

#*** Start of imports. If edited, may not auto-convert in the playground. ***#


# Creamos nuestra area de estudio
Area_estudio = Popa
#*Selecciona una opcion y cambie la variable "Indice":
NDVI (Normalice diference vegetacion index)
NDWI (Normalized difference water index)
GCI (Green Coverage Index)
SAVI (Soil Adjusted Vegetation Index)
##
Indice = 'NDWI'
#Seleccionamos la coleccion de imagenes
#1: Landsat 8
#2: Sentinel 2
#Escoger una opccion
Satelite = 2
# Fechas de estudio
Fecha_inicio = '2021-01-01'
Fecha_fin = '2021-03-30'
# Guardamos y corremos el programa

#-------------------------------------------------------------------------------------------

# Centramos acorde al area de estudio
Map.centerObject(Area_estudio,15)

if (Satelite == 1){
  Colection = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR") \
                      .filterBounds (Area_estudio) \
                      .filterDate(Fecha_inicio, Fecha_fin) \
                      .filterMetadata("CLOUD_COVER", "less_than", 20)

} else {
  Colection = ee.ImageCollection("COPERNICUS/S2_SR") \
                      .filterBounds (Area_estudio) \
                      .filterDate(Fecha_inicio, Fecha_fin) \
                      .filterMetadata("CLOUDY_PIXEL_PERCENTAGE","less_than",20)
}
# Determinamos el numero de imagenes que tenemos en la coleeccion
N_imagenes = Colection.size()
print ('Numero de imagenes:', N_imagenes)

#Calculamos los diferentes indices
switch (Indice) {
  case 'NDVI':
    def NDVI(img):
      if (Satelite == 1){
        NDVI_img = img.addBands(img.normalizedDifference(['B5','B4']).rename("NDVI"))
        return NDVI_img
      } else {
        NDVI_img_ST = img.addBands(img.normalizedDifference(['B8','B4']).rename("NDVI"))
        return NDVI_img_ST
      }
    
    Vis_param = {"opacity":1,
    "bands":["NDVI"],
    "min":0,"max":0.8,
    "palette":["red","yellow","green"]}
    Col_indice = Colection.map(NDVI)
    break

#------------------------------------------------------------------------------------------------------
  case 'NDWI':
    def NDWI(img):
      if (Satelite == 1){
        NDWI_img = img.addBands(img.normalizedDifference(['B3','B5']).rename("NDWI"))
        return NDWI_img
      } else {
        NDWI_img_ST = img.addBands(img.normalizedDifference(['B3','B8']).rename("NDWI"))
        return NDWI_img_ST
      }
    
    Col_indice = Colection.map(NDWI)
    Vis_param = {
      "opacity":1,
      "bands":["NDWI"],
      "min":-1,
      "max":0.2,
      "palette":["169d06","ff1818","37edff"]}
    break
#-----------------------------------------------------------------------
  case 'GCI':
    def GCI(img):
      if (Satelite == 1){
        GCI_img = img.addBands(((img.select("B5").divide(img.select("B3"))).subtract(1)).rename("GCI"))
        return GCI_img
      } else {
        GCI_img_ST = img.addBands(((img.select("B7").divide(img.select("B5"))).subtract(1)).rename("GCI"))
        return GCI_img_ST
      }
    
    Col_indice = Colection.map(GCI)
    if (Satelite == 1){
      min = 1
      max = 5
    } else {
      min = 0
      max = 3.5
    }
    Vis_param = {
      "opacity":1,
      "bands":["GCI"],
      "min": min,
      "max": max,
      "palette":["b48674","ffee25","5fff6c","2a8138"]}
  break
#--------------------------------------------------------------------------
  case 'SAVI':
    def SAVI(img):
      if (Satelite == 1){
        B5 = img.select("B5")
        B4 = img.select("B4")
        L = 0.5
        SAVI_img = img.addBands((((B5.subtract(B4)).divide((B5.add(B4)).add(L))).multiply(L+1)) \
        .rename("SAVI"))
        return SAVI_img
      } else {
        B8_ST = img.select("B8")
        B4_ST = img.select("B4")
        L_ST = 0.2
        SAVI_img_ST = img.addBands((((B8_ST.subtract(B4_ST)).divide((B8_ST.add(B4_ST)).add(L_ST))).multiply(L_ST+1)) \
        .rename("SAVI"))
        return SAVI_img_ST
      }
    
    Col_indice = Colection.map(SAVI)
        if (Satelite == 1){
      min = 0
      max = 1.5
    } else {
      min = 0
      max = 1
    }
    Vis_param = {
      "opacity":1,
      "bands":["SAVI"],
      "min":0,
      "max":1.5,
      "palette":["red","yellow","green"]}
    break
  default:
    print ('Aun no se desarrolla el indice solicitado')
}

#Cortamos la coleccion
def corte (img):
  return img.clip(Area_estudio)

Col_corte = Col_indice.map(corte)
imageVis = {
  "opacity":1,
  "bands":["B4","B3","B2"],
  "min":389.655,
  "max":3431.3807142857145,
  "gamma":[1.2, 1.2, 1.2]}

Col_corte_prom =  Col_corte.mean()
Map.addLayer(Col_corte_prom, imageVis, 'Promedio_RGB')
print ('Colection', Colection)
colection_mean = Col_corte.mean()
print ('colection_mean', colection_mean)
nombre = 'Promedio_'+ Indice
Map.addLayer(colection_mean, Vis_param, nombre, 1)

# Creamos un titulo
title = ui.Label(Indice + ' Promedio')
title.style().set({
  'position': 'top-center',
  'fontWeight': 'bold'
})
#*title.style().set('position', 'top-center')
title.style().set('color', 'white')
title.style().set('backgroundColor', 'black')
title.style().set('padding', '4px 4px 4px 4px')
title.style().set('border', '1px solid black')
title.style().set('fontFamily', 'serif')
title.style().set('fontWeight', 'bold');*#
Map.add(title)

#Barra

def makeColorBarParams (palette):
  return {
    'bbox': [0, 0, 1, 0.1],
    'dimensions': '100x8',
    format: 'png',
    'min': 0,
    'max': 1,
    'palette': palette,
  }



colorBar = ui.Thumbnail({
  #Se crea una imagen que contiene los valores de lat y long por pixel
  'image': ee.Image.pixelLonLat().select(0),
  'params': makeColorBarParams(Vis_param.palette),
  'style': '{stretch': 'horizontal', 'margin': '0px 8px', 'maxHeight': '100px', 'width': '200px'},
})

minimo = Vis_param.min

legendLabels = ui.Panel({
  'widgets': [
    ui.Label(Vis_param.min, {'margin': '4px 5px'}),
    ui.Label(
        ((Vis_param.max + Vis_param.min) / 2),
        {'margin': '4px 8px', 'textAlign': 'center', 'stretch': 'horizontal'}),
    ui.Label(Vis_param.max, {'margin': '4px 8px'})
  ],
  'layout': ui.Panel.Layout.flow('horizontal')
})


legendTitle = ui.Label({
  'value': Indice,
  'style': {
    'fontWeight': 'bold',
    'margin': '4px 8px'
    #width: '200px',
    #height : '10px'
  }
})

legendPanel = ui.Panel(legendTitle).add(colorBar).add(legendLabels)
legendPanel.style().set({
  #height: '95px',
  #width: '200px',
  'position': 'bottom-right'
})
Map.add(legendPanel)

#-----------------------------------------------------------
#Anadimos el mapa de ubicacion

# Make a little map.
map_base = ui.Map()
map_base.setOptions('ROADMAP')
map_base.setControlVisibility({'zoomControl': False, 'drawingToolsControl': False, 'mapTypeControl': False})

# Make the little map display an inset of the big map.
def createInset():
  bounds = ee.Geometry.Rectangle(Map.getBounds())
  map_base.centerObject(bounds)
  map_base.clear()
  map_base.addLayer(bounds)


# Run it once to initialize.
createInset()

# Get a new inset map whenever you click on the big map.
Map.onClick(createInset)

# Display the inset map in the console.
print(map_base)
