import gpxpy
import gpxpy.gpx
import time
import simplekml

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# ...................................................
# Where do I find my utils to be imported? Set your path here!
sys.path.append("C:\\SynologyDrive\\Python\\00_import_h_utils")
import h_utils                                                              # type: ignore
# I wasn't able to find the error in my compile, but as long as I don't add the same 
# imports as in utils, the exe breaks with an import error.
# Duplicate imports from uitls.py:
# from pathlib import Path
# import json
# import gpxpy
# import sys
# from tkinter import *
# from tkinter import ttk
# from ttkthemes import ThemedTk
# import xml.etree.ElementTree as ET
# ...................................................



# ------------------------------------------------------------------------------------------
#  _____ _ _                _   _                 _ _ _             
# |  ___(_) | ___          | | | | __ _ _ __   __| | (_)_ __   __ _ 
# | |_  | | |/ _ \  _____  | |_| |/ _` | '_ \ / _` | | | '_ \ / _` |
# |  _| | | |  __/ |_____| |  _  | (_| | | | | (_| | | | | | | (_| |
# |_|   |_|_|\___|         |_| |_|\__,_|_| |_|\__,_|_|_|_| |_|\__, |
#                                                             |___/ 
# ------------------------------------------------------------------------------------------
def make_gpx_name(gpx_in_file_name):
# ...................................................
# Make GPX FileName
# 2022 12 06
# ...................................................
    '''
    Make a valid GPX name

    ### Args: 
    - Input  : GPX File Name to be analyzed
    - Returns: GPX File Name to be used. May be blank
    '''
    if gpx_in_file_name:
        in_path = Path(gpx_in_file_name).parent     # Der Pfad zur EingabeDatei
        in_name = Path(gpx_in_file_name).stem       # Der Name der Datei ohne Suffix
        in_suffix = Path(gpx_in_file_name).suffix    
        if in_suffix.lower() != '.gpx':         # Prüfe ob das richtige Datenformat eingegeben wurde
            # in_name = ""                            # Wenn falsch, dann kein EingabeName
            # in_suffix = ""                          # Wenn falsch, dann kein EingabeName
            # in_path = my_path                        # Setze den Pfad dieses Programms als Default
            gpx_file_name = ''
        else:
            gpx_file_name = str(in_path) + '\\' + str(in_name) + str(in_suffix)
    else:
        gpx_file_name = ''

    return gpx_file_name

def make_kml_name(gpx_in_file_name ):
# ...................................................
# Make KML FileName
# 2022 12 06
# ...................................................
    '''
    Make a valid KML name.
    Name, Suffix and Path

    ### Args: 
    - Input  : GPX File Name to be analyzed
    - Returns: KML File Name to be used. May be blank
    '''
    if gpx_in_file_name:
        in_path = Path(gpx_in_file_name).parent    # Der Pfad zur EingabeDatei
        in_name = Path(gpx_in_file_name).stem      # Der Name der Datei ohne Suffix
        in_suffix = '.kml'
        # kml_file_name = str(in_path) + '\\' + str(in_name) + in_suffix
        kml_file_name = str(in_path) + '\\' + str(in_name)      # Ohne Suffix machen. Später werden beim KML schreiben verschiedene KML erzeugt
                                                                # tracks # 1...x und waypoints
    else:
        kml_file_name = ''
    return kml_file_name

# ------------------------------------------------------------------------------------------
#   ____                      _            ____                 _       _ 
#  / ___| __ _ _ __ _ __ ___ (_)_ __      / ___| _ __   ___ ___(_) __ _| |
# | |  _ / _` | '__| '_ ` _ \| | '_ \ ____\___ \| '_ \ / _ \_  / |/ _` | |
# | |_| | (_| | |  | | | | | | | | | |_____|__) | |_) |  __// /| | (_| | |
#  \____|\__,_|_|  |_| |_| |_|_|_| |_|    |____/| .__/ \___/___|_|\__,_|_|
#                                               |_|                       
# ------------------------------------------------------------------------------------------
def read_garmin_DisplayColor(gpx_file_path):
    ''' 
    Ich lese den GPX Track per XML Parser ein, lese die DisplayColors aus und übergebe diese 
    in einer Liste: display_colors
    '''
    # ....................................................
    # Spezialbehandlung für den GPX Track!
    # Ich hole die DisplayColor aus dem GPX Track. GPXPY kann keine Garmin codes lesen! 
    # Die alte Bibliothek gpxdata, obwohl sie eigentlich passen müsste, liess sich nicht mehr nutzen.
    # Ich habe Stunden damit zugebracht die Garmin Struktur ansprechen zu können. NUR dieser Weg ging bislang!
    # Also jede einzelne Elementstruktur in der Tiefe der GPX / XML mit ihrem Namespace ansprechen.
    # So zerlegt sich das: 
    #   <gpx creator="Garmin........                                          = . = root
    #         <trk>                                                           = ./h_main:trk/
    #              <name>Track 005</name>                                      
    #              <extensions>                                               = ./h_main:trk/h_main:extensions
    #                 <gpxx:TrackExtension>                                   = ./h_main:trk/h_main:extensions/h_gpxx:TrackExtension
    #                     <gpxx:DisplayColor>DarkGray</gpxx:DisplayColor>     = ./h_main:trk/h_main:extensions/h_gpxx:TrackExtension/h_gpxx:DisplayColor
    #                 </gpxx:TrackExtension>
    #             </extensions>
    #         <trkseg>....
    #     </gpx>
    # ....................................................
    tree = ET.parse(gpx_file_path)
    root = tree.getroot()
    ns = {'h_main': 'http://www.topografix.com/GPX/1/1' ,
        'h_gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'}
    display_colors = root.findall("./h_main:trk/h_main:extensions/h_gpxx:TrackExtension/h_gpxx:DisplayColor", ns)
    return display_colors







# ------------------------------------------------------------------------------------------
#  _____       _  ____  __ _     
# |_   _|__   | |/ /  \/  | |    
#   | |/ _ \  | ' /| |\/| | |    
#   | | (_) | | . \| |  | | |___ 
#   |_|\___/  |_|\_\_|  |_|_____|
# ------------------------------------------------------------------------------------------
def create_kml_from_gpx(gpx_file_path, kml_file_path):
    '''
    * Based on a GPX file, analyse that on its elements Waypoint and Track.
    * Don't use Routes, as they mainly aren't useful as a Track to follow or an Overlay
    * Load Translation Table as a JSON
    * 
    '''
    mein_gpx = h_utils.mein_gpx(gpx_file_path)
    gpx = mein_gpx.gpx
    display_colors = mein_gpx.display_color

    translate_table = h_utils.load_json(json_file_name)                     # Lade deine eigene Translation Tabelle
    # ...........................................
    #   Loop Tracks and write to kml
    # ...........................................
    i = 0
    a = Path(gpx_file_path).stem
    kml = simplekml.Kml(name="<![CDATA["+a+"]]>", visibility = "1" , open ="1", atomauthor = "Hans Straßgütl" , atomlink = "https://gravelmaps.de"  )     
    if len(gpx.tracks) > 0:     
        # Erstelle einen Tracks Folder sofern ein Track vorhanden ist. Nicht für reine Waypointlisten
        folder = kml.newfolder(name="Tracks")
        for track in gpx.tracks:
            track_line = folder.newlinestring(name=gpx.tracks[i].name)         # Erstelle den Namen im Track im KML
            track_line.altitudemode="relativeToGround"                      # Welches Höhenmodell verwenden wir?
            track_line.description=track.description                        # Beschreibung des Tracks
            # ...........................................
            # Jetzt kommen die LineStyle Parameter.
            # display_colors kommen aus der GPX Sonderbehandlung und sind in einer adressierbaren Liste
            # Ich muss nun fragen, ob die GPX TrackFarbe als Farbe in der JSON auffindbar ist. Gleiches gilt für die Breite.
            # Wenn nicht, dann setzte die Defaultwerte
            # ...........................................
            try:
                linestyle_para = my_track_color_dict[display_colors[i].text]    # Das Dict wurde ganz am Anfang im Programm aus der JSON Steuerdatei erstellt
            except:
                linestyle_para = my_track_color_dict['Default']    # Das Dict wurde ganz am Amfang im Programm aus der JSON Steuerdatei erstellt
                print('---------------------------------------------------------------------------------------------')
                try:
                    print('               Line Color used in GPX not found in translation table: '+ str(display_colors[i].text))
                except:
                    print('               Line Color not used in GPX')
                print('               Default value used')
                print('---------------------------------------------------------------------------------------------\n\n')

            track_line.style.linestyle.color=linestyle_para
            try:
                linestyle_para = my_track_width_dict[display_colors[i].text]
            except:
                linestyle_para = my_track_width_dict['Default']
            track_line.style.linestyle.width=linestyle_para

            for track_segment in gpx.tracks[i].segments:
                for point in track_segment.points:
                    # Füge die Koordinaten zu der Linie hinzu
                    track_line.coords.addcoordinates([(point.longitude, point.latitude)])
            i = i+1
        
    # ...........................................
    #   Loop Waypoints and write to kml
    # ...........................................
    # Sofern es Wegpunkte gibt, mache die Sektion dafür
    if len(gpx.waypoints) > 0:     
        my_point_symbol_dict = translate_table.get("points")
        folder = kml.newfolder(name="Waypoints")
        for waypoint in gpx.waypoints:
            # If the waypoint.symbol can be found in the Json Table for Waypoints then get the Waypoint reference for the pin
            try:
                href_address = my_path_to_icon + (my_point_symbol_dict[waypoint.symbol])
            # if the waypoint.symbol can NOT be found in the Json Table, find the href for the default value
            except:
                href_address = my_path_to_icon + (my_point_symbol_dict["Default"])
                print('---------------------------------------------------------------------------------------------')
                print('               GPX Symbol used but not found in translation table: '+ str(waypoint.symbol))
                print('               Default value used')
                # print('---------------------------------------------------------------------------------------------\n\n')
            # Bereite den Waypoint als KML auf
            if waypoint.elevation == None : waypoint.elevation = 0    # Manche Waypoints haben Höhe, manche nicht.
            pt2 = folder.newpoint(name='<![CDATA[' + waypoint.name + ']]>' , coords=[(waypoint.longitude,waypoint.latitude,waypoint.elevation)])
            if waypoint.description and waypoint.link :
                pt2.description = '<![CDATA[<p align="left"><font size="+1">' + waypoint.description + '</p> <p>' + waypoint.link + '</p>]]>'
            if waypoint.description and not waypoint.link :
                pt2.description = '<![CDATA[<p align="left"><font size="+1">' + waypoint.description + '</p>]]>'
            if waypoint.link and not waypoint.description :
                pt2.description = '<![CDATA[<p align="left"><font size="+1">'  + waypoint.link + '</p>]]>'
            
            # if waypoint.link : pt2 = waypoint.folder.newpoint(name='<![CDATA[' + waypoint.name + ']]>' , coords=[(waypoint.longitude,waypoint.latitude,waypoint.elevation)], description='<![CDATA[<p align="left"><font size="+1">' + waypoint.description + '</p> <p>' + waypoint.link + '</p>]]>')
            # else:
                # pt2 = folder.newpoint(name='<![CDATA[' + waypoint.name + ']]>' , coords=[(waypoint.longitude,waypoint.latitude,waypoint.elevation)], description='<![CDATA[<p align="left"><font size="+1">' + waypoint.description + ']]>')
            pt2.altitudemode='absolute'
            pt2.style.iconstyle.icon.href = href_address
            pt2.style.iconstyle.color ='FFFFFFFF' 
            pt2.style.iconstyle.scale ='3' 
            pt2.balloonstyle.text= '<![CDATA[<p align="left"><font size="+1"><b>$[name]</b></font></p> <p align="left">$[description]</p>]]>'
            pt2.labelstyle.color='FFFFFFFF'

    # ...........................................
    # Schreibe die KML raus
    # ...........................................
    kml.save(kml_file_path+".kml")

# ------------------------------------------------------------------------------------------
#  __  __       _       
# |  \/  | __ _(_)_ __  
# | |\/| |/ _` | | '_ \ 
# | |  | | (_| | | | | |
# |_|  |_|\__,_|_|_| |_|
# ------------------------------------------------------------------------------------------
if __name__ == "__main__":
    global gpx_file_name
    global kml_file_name
    global json_file_name
    global my_track_color_dict, default_line_color, my_track_width_dict

    # ....................................................
    # Erhalte die Übergabeparameter. Erstelle dazu den 
    # default GPX Entry - sofern übergeben.
    # Ansonsten setze Default Pfad auf den Pfad der Exe
    # ....................................................
    os.system('cls') 
    my_script = h_utils.IchSelbst()

    file_paths = sys.argv[1:]                   # the first argument (0) is the script itself. 1: heisst, wir haben nun in der file_paths alle anderen Argumente
    print("\n\n  GPX_2_KML_4_Orux - convert Garmin GPX into KML for OruxMaps\n  Version v2.0 dated 11/2024\n  Written by Hans Strassguetl - https://gravelmaps.de \n  Licenced under 'Licenced under https://creativecommons.org/licenses/by-sa/4.0/ \n  Icons used are licensed under\n    Map Icons Collection\n    Creative Commons 3.0 BY-SA\n    Author: Nicolas Mollet - https://mapicons.mapsmarker.com")

    # Make sure you have either set a valid GPX / KML name 
    # or make sure its clear
    # ....................................................
    mein_gpx = h_utils.mein_gpx(None)
    gpx_file_name = mein_gpx.gpx_name_with_path

    if gpx_file_name:
        kml_file_name = make_kml_name(gpx_file_name)
        json_file_name = my_script.path_name_without_suffix+".json"
        # print(json_file_name)
    else:
        gpx_file_name = ''
        kml_file_name = ''
        json_file_name = ''
        h_utils.error_message("gpx_02",True)

    translate_table = h_utils.load_json(json_file_name)
    my_track_color_dict = translate_table.get("trackcolor")         # Erhalte ein Dictionary mit allen Farbein im Format  "Magenta": "FFFE01FE"

    # default_line_color = my_track_color_dict.get("Default")         # Wenn keine Farbe gefunden werden kann, dann heisst der Farbname Default und ich hole die Farbe
    my_track_width_dict = translate_table.get("trackwidth")         # Erhalte wie bei den Farben ein Dict mit den TrackBreiten: "Magenta": "10"

    my_path_to_icon = "http://motorradtouren.de/pins/"

create_kml_from_gpx(gpx_file_name,kml_file_name)
print('\n  Done!\n  You should now find one or more KML within the same folder and with the same name as the calling GPX.\n  Program closes.\n\n')
time.sleep(2) # Seconds