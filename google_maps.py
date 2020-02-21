# Built-in modules
import requests
import time
from math import cos, asin, sqrt

# Third-party modules
from bs4 import BeautifulSoup

# Local modules
import settings

logger = settings.get_logger(__name__)

# Google Maps API Key is inputted from settings here
gmap_key = settings.GMAPYKEY

subway_coordinates = {
    'vaughan': (43.778046, -79.512089), '407': (43.782804, -79.523748),
    'pioneer_village': (43.777386, -79.510318), 'york_university': (43.774149, -79.499784),
    'finch_west': (43.765311, -79.491108), 'downsview_park': (43.755842, -79.479199),
    'sheppard_west': (43.751502, -79.462204), 'wilson': (43.734699, -79.450152),
    'yorkdale': (43.724786, -79.447516), 'lawrence_west': (43.716420, -79.444452),
    'glencairn': (43.709616, -79.441158), 'eglinton_west': (43.699572, -79.436179),
    'st_clair_west': (43.684383, -79.415433), 'dupont': (43.675034, -79.407049),
    'spadina': (43.667570, -79.403845), 'st_george': (43.668460, -79.399758),
    'bay': (43.670341, -79.390684), 'bloor_yonge': (43.671061, -79.385616),
    'sherbourne': (43.672400, -79.376378), 'castle_frank': (43.673814, -79.368787),
    'broadview': (43.677195, -79.358387), 'chester': (43.678453, -79.352433),
    'pape': (43.680249, -79.344640), 'donlands': (43.681213, -79.337723),
    'greenwood': (43.682699, -79.330374), 'coxwell': (43.684368, -79.323120),
    'woodbine': (43.686650, -79.312459), 'main_street': (43.689215, -79.301915),
    'bathurst': (43.666678, -79.411296), 'christie': (43.664303, -79.418412),
    'ossington': (43.662623, -79.426189), 'dufferin': (43.660460, -79.435538),
    'lansdowne': (43.659297, -79.442790), 'dundas_west': (43.657103, -79.453130),
    'keele': (43.655583, -79.459829), 'high_park': (43.654033, -79.466807)
}


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))


def closest(v):
    data = []
    for coord in subway_coordinates:
        data += [{'lat': subway_coordinates[coord][0], 'lon': subway_coordinates[coord][1]}]
    d = min(data, key=lambda p: distance(float(v['lat']), float(v['lon']), p['lat'], p['lon']))
    value = (d['lat'], d['lon'])
    return [k for k, v in subway_coordinates.items() if v == value]


def get_address(link):
    try:
        with requests.session() as r:
            soup = BeautifulSoup(r.get(link).content, 'lxml')
            try:
                address = soup.find(id='ctl00_ContentPlaceHolder1_lbNameAddress').text.rstrip().\
                    split(': ', 1)[-1].replace(' ', '+')
            except AttributeError:
                logger.info('No precise address was given, instead generic address will be used.')
                address = soup.find('h1').text.strip().replace('-', ' at ').split(':', 1)[-1].replace(' ', '+')
            url_google = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}' \
                         f'+Toronto+Ontario+Canada&key={gmap_key}'
            page_google = r.get(url_google).json()
            coords = {'lat': str(page_google['results'][0]['geometry']['location']['lat']),
                      'lon': str(page_google['results'][0]['geometry']['location']['lng'])}
            subway = closest(coords)
            walk_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={coords["lat"]},' \
                       f'{coords["lon"]}&destinations={str(subway_coordinates[subway[0]][0])},' \
                       f'{str(subway_coordinates[subway[0]][1])}&mode=walking&key={gmap_key}.'
            page_walk = r.get(walk_url).json()
            kms = (page_walk['rows'][0]['elements'][0]['distance']['value'])/1000
            duration = (page_walk['rows'][0]['elements'][0]['duration']['value'])/60
            commute_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={coords["lat"]},' \
                          f'{coords["lon"]}&destinations={settings.COMMUTE_LAT_LON[0]},' \
                          f'{settings.COMMUTE_LAT_LON[1]}&mode=transit&transit_mode=subway&key={gmap_key}.'
            page_commute = r.get(commute_url).json()
            commute_duration = page_commute['rows'][0]['elements'][0]['duration']['value']/60
            return [subway[0], round(kms, 2), round(duration, 2), round(commute_duration, 2), address.replace('+', ' ')]
    except KeyError:
        logger.info('#################################################################################')
        logger.info('Rate limited by google, waiting 100 seconds before retrying.')
        logger.info('#################################################################################')
        time.sleep(100)


if __name__ == '__main__':
    link_main = 'https://classic.viewit.ca/vwExpandView.aspx?ViT=25078'
    # print(get_address(link_main))
