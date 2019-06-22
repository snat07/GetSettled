from ipywidgets import HTML
from ipyleaflet import Map, Marker, Popup, Icon
import telluric as tl
from telluric.plotting import plot
from Utils import alias_dictionary, alias_list
import random

def draw_map(neighborhoods, points, location, title):
    fc = tl.FileCollection.open("../barris_geo.json")
    geo_alias = alias_dictionary(neighborhoods,list(fc.get_values("N_Barri")))
    fc = tl.FeatureCollection(barri for barri in fc if barri['N_Barri'] in alias_list(geo_alias))

    fc_points = tl.FeatureCollection.from_geovectors([tl.GeoVector.point(*coords) for coords in points])
    mp = fc_points.plot()
    mp.close_popup_on_click=False
    fc.plot(mp=mp, style_function=style_func);

    for idx, val in enumerate(neighborhoods):
        message = HTML(fc[idx].get('N_Barri'))
        center = (fc[idx].centroid.y, fc[idx].centroid.x)
        popup = Popup(
            location=center,
            child=message,
            close_button=False,
            auto_close=False,
            close_on_escape_key=False,
            keep_in_view=True,
        )
        mp.add_layer(popup)
    icon = Icon(icon_url='http://icons.iconarchive.com/icons/google/noto-emoji-travel-places/32/42496-school-icon.png', 
            icon_size=[20, 20])
    marker = Marker(location=(location[1],location[0]),icon=icon, draggable=False)
    address = HTML()
    address.value = title
    marker.popup = address
    mp.add_layer(marker)
    return mp

def style_func(gjson):
    r = lambda: random.randint(0,255)
    color = '#%02X%02X%02X' % (r(),r(),r())
    return {"color": color}