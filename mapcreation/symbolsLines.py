import urllib
from PIL import ImageColor
from bs4 import BeautifulSoup




agsLineType = {"stroke-dasharray": 'esriSLSShortDot',
                   'stroke-linejoin': {'mitre': 'mitre', 'round': 'round', 'bevel': 'bevel'},
                   'stroke-linecap': {'butt': 'butt', 'round': 'round', 'square': 'square'}}



def convertSingleSymbol(lnRule):

    # Check the symbol parameters and map the SLD to SimpleLineSymbol types
    chk = [list(lnattr.attrs.values())[0] for lnattr in lnRule.find_all('sld:CssParameter')]



    # Check for a lineSymbolizer
    lnSymbolizer = lnRule.find_all('sld:LineSymbolizer')[0]


    # LineColor Opacity
    lnCLROpac = lnSymbolizer.find_all('sld:CssParameter', attrs={'name': 'stroke-opacity'})
    if lnCLROpac:
        lnOpacFLT = float(lnCLROpac[0].text)
        lnOpacFLTCNV1 = lnOpacFLT * 100
        lnOpacFLTCNV2 = lnOpacFLTCNV1 * 255
        lnOpac = round(lnOpacFLTCNV2 / 100)
    else:
        lnOpac = 255

    # LineColor
    lnCLR = lnSymbolizer.find_all('sld:CssParameter', attrs={'name': 'stroke'})

    if len(lnCLR) == 1:
        lnCLRrgb = list(ImageColor.getrgb(lnCLR[0].text))
        lnCLRrgb.append(lnOpac)
    else:
        lnCLRrgb = [255, 0, 0, lnOpac]

    # Line Width
    lnwidth = lnSymbolizer.find_all('sld:CssParameter', attrs={'name': 'stroke-width'})

    if len(lnwidth) == 1:
        lnwidthVal = lnwidth[0].text

    else:
        lnwidthVal = 1

    arcgisSimpLineJson = {
        'type':"esriSLS",
        'color':lnCLRrgb,
        'width':lnwidthVal
    }

    # Determine line Style
    lnStyle = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke-dasharray'})
    if lnStyle:
        arcgisSimpLineJson['style'] = agsLineType["stroke-dasharray"]

    if 'stroke-linejoin' in chk:
        lnJoinRule = lnRule.find_all('sld:CssParameter', attrs={'name': 'stroke-linejoin'})[0].text
        arcgisSimpLineJson['join'] = agsLineType['stroke-linejoin'][lnJoinRule]

    if 'stroke-linecap' in chk:
        lnJoinRule = lnRule.find_all('sld:CssParameter', attrs={'name': 'stroke-linecap'})[0].text
        arcgisSimpLineJson['cap'] = agsLineType['stroke-linecap'][lnJoinRule]

    simpleLineRenderer = {
        "type":"simple",
        "symbol":arcgisSimpLineJson
    }


    return simpleLineRenderer

def convertClassBrksValues(lnRules,parseSoup):
    clsField = parseSoup.find('ogc:PropertyName').text


    clsBreaksRen = {
        "type": "class-breaks",
        "field": clsField
    }

    clsBreaksRenBrkInfo = []


    clsDefaultSymbol = {"type": "simple-line", "color": [66, 60, 60, 1]};

    for lnRule in parseSoup.find_all('sld:Rule'):

        lnBrkInfo = {}

        if lnRule.find('ogc:PropertyIsBetween'):
            print('has a val')

            renType = 'classbreaks'

            # Find the low Range Value
            minValue = float(lnRule.find('ogc:LowerBoundary').find('Literal').text)

            # Find the max Range Value
            maxValue = float(lnRule.find('ogc:UpperBoundary').find('Literal').text)

            lnBrkInfo["minValue"] = minValue
            lnBrkInfo["maxValue"] = maxValue





        # Check for a lineSymbolizer
        lnSymbolizer = lnRule.find('sld:LineSymbolizer')

        # Check the symbol parameters and map the SLD to SimpleLineSymbol types
        chk = [list(lnattr.attrs.values())[0] for lnattr in lnRule.find_all('sld:CssParameter')]

        # LineColor Opacity
        lnCLROpac = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke-opacity'})
        if lnCLROpac:
            lnOpacFLT = float(lnCLROpac[0].text)
            lnOpacFLTCNV1 = lnOpacFLT * 100
            lnOpacFLTCNV2 = lnOpacFLTCNV1 * 255
            lnOpac = round(lnOpacFLTCNV2 / 100)
        else:
            lnOpac = 255

        # LineColor
        lnCLR = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke'})

        if len(lnCLR) == 1:
            lnCLRrgb = list(ImageColor.getrgb(lnCLR.text))
            lnCLRrgb.append(lnOpac)
        else:
            lnCLRrgb = [255, 0, 0, lnOpac]

        # Line Width
        lnwidth = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke-width'})

        if len(lnwidth) == 1:
            lnwidthVal = lnwidth.text

        else:
            lnwidthVal = 1

        clsBrkSymbol = {
            'type': "simple-line",
            'color': lnCLRrgb,
            'width': lnwidthVal
        }

        if 'stroke-linejoin' in chk:
            lnJoinRule = lnRule.find('sld:CssParameter', attrs={'name': 'stroke-linejoin'}).text
            clsBrkSymbol['join'] = agsLineType['stroke-linejoin'][lnJoinRule]

        if 'stroke-linecap' in chk:
            lnJoinRule = lnRule.find('sld:CssParameter', attrs={'name': 'stroke-linecap'}).text
            clsBrkSymbol['cap'] = agsLineType['stroke-linecap'][lnJoinRule]

        lnBrkInfo['symbol'] = clsBrkSymbol

        clsBreaksRenBrkInfo.append(lnBrkInfo)

    clsBreaksRen['classBreakInfos']=clsBreaksRenBrkInfo

    return clsBreaksRen


def convertUnqValues(lnRules,parseSoup):


    unqValueInfosDict = {}
    unqValueInfos = []

    unqDefaultSymbol = { "type": "simple-line", "color": [66, 60, 60, 1] };


    # Find the rules to get the unique values
    unqField = parseSoup.find('ogc:PropertyName').text

    unqValueInfosDict['uniqueField'] = unqField


    for lnRule in lnRules:#parseSoup.find_all('sld:Rule'):

        unqVal = lnRule.find('ogc:Literal').text


        # Check the symbol parameters and map the SLD to SimpleLineSymbol types
        chk = [list(lnattr.attrs.values())[0] for lnattr in lnRule.find_all('sld:CssParameter')]



        # Check for a lineSymbolizer
        lnSymbolizer = lnRule.find('sld:LineSymbolizer')

        # LineColor Opacity
        lnCLROpac = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke-opacity'})
        if lnCLROpac:
            lnOpacFLT = float(lnCLROpac[0].text)
            lnOpacFLTCNV1 = lnOpacFLT * 100
            lnOpacFLTCNV2 = lnOpacFLTCNV1 * 255
            lnOpac = round(lnOpacFLTCNV2 / 100)
        else:
            lnOpac = 255

        # LineColor
        lnCLR = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke'})

        if len(lnCLR) == 1:
            lnCLRrgb = list(ImageColor.getrgb(lnCLR.text))
            lnCLRrgb.append(lnOpac)
        else:
            lnCLRrgb = [255, 0, 0, lnOpac]

        # Line Width
        lnwidth = lnSymbolizer.find('sld:CssParameter', attrs={'name': 'stroke-width'})

        if len(lnwidth) == 1:
            lnwidthVal = lnwidth.text

        else:
            lnwidthVal = 1


        unqValSymbol = {
            'type':"simple-line",
            'color':lnCLRrgb,
            'width':lnwidthVal
        }

        if 'stroke-linejoin' in chk:
            lnJoinRule = lnRule.find('sld:CssParameter', attrs={'name': 'stroke-linejoin'}).text
            unqValSymbol['join'] = agsLineType['stroke-linejoin'][lnJoinRule]

        if 'stroke-linecap' in chk:
            lnJoinRule = lnRule.find('sld:CssParameter', attrs={'name': 'stroke-linecap'}).text
            unqValSymbol['cap'] = agsLineType['stroke-linecap'][lnJoinRule]



        unqValJson = {
            "value":unqVal,
            "label":unqVal,
            "description":"",
            "Symbol":unqValSymbol
        }

        unqValueInfos.append(unqValJson)



    unqValRenderer = {
        "type":"uniqueValue",
        "field1":unqField,
        "uniqueValueInfos":unqValueInfos
    }


    # return the distionary of the field and unique values
    return unqValRenderer





def processLineSymbol(stylFile):
    ###styleFile: the path to the .sld file, returns a list with the renderer and type###


    styURL = stylFile#'http://worldmap.harvard.edu/geoserver/styles/subwaylines_p_odp.sld'


    styReq = urllib.request.urlopen(styURL)
    data = styReq.read()
    text = data.decode('utf-8')

    soup = BeautifulSoup(text, 'xml')

    # Variable to return the polygon renderer to main thread
    retPolyLineRenderer = ''


    # Check for single, Unique and Classified
    renType = ''
    if soup.find_all('ogc:PropertyIsEqualTo'):
        renType = 'unique'
        unqRules = soup.find_all('sld:Rule')

        #Dictionary of field and unique values
        retPolyLineRenderer = convertUnqValues(unqRules,soup)

    elif soup.find_all(['ogc:PropertyIsLessThan','ogc:PPropertyIsGreaterThan','ogc:PropertyIsLessThanOrEqualTo','ogc:PropertyIsGreaterThanOrEqualTo']):
        renType = 'classbreaks'

        clsRules = soup.find_all('sld:Rule')

        # Dictionary of field and unique values
        retPolyLineRenderer = convertClassBrksValues(clsRules, soup)

    else:
        renType = 'single'
        lnCheck = soup.find_all('sld:FeatureTypeStyle')
        retPolyLineRenderer = convertSingleSymbol(lnCheck[0])

    basicLnSym = {}

    return [retPolyLineRenderer, renType]




