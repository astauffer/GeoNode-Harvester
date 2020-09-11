from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import ast
import urllib.request
import json
import re

from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.mapping import generate_renderer
import pandas as pd

import symbolsPoints
import symbolsPolygon
import symbolsLines

import operator
from functools import reduce

#mapID = 17305


def processMap(processOrg,fldr,mapTitle,mpNum,mpLayerTags,termsOfUse):


    #Flatten and get the unique Tags

    mpTags = reduce(operator.concat,mpLayerTags)
    uniqueMpTags = set(mpTags)


    # Accesses the map metadata to understand the layers that are used in the map
    # Creates a list of the layers found
    styleFrontUrl = "http://worldmap.harvard.edu/geoserver/styles/"


    folderProcess = fldr#"HarvardForestDataMap"
    mTitle = mapTitle#'Harvard Forest Data Map'
    mapNum = mpNum#17305

    procSpace = r'C:\projects\HarvardMap\Data\{}'.format(folderProcess)

    # Dictionary lookup for sld styles
    sldGeomLookup = {}
    sldGeomLookup['MultiPolygon'] = "Polygon"
    sldGeomLookup['MultiLineString'] = "Polyline"
    sldGeomLookup['Point'] = "Point"


    # log into the org
    #gis = GIS(profile='harvardworldmap')
    gis = processOrg#(profile="myorg")


    # Access the map inventory Excel file and load into a dataframe for later access
    #mapDF = pd.read_csv(r"C:\projects\HarvardMap\Data\maps_tab\maps_tab_excelExport.csv",sep=',')
    #seaMP = mapDF[mapDF.id == '{}'.format(mapNum)]

    # read in the Published map data layers from conversion script
    # Add to a dataframe for later access


    # Connect to the log table to determine
    tbIT = gis.content.get('5ca2378ea96e48e7b5739b6121557c3e')
    # c2169b562b4f407e8acf2e2b73b11a4a
    # 5ca2378ea96e48e7b5739b6121557c3e
    tbl = tbIT.tables[0]
    tbDF = tbl.query(where="mapname='{}'".format(mapTitle), as_df=True)

    lyrlgPubPath = '{}\{}PubLyrLog.txt'.format(procSpace,mTitle)

    #pubLyrDataFrame = pd.read_csv(lyrlgPubPath,index_col='indxCol')


    browser = webdriver.Chrome(executable_path=r"C:\projects\chromedriver_win32\chromedriver.exe")

    #url = "https://worldmap.harvard.edu/maps/17305/info/"
    url = "https://worldmap.harvard.edu/maps/{}".format(mapNum)
    # url = "http://trainingapps.esri.com/osiris/TrainingEvents/Search?PageSize=20&OrderBy=StartDate&Direction=asc&InstructorName={0}+{1}&StartDate=09%2F12%2F2016&EndDate=12%2F31%2F2016".format(firstName,lastName)

    browser.implicitly_wait(60)
    a = browser.get(url)

    # FireFox
    # browser = webdriver.Firefox(executable_path=r"C:\Software\geckodriver-v0.20.0-win64\geckodriver.exe")
    # browser.get(url)


    # opnFile = open(r"C:\Dev\Python\OsirisTools\pythclass.html",'r')
    # pgSource = BeautifulSoup(opnFile,'html.parser')
    pgSource = BeautifulSoup(browser.page_source, 'html.parser')


    # Create an empty webmap
    empty_webmap = WebMap()


    s = pgSource.head.find_all('script')
    jj = s[18]
    regex = re.compile('\n^(.*?){(.*?)$|,', re.MULTILINE)
    js_text = re.findall(regex, jj.string) #Change jj.text to jj.string based on error
    mapJsonpre = js_text[76][1]
    mapJson = '{0}{1}'.format('{',mapJsonpre[:-2])
    mpJ = json.loads(mapJson)


    # Map Description from the JSON
    if mpJ['about']['introtext']:
        mapDesc = mpJ['about']['introtext']
    else:
        mapDesc = mTitle

    # Map scale
    #if mpJ['map']['maxResolution']:
        #mapScale = ['map']['maxResolution']

    grpDict = {}

    # Pull the group names into a list to reverse their order to preserve layer order from the map
    grpNames = [grp['group'] for grp in mpJ['map']['groups']]
    grpNames.reverse()


    for grp in grpNames:#mpJ['map']['groups']:
        grpName = grp#['group']
        print('GroupName :: {} '.format(grpName))
        grpLyrs = []
        for lyr in mpJ['map']['layers']:
            if lyr['group'] == grpName:
                print(lyr['title'])


                #if lyr['visibility']:
                    #if lyr['visibility']:


                #visibile layer start
                if lyr['title'] == 'Population Density (2010)km2':
                    print('need to stop')


                # # use the name to link over to the item ID
                # if not 'geonode:' in lyr['name']:
                #     llkUP = lyr['detail_url'].split("/")[-1]
                #     print(llkUP)
                # else:
                #     llkUP = lyr['name']

                # isolate and test if the current layer is published vectordata
                #publyrLookupID = tbDF.query("geonodeSRC == '{}'".format(llkUP))

                # search for the published Layer by snippet
                addLayer = gis.content.search(query='snippet:"{}"'.format(lyr['name']),item_type="Feature Layer")

                if len(addLayer) == 1:

                    # Check for styles in layer
                    if 'styles' in lyr and lyr['styles'] != '':


                        lyrStylesUrl = styleFrontUrl
                        sldFileURLTest = "{}{}".format(styleFrontUrl,lyr['styles'])

                        if ".sld" in sldFileURLTest:
                            sldFileURL = sldFileURLTest
                        else:
                            sldFileURL = "{}.sld".format(sldFileURLTest)

                    else:
                        #Check the layer info page
                        lyrInfo = urllib.request.urlopen('http://worldmap.harvard.edu/data/{}'.format(lyr['name']))
                        lyrInfoRD = lyrInfo.read()
                        lyrInfoRDDC = lyrInfoRD.decode('utf-8')

                        lyrInfoSoup = BeautifulSoup(lyrInfoRDDC)



                        spnTyle = lyrInfoSoup.find('span', attrs={'class': 'styles-list'})

                        if spnTyle:
                            styles = spnTyle.find_all('a')

                            if len(styles) > 0:
                                sldFileURL = styles[0].attrs['href']

                                # Need to write in how to distinguish renderer type
                                #simple_renderer = {"renderer": "autocast", "type": "simple"}
                                    # Check the style Geometry

                    #test the url for a valid connectiono
                    try:
                        stylOpen = urllib.request.urlopen(sldFileURL).read()
                        stylOpenDecode = stylOpen.decode('utf-8')






                        if 'PolygonSymbolizer' in stylOpenDecode:
                            sldGeom = 'Polygon'
                        elif 'LineSymbolizer' in stylOpenDecode:
                            sldGeom = 'Polyline'
                        elif 'PointSymbolizer' in stylOpenDecode:
                            sldGeom = 'Point'




                        # Find the geometry type and pass it to the right render Geometry
                        #sldGeom = sldGeomLookup[publyrLookupID.geometryType.values[0]]
                        renren = ""
                        if sldGeom == 'Point':
                            pntRenderer = symbolsPoints.processPointSymbol(sldFileURL)

                            renren = pntRenderer
                        if sldGeom == 'Polygon':
                            polyRenderer = symbolsPolygon.processPolygonSymbol(sldFileURL)

                            if polyRenderer[1] == 'classbreaks':
                                sdf = pd.DataFrame.spatial.from_layer(addLayer[0].layers[0])

                                if polyRenderer[0]['field'][0] == '_':
                                    sdfRenFLD = 'F{}'.format(polyRenderer[0]['field'])
                                else:
                                    sdfRenFLD = polyRenderer[0]['field']

                                genRen = generate_renderer('Polygon', sdf, render_type='c', field=sdfRenFLD)

                                brks = polyRenderer[0]['classBreakInfos']
                                genRen['classBreakInfos'] = brks

                                polyRenderer.pop(0)
                                polyRenderer.insert(0,genRen)

                            renren = polyRenderer

                        if sldGeom == 'Polyline':
                            lnRenderer = symbolsLines.processLineSymbol(sldFileURL)
                            
                            if lnRenderer[1] == 'classbreaks':
                                sdf = pd.DataFrame.spatial.from_layer(addLayer[0].layers[0])

                                if lnRenderer[0]['field'][0] == '_':
                                    sdfRenFLD = 'F{}'.format(lnRenderer[0]['field'])
                                else:
                                    sdfRenFLD = lnRenderer[0]['field']

                                genRen = generate_renderer('Polyline', sdf, render_type='c', field=sdfRenFLD)

                                brks = lnRenderer[0]['classBreakInfos']
                                genRen['classBreakInfos'] = brks

                                lnRenderer.pop(0)
                                lnRenderer.insert(0,genRen)

                            renren = lnRenderer

                    #renren[0]["renderer"] = "autocast"

                        # Get the item from the org
                        #addLayer = gis.content.search(query='snippet:"{}"')
                        #addLayer = gis.content.get(publyrLookupID.itemID.values[0])
                        if renren != "":

                            empty_webmap.add_layer(addLayer[0].layers[0],
                                                   {"type": "FeatureLayer", "renderer": renren[0],'visibility':lyr['visibility']})
                        else:
                            empty_webmap.add_layer(addLayer[0].layers[0],{"type": "FeatureLayer",'visibility':lyr['visibility']})


                    except:
                        empty_webmap.add_layer(addLayer[0].layers[0], {"type": "FeatureLayer",'visibility':lyr['visibility']})
                        pass




                            # Add an item update to remove the tracking snippet
                            # addLayer.update(item_properties={'snippet': "{}".format(lyr['title'])})
                    grpLyrs.append(lyr)


                else:
                    print('Current Layer {} does not have a featurelayer')
                    grpLyrs.append(lyr)
                    # # use the name to link over to the item ID
                # if not 'geonode:' in lyr['name']:
                #     llkUP = lyr['detail_url'].split("/")[-1]
                #     print(llkUP)
                # else:
                #     llkUP = lyr['name']
                #
                #
                # publyrLookupID = pubLyrDataFrame.query("geonodeSRC == '{}'".format(llkUP))


        grpDict[grpName] = grpLyrs














    webmapprops={'title':'{}'.format(mTitle),'description':mapDesc,'licenseInfo':termsOfUse,'snippet':' ','tags':uniqueMpTags}

    empty_webmap.save(item_properties=webmapprops)

    # Webmap center::: mpj['map']['center'] web merc coords 3857
    # Webmap zoom::::: mpj['map']['zoom']

if __name__=="__main__":
    # Accesses the map metadata to understand the layers that are used in the map
    # Creates a list of the layers found
    folderProcess = "AfricaDNA"

    onlyVisibleLayers = True

    fldr = folderProcess

    mpNum = 2788

    # Connect to the org
    gis = GIS(profile="worldmap_manager")
    processOrg = gis

    mapTitle = "Africa DNA"

    mpLayerTags = ["Africa DNA", "Harvard World Map"]

    termsOfUse = """<a href="https://creativecommons.org/licenses/by/3.0/us/"><img alt="Creative Commons License" src="https://i.creativecommons.org/l/by/3.0/us/88x31.png" style="border-width:0;" /></a><br />This work is licensed under a <a href="https://creativecommons.org/licenses/by/3.0/us/">Creative Commons Attribution 3.0 United States License</a>"""




    processMap(processOrg, fldr, mapTitle, mpNum, mpLayerTags, termsOfUse)