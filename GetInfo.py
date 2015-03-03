#-------------------------------------------------------------------------------
# Name:        zeeshan.py
# Purpose:     Context Based Image Search
#
# Author:      Akkas Uddin Haque
#
# Created:     24/02/2015
# Copyright:   (c) akkasuddin 2015
# Licence:     Public Domain
#-------------------------------------------------------------------------------
from __future__ import print_function
from alchemyapi import AlchemyAPI
import json
import sys
# Create the AlchemyAPI Object
alchemyapi = AlchemyAPI()

def getInfoFromImage(path):
    response = alchemyapi.faceDetection('image',path)#sys.argv[1]) #'C:/Users/au.haque/Desktop/url.jpg')
    #print(json.dumps(response, indent=4))
    buff = []

    if response['status'] == 'OK':
    #    writeBuffer = ''


        for person in response['imageFaces']:
            buf = {}
            buf['Gender'] = str(person['gender']['gender']).lower()
            buf['Position'] = ( int(person['positionX']) , int(person['positionY']))
            buf['Size'] = (int(person['width']) , int(person['height']))
            buf['Age'] = str(person['age']['ageRange'])

            if person.has_key('identity'):
                identity =  person['identity']
                buf['Name'] = identity['name']
                buf['Professions'] = []
                buf['Info'] = ' '
                if(identity.has_key('disambiguated')):
                    for profession in identity['disambiguated']['subType'][1:]:
                        buf['Professions'].append(profession)

                    if identity['disambiguated'].has_key('dbpedia'):
                        buf['Info'] = identity['disambiguated']['dbpedia']

            buff.append(buf)
    else:
        return None
    return buff



#if __name__ == '__main__':
 #   main()
