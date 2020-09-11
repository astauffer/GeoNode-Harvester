from bs4 import BeautifulSoup
import urllib.request
from arcgis.gis import GIS
from arcgis.features import Feature
import os
import re
import json
import time
import sys


# Accesses the map metadata to understand the layers that are used in the map
# Creates a list of the layers found
folderProcess = "Tester"
mapNum = 7694

# Connect to the org
#gis = GIS(profile='harvardworldmap')
gis = GIS(profile="worldmap_manager")

#Define the Terms of Use for each Layer to be Published
termsOfUse ="""<a href="https://creativecommons.org/licenses/by/3.0/us/"><img alt="Creative Commons License" src="https://i.creativecommons.org/l/by/3.0/us/88x31.png" style="border-width:0;" /></a><br />This work is licensed under a <a href="https://creativecommons.org/licenses/by/3.0/us/">Creative Commons Attribution 3.0 United States License</a>"""

# Get the organization index log (Hosted Table) via Online Item ID
indexTable = gis.content.get("5ca2378ea96e48e7b5739b6121557c3e").tables[0]

#Local directory on disk where the data will download and each log will be written local. The root directory needs to exist on local disk.
procSpace = r'C:\projects\HarvardMap\Data\{}'.format(folderProcess)

if not os.path.isdir(r'C:\projects\HarvardMap\Data\{}'.format(folderProcess)):
    os.mkdir(procSpace)


def writeToIndex(logVals):
    # function used to write the published service information to a hosted table
    writeValList = logVals.split(",")[1:]
    indxVal = int(logVals.split(",")[0])

    fldNames = ['mapname','itemID','title','geonodeSRC']

    logRow = {k:v for k,v in zip(fldNames,writeValList)}

    logRow['indxCol'] = indxVal
    logRow['geometryType'] = "NA"

    logRowAdd = Feature(attributes=logRow)

    indexTable.edit_features(adds=[logRowAdd])


# Get the map page info
mapPageInfoUrl = r'http://worldmap.harvard.edu//maps/{}/'.format(mapNum)

mapInfoRequest = urllib.request.urlopen(mapPageInfoUrl)

mapDataInfo = mapInfoRequest.read()

textInfo = mapDataInfo.decode('utf-8')

soupMpInfo = BeautifulSoup(textInfo, 'xml')

# The header of the map page has a json object in the response that details information about the map
# The following code uses a regular expression to find and draw out that information
scrTags = soupMpInfo.head.find_all('script')
scrMapJson = scrTags[18]
regex = re.compile('\n^(.*?){(.*?)$|,', re.MULTILINE)
js_textMPSrc = re.findall(regex, scrMapJson.text)
mapJsonpre = js_textMPSrc[76][1]
mapJson = '{0}{1}'.format('{',mapJsonpre[:-2])
mpJ = json.loads(mapJson)

# Map title from the JSON repsonse
mapTitleFromJson = mpJ['about']['title']

# Access the underlying metadata of the map
mapCapUrl = r'http://worldmap.harvard.edu//capabilities/map/{}/'.format(mapNum)


# Make a request for the map capabilities page
mapRequest = urllib.request.urlopen(mapCapUrl)

data = mapRequest.read()

text = data.decode('utf-8')

soup = BeautifulSoup(text, 'xml')

# Current map name
mpName = soup.find('Name').text

# log out the map and the layers migrated
lg = open('{}\{}lyrLog.txt'.format(procSpace,mapTitleFromJson),'w')
lg.write(mapTitleFromJson +'\n')

# Create a layer published log to support creating the WebMaps later
lyrlgPub = open('{}\{}PubLyrLog.txt'.format(procSpace,mapTitleFromJson),'w')
lyrlgPub.write('indxCol,mapname,itemID,title,geonodeSRC\n')

# Create a python list to hold the records to add to the textfile
lyrlgPubLst = []


# Dictionary of layers not processes
lyrsNotProcess = {}

# Dictionary of layers processed
lyrsProcess = {}

# Get the underlying geoserver names to query for URL downloads
lyrs = soup.find_all('Layer',attrs={'queryable':'1'})

# Add: Check for map with no layers exit and report
if lyrs == None:
    #lyrlgPub.write('indxCol,mapname,itemID,title,geometryType,geonodeSRC\n')
    logVal = '1,mapname,NA,NA,NA'
    lyrlgPub.write('{}\n'.format(logVal))
    lyrlgPub.close()

    writeToIndex(logVal)

    sys.exit(0)


# Potential issues with download so close to publishing
# Create a Dictionary that will be looped on to publish after download
publishSHPDict={}


# Get the layer names from the map to use in the webmap later
mpLyrsTitle = [l.find('Title').text for l in lyrs]


# Create a list to hold the layers to add to a webmap
webMapLayers = []

# Collect all the keywords to add the map
mapLayerTags = []

print(mpLyrsTitle)
for iVal,l in enumerate(lyrs):

    # Create a dictionary of publishing information
    publishDict = {}

    # find a layer name match
    layerNameLookUp = l.find('Title').text

    if l.Name.text.count("geonode:") == 1:
        lyrURL = 'http://worldmap.harvard.edu/data/{}'.format(l.Name.text)
    else:
        lyrURL = 'http://worldmap.harvard.edu/data/geonode:{}'.format(l.Name.text)

    ly = [y for y in mpJ['map']['layers'] if y['title'] == layerNameLookUp]

    #if len(ly) >0:
    # Check to see if the layer has already been published
    if l.Name.text.find('geonode:',0,6)!=-1:
        whr = "geonodeSRC = '{}'".format(l.Name.text)
    else:
        whr = "geonodeSRC = 'geonode:{}'".format(l.Name.text)

    layerTest = indexTable.query(where=whr)

    if len(layerTest.features) > 0:
        # Get the item iD to add to the new record
        itmID = layerTest.features[0].attributes['itemID']

        # Get the item iD to add to the new record
        lyrTitle = layerTest.features[0].attributes['title']

        # Write published services to the local log file
        logVal = '{0},{1},{2},{3},{4}'.format(iVal, mapTitleFromJson, itmID, lyrTitle, l.Name.text)

        # write to the Hosted index table in the organization
        writeToIndex(logVal)

        continue


    lyrPage = urllib.request.urlopen(lyrURL)

    lyrPageData = lyrPage.read()

    lyrPageDataSoup = BeautifulSoup(lyrPageData)
    ownT = lyrPageDataSoup.find_all('p')

    owner = [x.text for x in ownT if x.text.count('Owner') == 1]

    ownerMetadata = owner[0][owner[0].index(':') + 1:].strip()
    #lyrName = l.find_all('Name')
    #lyrNameText = lyrName[0].text
    #print(lyrNameText)

    # Get the map layer name to send to the publishing function
    agolLyrName = mpLyrsTitle[iVal]
    print(agolLyrName)


    # Check to see if the name has the geonode add it if needed
    #geoChk = lyrNameText[lyrNameText.rfind('/') + 1:].find('geonode:')
    #if geoChk == -1:
     #   lyrNameText = lyrNameText[lyrNameText.rfind('/') + 1:].replace(lyrNameText, 'geonode:{}'.format(geoChk))

    # get the metadata url for the layer
    lyrMeta = l.find('MetadataURL')
    oln = lyrMeta.findNext('OnlineResource')
    olnLink = oln.attrs['xlink:href']

    # Conditional check to see if url front end is there
    geoNetHTTP = 'http://worldmap.harvard.edu/geonetwork'
    if geoNetHTTP in olnLink:
        lyrMUrl = olnLink
    else:
        lyrMUrl = r'http://worldmap.harvard.edu/geonetwork/{}'.format(olnLink)

    # construct metadata URL
    #lyrMUrl = olnLink#r'http://worldmap.harvard.edu/geonetwork/{}'.format(olnLink)
    mLyrPageLoad = urllib.request.urlopen(lyrMUrl)
    mLyrPageLoadRead = mLyrPageLoad.read()
    mLyrPageLoadReadDC = mLyrPageLoadRead.decode('utf-8')
    mLyrSoup = BeautifulSoup(mLyrPageLoadReadDC, 'xml')

    # Get the contact name
    gmRES = mLyrSoup.find('gmd:CI_ResponsibleParty').find('gmd:individualName')
    contactName = gmRES.text.strip()


    # Get layer extents
    extKeys = ['ymin', 'ymax', 'xmin', 'xmax']
    lyrExt = mLyrSoup.find('gmd:EX_GeographicBoundingBox')
    lyrExtLST = lyrExt.text.replace('\n',' ').split()

    extentDict = dict(zip(extKeys,lyrExtLST))
    #extentDict ={}
    #extVals = ['gmd:westBoundLongitude','gmd:eastBoundLongitude','gmd:southBoundLatitude','gmd:northBoundLatitude']
    #for extVal in extVals:
     #   lyrExtTxt = mLyrSoup.find(extVal)
      #  lyrExtTxt.text.strip()

    # Find  the abstract for the description
    lyrAbstract = mLyrSoup.find('gmd:abstract')
    if lyrAbstract:
        itemDesc = lyrAbstract.text.strip()
    else:
        itemDesc = " "


    # Find keywords and use those as tags
    keyWords = mLyrSoup.find('gmd:MD_Keywords').find_all('gmd:keyword')
    if len(keyWords) > 0:
        keywordlist = keywordlist = [kword.text.strip() for kword in keyWords]
    else:
        keywordlist = [agolLyrName]

    # Append world map owner name to the item tags
    keywordlist.append(ownerMetadata)

    # Append the geonode source to tags
    keywordlist.append(l.Name.text)

    # Find the Shapefile URLS
    gJUrl = [g.text for g in mLyrSoup.find_all('gmd:URL') if 'SHAPE' in g.text or 'SHAPE-ZIP' in g.text ]

    if len(gJUrl) == 0:
        lyrsNotProcess[agolLyrName] = mapTitleFromJson
        lg.write(agolLyrName + 'has no shapefile \n')
        continue
    else:


        dnwlF = 'http://worldmap.harvard.edu'

        if dnwlF in gJUrl[0]:
            fileDownURL = gJUrl[0]
        else:
            fileDownURL = "{}{}".format(dnwlF, gJUrl[0])



        publishDict["agolLayerName"] = agolLyrName
        publishDict["agolLayerExtent"] = extentDict
        publishDict["layerTags"] = keywordlist
        publishDict["fileURL"] = fileDownURL#gJUrl[0]


        geoJsonFile = publishDict["fileURL"]

        # Collect the layer tags
        mapLayerTags.append(publishDict["layerTags"])



        # ~~~~~~~~~~~  Publish as shapefile Area  ~~~~~~~~~~~~~~~~

        if agolLyrName.find(' '):
            tempZPName = agolLyrName.replace(' ', '_')
        else:
            tempZPName = agolLyrName

        # temp download location for processing geojson
        fileLocation = r"C:\projects\HarvardMap\Data\{}\{}.zip".format(folderProcess,tempZPName)



        try:

            if not os.path.isfile(fileLocation):
                # Download the geojson file locally
                req = urllib.request.urlretrieve(fileDownURL, fileLocation)

            #fileSize = os.stat(fileLocation)

            #if fileSize.st_size > 100:

            #populate the publishShpDict
            publishSHPDict[agolLyrName] = [{'title': agolLyrName,'type': 'Shapefile','description':itemDesc,'snippet':l.Name.text,"licenseInfo": termsOfUse,
                                            "tags": publishDict["layerTags"]},fileLocation,l.Name.text]



        except:
            lg.write("{} did not download \n".format(agolLyrName))
            print('error adding to Publish Dictionary')
            continue


#Downloads of Shapes are complete now to publish shapes and write to logs


for lyrKey in publishSHPDict.keys():
    lyrPubInfo = publishSHPDict[lyrKey]

    # Search for the shapefile to see if it is there
    orgSHP = gis.content.search(lyrPubInfo[0]['title'], 'Shapefile')

    if len(orgSHP)==0:
        pubLyr = gis.content.add(lyrPubInfo[0],
                             data=lyrPubInfo[1]
                             )

        if gis.content.is_service_name_available(lyrPubInfo[2],'featureService'):
            pubFeatLyr = pubLyr.publish()


            # Write published services to the local log file
            logVal = '{0},{1},{2},{3},{4}'.format(iVal, mapTitleFromJson, pubFeatLyr.id, pubFeatLyr.title, lyrPubInfo[2])

            webMapLayers.append([logVal])

            lyrlgPub.write('{0},{1},{2},{3},{4}\n'.format(iVal, mapTitleFromJson, pubFeatLyr.id, pubFeatLyr.title, lyrPubInfo[2]))
            lg.write(agolLyrName + '\n')

            # write to the Hosted index table in the organization
            writeToIndex(logVal)


print('Done')
lg.close()
lyrlgPub.close()


#Write the published info to an output file

w = open(r'{}\{}publishLog.csv'.format(procSpace,mapTitleFromJson), 'w')
w.write('indxCol,mapname,itemID,title,geonodeSRC\n')
for ln in webMapLayers:
    w.writelines(ln[0] + '\n')

w.close()




