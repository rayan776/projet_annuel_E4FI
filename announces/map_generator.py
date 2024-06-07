import math
import folium
import ast
from datetime import datetime

class MapGenerator:

    DEFAULT_ZOOM = 2

    def __init__(self):
        pass

    def generate_map(self, context, request, announcesToShow):
        context["nb_announces"] = len(announcesToShow['announces'])
        zoom = self.DEFAULT_ZOOM
        if announcesToShow['radius'] > 0:
            zoom = math.ceil( (7 - ((announcesToShow['radius']-10) * (6.0/490.0))) * 1.3 )

        map = folium.Map(location=[announcesToShow['starting_lat'], announcesToShow['starting_lon']], zoom_start = zoom)

        for announce in announcesToShow['announces']:
            announce_popup = self.generate_popup(announce)
            folium.Marker(location=[announce['latitude'], announce['longitude']], icon=self.choose_icon(announce), popup=announce_popup).add_to(map)

        # une fois que la map est construite, conversion en HTML
        map = map._repr_html_
        context["map"] = map
        
    def generate_popup(self, announce):
        localisationDict = announce['localisation']
        popupHtml = f"""
        <div style="text-align:center; width:200px">
        <a 
        style="font-size:15px !important; 
        "
        href="http://127.0.0.1:8000/announces/viewAnnounce/{announce['idAnnounce']}"
        target="_blank">{announce['intitule']}
        </a>
        <div style="font-weight:bold"> {announce['catName']}</div>
        <div>{datetime.strptime(str(announce['dateAnnounce']), "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y")}</div>
        <div> {localisationDict.get("city", localisationDict.get("town", localisationDict.get("village")))}, {localisationDict['state']}, {localisationDict['country']} </div>
        <div>Par {announce['username']} ({announce['lastname']} {announce['firstname']})</div>
        </div>"""
        return folium.Popup(popupHtml)


    def choose_icon(self, announce):
        marker_icon = folium.Icon()

        if (announce['valid'] == 0):
            # icône pour les annonces pas encore approuvées
            marker_icon = folium.Icon(color='red')
        else:
            # icône pour les annonces approuvées
            if (announce['typeAnnounce'] == 1):
                # annonce de type "je propose"
                marker_icon = folium.Icon(color='blue')
            else:
                # annonce de type "je recherche"
                marker_icon = folium.Icon(color='green')
        
        return marker_icon