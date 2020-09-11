import urllib
from PIL import ImageColor
from bs4 import BeautifulSoup

#How to delinate between single, unique, class
def convertSingleFillSymbol(polyRule):

    simpFillSymbol = {
        "type": "esriSFS",
        "color": [92, 103, 196, 0],
        "outline": {
            "type": "esriSLS",
            "color": [178, 178, 178, 255],
            "width": 0.4,
            "style": "esriSLSSolid"
        },
        "style": "esriSFSSolid"
    }

    # Polygon fill color
    polyFillCLR = polyRule.find('sld:CssParameter', attrs={'name': 'fill'})




    if polyFillCLR:

        if polyFillCLR:
            polyFillCLRrgb = list(ImageColor.getrgb(polyFillCLR.text))
        else:
            polyFillCLRrgb = [0, 0, 0]


        # PolygonColor Opacity
        polyFillCLROpac = polyRule.find_all('sld:CssParameter', attrs={'name': 'fill-opacity'})
        if polyFillCLROpac:
            polyFillOpacFLT = float(polyFillCLROpac[0].text)
            polyFillOpacFLTCNV1 = polyFillOpacFLT*100
            polyFillOpacFLTCNV2 = polyFillOpacFLTCNV1 * 255
            polyFillOpac = round(polyFillOpacFLTCNV2/100)


        else:
            polyFillOpac = 1


        polyFillCLRrgb.append(polyFillOpac)

    else:
        polyFillCLRrgb = [244,244,244,0]

    simpFillSymbol['color'] = polyFillCLRrgb


    # Polygon outline color
    outLineCLR = polyRule.find_all('sld:CssParameter', attrs={'name': 'stroke'})
    if outLineCLR:

        outLineCLRrgb = list(ImageColor.getrgb(outLineCLR[0].text))
        outLineCLRrgb.append(255)
        simpFillSymbol['outline']['color'] = outLineCLRrgb

    # Polygon outline width
    outLineWidth = polyRule.find_all('sld:CssParameter', attrs={'name': 'stroke-width'})
    if outLineWidth:
        outLineWidthVal = outLineWidth[0].text
        simpFillSymbol['outline']['width'] = float(outLineWidthVal)





    simpleRenderer = {
        "type":"simple",
        "symbol":simpFillSymbol
    }

    return simpleRenderer

def convertClassBrksValues(lnRules,parseSoup):
    clsField = parseSoup.find('ogc:PropertyName').text

    # Track the min value for the renderer
    clsMinValRen = 0.0
    trackClsMinValRen = 1

    clsBreaksRenBrkInfo = []

    # simpFillSymbol = {
    #     "type": "esriSFS",
    #     "color": [92, 103, 196, 255],
    #     "outline": {
    #         "type": "esriSLS",
    #         "color": [178, 178, 178, 255],
    #         "width": 0.4,
    #         "style": "esriSLSSolid"
    #     },
    #     "style": "esriSFSSolid"
    # }

    for fillRule in parseSoup.find_all('sld:Rule'):
        polyBrkInfo = {}

        simpFillSymbol = {
            "type": "esriSFS",
            "color": [92, 103, 196, 255],
            "outline": {
                "type": "esriSLS",
                "color": [178, 178, 178, 255],
                "width": 0.4,
                "style": "esriSLSSolid"
            },
            "style": "esriSFSSolid"
        }


        if fillRule.find('ogc:PropertyIsBetween'):
            print('has a val')

            renType = 'classbreaks'

            # Find the low Range Value
            if trackClsMinValRen == 1:
                clsMinValRen = float(fillRule.find('ogc:LowerBoundary').find('Literal').text)
                trackClsMinValRen +=1
            #minValue = float(fillRule.find('ogc:LowerBoundary').find('Literal').text)
            #else:
                #clsMinValRen = 3

            # Find the max Range Value
            maxValue = float(fillRule.find('ogc:UpperBoundary').find('Literal').text)

            #polyBrkInfo["minValue"] = minValue
            polyBrkInfo["classMaxValue"] = maxValue

        # Polygon fill color
        polyFillCLR = fillRule.find_all('sld:CssParameter', attrs={'name': 'fill'})[0]


        if polyFillCLR:
            polyFillCLRrgb = list(ImageColor.getrgb(polyFillCLR.text))
        else:
            polyFillCLRrgb = [0, 0, 0]

        # PolygonColor Opacity
        polyFillCLROpac = fillRule.find_all('sld:CssParameter', attrs={'name': 'fill-opacity'})
        if polyFillCLROpac:
            polyFillOpacFLT = float(polyFillCLROpac[0].text)
            polyFillOpacFLTCNV1 = polyFillOpacFLT * 100
            polyFillOpacFLTCNV2 = polyFillOpacFLTCNV1 * 255
            polyFillOpac = round(polyFillOpacFLTCNV2 / 100)




        else:
            polyFillOpac = 130


        polyFillCLRrgb.append(polyFillOpac)

        # Polygon outline color
        outLineCLR = fillRule.find_all('sld:CssParameter', attrs={'name': 'stroke'})[0]
        outLineCLRrgb = list(ImageColor.getrgb(outLineCLR.text))
        outLineCLRrgb.append(255)

        # Polygon outline width
        outLineWidth = fillRule.find_all('sld:CssParameter', attrs={'name': 'stroke-width'})[0]
        outLineWidthVal = outLineWidth.text

        simpFillSymbol["color"] = polyFillCLRrgb
        simpFillSymbol["outline"]['width'] = outLineWidthVal
        simpFillSymbol["outline"]['color'] = outLineCLRrgb

        polyBrkInfo['symbol'] = simpFillSymbol
        polyBrkInfo['label'] = fillRule.Title.text

        clsBreaksRenBrkInfo.append(polyBrkInfo)
        del polyBrkInfo
        del simpFillSymbol

    clsBreaksRen = {
        "type": "classBreaks",
        "field": clsField,
        "visualVariables":[],
        "rotationType":"arithmetic",
        "minValue":clsMinValRen,
        "classBreakInfos":clsBreaksRenBrkInfo
    }

    return clsBreaksRen


def convertUnqValues(lnRules,parseSoup):

    # Get the field where the values are from
    unqField = parseSoup.find('ogc:PropertyName').text



    # Capture the uniqueValueInfos property of the renderer
    uniqueValueInfos = []

    for p in lnRules:


        simpFillSymbol = {
            "type": "esriSFS",
            "color": [92, 103, 196, 255],
            "style": "esriSFSSolid",
            "outline": {
                "type": "esriSLS",
                "color": [178, 178, 178, 255],
                "width": 0.4,
                "style": "esriSLSSolid"
            }
        }




        # Polygon fill color
        polyFillCLR = p.find('sld:CssParameter', attrs={'name': 'fill'})

        if polyFillCLR:
            polyFillCLRrgb = list(ImageColor.getrgb(polyFillCLR.text))
        else:
            polyFillCLRrgb = [0,0,0]

        # PolygonColor Opacity
        polyFillCLROpac = p.find('sld:CssParameter', attrs={'name': 'fill-opacity'})
        if polyFillCLROpac:
            polyFillOpacFLT = float(polyFillCLROpac[0].text)
            polyFillOpacFLTCNV1 = polyFillOpacFLT * 100
            polyFillOpacFLTCNV2 = polyFillOpacFLTCNV1 * 255
            polyFillOpac = round(polyFillOpacFLTCNV2 / 100)
        else:
            polyFillOpac = 255


        polyFillCLRrgb.append(polyFillOpac)


        # Polygon outline color
        outLineCLR = p.find('sld:CssParameter', attrs={'name': 'stroke'})
        outLineCLRrgb = list(ImageColor.getrgb(outLineCLR.text))
        outLineCLRrgb.append(255)

        # Polygon outline width
        outLineWidth = p.find('sld:CssParameter', attrs={'name': 'stroke-width'})
        outLineWidthVal = outLineWidth.text

        # replace the width on the symbol
        simpFillSymbol['outline']['width'] = float(outLineWidthVal)



        fill = {
            'type': "esriSFS",
            'outline': {'style': "esriSLSSolid", 'color': [245, 163, 163, 255]},
            'color': [252, 162, 5, 255]
        }

        # replace the fill
        simpFillSymbol['color'] = polyFillCLRrgb

        # replace the outline Color
        simpFillSymbol['outline']['color'] = outLineCLRrgb


        unqVal = {
        "value":'San',
        "label": 'San',
        "symbol":simpFillSymbol}

        # Replace the unique value populate value and Label
        #if p.Name is None:
        if p.find('ogc:Literal') is None:
            unqVal['value'] = ' '
            unqVal['label'] = ' '
        else:
            unqVal['value'] = p.find('ogc:Literal').text
            unqVal['label'] = p.find('ogc:Literal').text
        #else:
            #unqVal['value']=p.Name.text
            #unqVal['label'] = p.Name.text


        uniqueValueInfos.append(unqVal)

    uniqueRenderer = {
         "type": "uniqueValue",
         "field1": unqField,
        "uniqueValueInfos":uniqueValueInfos
    }

    #uniqueRenderer["uniqueValueInfos"] = uniqueValueInfos"defaultSymbol": simpFillSymbol,
         #"defaultLabel": "Other",

    return uniqueRenderer




def processPolygonSymbol(stylFile):



    styURL = stylFile


    styReq = urllib.request.urlopen(styURL)
    data = styReq.read()

    text = data.decode('utf-8')

    if 'ISO-8859-1' in text:
        soup = BeautifulSoup(data,'xml', from_encoding="ISO-8859-1")
    else:
        soup = BeautifulSoup(text, 'xml')

    #soup = BeautifulSoup(text, 'xml')

    # Track the renderer type
    renType = ''

    # Variable to return the polygon renderer to main thread
    retPolygonRenderer = ''


    if soup.find_all('ogc:PropertyIsEqualTo'):
        renType = 'unique'
        unqRules = soup.find_all('sld:Rule')

        #Dictionary of field and unique values
        retPolygonRenderer = convertUnqValues(unqRules,soup)

    elif soup.find_all(['ogc:PropertyIsLessThan','ogc:PPropertyIsGreaterThan','ogc:PropertyIsLessThanOrEqualTo','ogc:PropertyIsGreaterThanOrEqualTo','ogc:PropertyIsBetween']):
        renType = 'classbreaks'
        clsRules = soup.find_all('sld:Rule')

        # Dictionary of field and unique values
        retPolygonRenderer = convertClassBrksValues(clsRules, soup)

    else:
        renType = 'single'
        polyRule = soup.find('sld:Rule')
        retPolygonRenderer = convertSingleFillSymbol(polyRule)

    return [retPolygonRenderer, renType]







