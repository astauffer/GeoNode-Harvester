import urllib
from PIL import ImageColor

from bs4 import BeautifulSoup


sldToEsriMrkStyle = {
    "circle":"esriSMSCircle",
    "square":"esriSMSSquare",
    "triangle":"esriSMSTriangle",
    "cross":"esriSMSCross",
    "star":"esriSMSDiamond",
    "x":"esriSMSX"
}




defaultSymbol = {
            'type': 'esriSMS',
            'style': "esriSMSCircle",
            'outline': {'style': "solid", 'color': [133, 110, 64, 1]},
            'size': 4,
            'color': [133, 110, 64, 1]
        }


def convertSingleSymbol(pntRule):

    marker = {
        "type": "esriSMS",
        "angle":0,
        "outline":{"color":[100, 125, 100, 255],"width":.9975},
        "size":15,
        "style":"esriSMSCircle",
    }




    # opacity
    pntOpacElem = pntRule.find('sld:Opacity')
    if pntOpacElem:


        pntOpacFLT = float(pntOpacElem.text)
        pntOpacFLTCNV1 = pntOpacFLT * 100
        pntOpacFLTCNV2 = pntOpacFLTCNV1 * 255
        pntOpac = round(pntOpacFLTCNV2 / 100)
    else:
        pntOpac = 255

    # Point inside color
    pntFillCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
    pntGrphicFill = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
    if len(pntFillCLR) == 1:
        pntCLRrgb = list(ImageColor.getrgb(pntFillCLR[0].text))
        pntCLRrgb.append(pntOpac)
    else:
        pntCLRrgb = [255, 0, 0, pntOpac]

    # Point outline color
    pntOutLnCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'stroke'})

    if len(pntOutLnCLR) == 1:
        pntOutLnCLRrgb = list(ImageColor.getrgb(pntOutLnCLR[0].text))
        pntOutLnCLRrgb.append(pntOpac)

        # replace the outline Color
        marker['outline']['color'] = pntOutLnCLRrgb
    else:
        marker.pop('outline')

    # Point type
    agPntStyle = ''
    pntStyleType = pntRule.find_all('sld:WellKnownName')
    if len(pntStyleType) == 1:
        pntStyle = pntStyleType[0].text
        agPntStyle = sldToEsriMrkStyle[pntStyle]
    else:
        agPntStyle = 'esriSMSSquare'

    # Point Size
    pntSizeElem = pntRule.find('sld:Size')
    if pntSizeElem:
        pntSize = int(float(pntSizeElem.text.strip()))
    else:
        pntSize = 6

    # Rotation
    pntRotate = 0
    pntRotElem = pntRule.find('sld:Rotation')
    if pntRotElem:
        pntRotate = int(pntRotElem.text)

    # replace the style
    marker['style'] = agPntStyle

    # replace the size
    marker['size'] = pntSize

    # replace the fill
    marker['color'] = pntCLRrgb

    # Check and add Rotation if needed
    if pntRotate != 0:
        marker['angle'] = pntRotate



    simplePntRenderer = {
        "type": "simple",
        "symbol": marker
    }

    return simplePntRenderer

def convertClassBrksValues(lnRules,parseSoup):


    clsField = parseSoup.find('ogc:PropertyName').text


    clsBreaksRen = {
        "type": "class-breaks",
        "field": clsField
    }

    clsBreaksRenBrkInfo = []


    clsDefaultSymbol = {"type": "simple-line", "color": [66, 60, 60, 1]};

    for pntRule in parseSoup.find_all('sld:Rule'):

        pntBrkInfo = {}

        # Find the low Range Value
        minValue = float(pntRule.find_all('ogc:LowerBoundary')[0].find('Literal').text)

        # Find the max Range Value
        maxValue = float(pntRule.find_all('ogc:UpperBoundary')[0].find('Literal').text)

        pntBrkInfo["minValue"] = minValue
        pntBrkInfo["maxValue"] = maxValue

        # opacity
        pntOpacElem = pntRule.find('sld:Opacity')
        if pntOpacElem:
            pntOpacFLT = float(pntOpacElem.text)
            pntOpacFLTCNV1 = pntOpacFLT * 100
            pntOpacFLTCNV2 = pntOpacFLTCNV1 * 255
            pntOpac = round(pntOpacFLTCNV2 / 100)
        else:
            pntOpac = 255

        # Point inside color
        pntFillCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
        pntGrphicFill = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
        if len(pntFillCLR) == 1:
            pntCLRrgb = list(ImageColor.getrgb(pntFillCLR[0].text))
            pntCLRrgb.append(pntOpac)
        else:
            pntCLRrgb = [255, 0, 0, pntOpac]

        # Point outline color
        pntOutLnCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'stroke'})

        if len(pntOutLnCLR) == 1:
            pntOutLnCLRrgb = list(ImageColor.getrgb(pntOutLnCLR[0].text))
            pntOutLnCLRrgb.append(pntOpac)

            # replace the outline Color
            pntBrkInfo['symbol']['outline']['color'] = pntOutLnCLRrgb
        else:
            pntBrkInfo['symbol'].pop('outline')

        # Point type
        agPntStyle = ''
        pntStyleType = pntRule.find_all('sld:WellKnownName')
        if len(pntStyleType) == 1:
            pntStyle = pntStyleType[0].text
            agPntStyle = pntStyle
        else:
            agPntStyle = 'esriSMSSquare'

        # Point Size
        pntSizeElem = pntRule.find('sld:Size')
        if pntSizeElem:
            pntSize = int(float(pntSizeElem.text.strip()))
        else:
            pntSize = 6

        # Rotation
        pntRotate = 0
        pntRotElem = pntRule.find('sld:Rotation')
        if pntRotElem:
            pntRotate = int(pntRotElem.text)

        # replace the style
        pntBrkInfo['symbol']['style'] = agPntStyle

        # replace the size
        pntBrkInfo['symbol']['size'] = pntSize

        # replace the fill
        pntBrkInfo['symbol']['color'] = pntCLRrgb

        # Check and add Rotation if needed
        if pntRotate != 0:
            pntBrkInfo['angle'] = pntRotate

        clsBreaksRenBrkInfo.append(pntBrkInfo)

    clsBreaksRen["minValue"] = float(pntRule.find_all('ogc:LowerBoundary')[0].find('Literal').text)
    clsBreaksRen["classBreakInfos"] = clsBreaksRenBrkInfo

    return clsBreaksRen


def convertUnqValues(lnRules,parseSoup):

    unqValueInfosDict = {}





    # Collect the unique value infos
    uniqueValueInfos = []

    # Find the rules to get the unique values
    unqField = parseSoup.find('ogc:PropertyName').text

    unqValueInfosDict['uniqueField'] = unqField

    for pntRule in lnRules:

        marker = {
            "value": '',
            "type": 'esriSMS',
            "symbol": {
                "style":'',
                'size':'8',
                'color':''
                }}


        # Test for a unique Value
        if pntRule.find('ogc:PropertyIsEqualTo'):
            print('has a val')
            marker["value"] = pntRule.find('ogc:PropertyIsEqualTo').find('Literal').text

            # opacity
            pntOpacElem = pntRule.find('sld:Opacity')
            if pntOpacElem:
                pntOpacFLT = float(pntOpacElem.text)
                pntOpacFLTCNV1 = pntOpacFLT * 100
                pntOpacFLTCNV2 = pntOpacFLTCNV1 * 255
                pntOpac = round(pntOpacFLTCNV2 / 100)
            else:
                pntOpac = 255

            # Point inside color
            pntFillCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
            pntGrphicFill = pntRule.find_all('sld:CssParameter', attrs={'name': 'fill'})
            if len(pntFillCLR) == 1:
                pntCLRrgb = list(ImageColor.getrgb(pntFillCLR[0].text))
                pntCLRrgb.append(pntOpac)
            else:
                pntCLRrgb = [255, 0, 0, pntOpac]

            # Point outline color
            pntOutLnCLR = pntRule.find_all('sld:CssParameter', attrs={'name': 'stroke'})

            if len(pntOutLnCLR) == 1:
                pntOutLnCLRrgb = list(ImageColor.getrgb(pntOutLnCLR[0].text))
                pntOutLnCLRrgb.append(pntOpac)

                # replace the outline Color
                marker['symbol']['outline']['color'] = pntOutLnCLRrgb
            #else:
                #marker['symbol'].pop('outline')

            # Point type
            agPntStyle = ''
            pntStyleType = pntRule.find_all('sld:WellKnownName')
            if len(pntStyleType) == 1:
                pntStyle = pntStyleType[0].text
                agPntStyle = pntStyle
            else:
                agPntStyle = 'esriSMSSquare'

            # Point Size
            pntSizeElem = pntRule.find('sld:Size')
            if pntSizeElem:
                pntSize = int(float(pntSizeElem.text.strip()))
            else:
                pntSize = 6

            # Rotation
            pntRotate = 0
            pntRotElem = pntRule.find('sld:Rotation')
            if pntRotElem:
                pntRotate = int(pntRotElem.text)

            # replace the style
            marker['symbol']['style'] = agPntStyle

            # replace the size
            marker['symbol']['size'] = pntSize

            # replace the fill
            marker['symbol']['color'] = pntCLRrgb

            # Check and add Rotation if needed
            if pntRotate != 0:
                marker['angle'] = pntRotate


            uniqueValueInfos.append(marker)
    #"defaultSymbol": defaultSymbol,

    unqPntValRenderer = {
        "type":"unique-value",

        "uniqueValueInfos":uniqueValueInfos
    }

    return  unqPntValRenderer


def processPointSymbol(stylFile):


    renType = ''


    styURL = stylFile


    styReq = urllib.request.urlopen(styURL)
    data = styReq.read()
    # decode the reponse based on the character set
    text = data.decode(styReq.headers.get_content_charset())#'utf-8')


    if 'ISO-8859-1' in text:
        soup = BeautifulSoup(data,'xml', from_encoding="ISO-8859-1")
    else:
        soup = BeautifulSoup(text, 'xml')




    # ArcGIS Simple Symbol map
    agsSimpleStyle = {}

    pntTypeTest = soup.find('sld:Rule')

    pntRules = soup.find_all('sld:Rule')

    # Variable to return the polygon renderer to main thread
    retPointRenderer = ''


        # If mark is found then it is not a picture marker symbol
    if pntTypeTest.find('Mark'):


            # Test for a unique Value
            if pntTypeTest.find('ogc:PropertyIsEqualTo'):

                # Returned UniqueValue Point Renderer
                retPointRenderer = convertUnqValues(pntRules, soup)

                renType = 'unique'

            # Test for a unique Value
            elif pntTypeTest.find('ogc:PropertyIsBetween'):
                print('has a val')

                renType = 'classbreaks'

                retPointRenderer = convertClassBrksValues(pntRules,soup)

            else:
                renType = 'single'
                pntStyle = soup.find('sld:FeatureTypeStyle')
                retPointRenderer = convertSingleSymbol(pntStyle)



    return [retPointRenderer,renType]




