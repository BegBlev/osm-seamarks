import re
import json
from dataclasses import dataclass
from geopy import distance
import json

__ALADIN__ = True

SHOM_FILE="json-db/beacon-cardinal.json"

__COLOURS__ = {
    "1": "white",
    "2": "black",
    "3": "red",
    "4": "green",
    "5": "blue",
    "6": "yellow",
    "7": "grey",
    "11": "orange",
}

__COLOUR_PATTERNS__ = {
    "1": "horizontal",
    "2": "vertical",
    "3": "diagonal",
}

__CATCAM__ = {
    "1": "north",
    "2": "east",
    "3": "south",
    "4": "west",
}

__CATLAM__ = {
    "1": "port",
    "2": "starboard",
    "3": "preferred_channel_starboard",
    "4": "preferred_channel_port",
}

def __colours2txt__(colours):
    colourtxt = ""

    for colour in colours.split(","):
        if colourtxt != "":
            colourtxt += ";"

        colourtxt += __COLOURS__[colour]

    return colourtxt


class SHOMSeamarkList(list):
    def __init__(self, seamarks):
            super().__init__(seamarks)

    @classmethod
    def from_file(cls, filename):
        # SHOM json file
        with open(filename, 'r') as shomfile:
            shom_seamarks = json.load(shomfile)

            return cls(SHOMSeamark(seamark) for seamark in shom_seamarks)

    def filter(self, lat, lon, dist):
        return SHOMSeamarkList(seamark for seamark in self if distance.distance((seamark.lat, seamark.lon), (lat, lon)).meters < dist)


@dataclass
class SHOMDescription:
    """Class for SHOM description"""
    def __init__(self, description):
        self.description = description
        self.attributes = {}

        for raw_attribute in self.description.split(";"):
            attribute = raw_attribute.strip()
            attribute_key = attribute[:6]
            attribute_value = attribute[8:]
            self.attributes.update({attribute_key: attribute_value})

    def validate(self):
        if "BCNCAR" in self.attributes.keys():
            # This is a cardinal beacon
            if "CATCAM" in self.attributes.keys():
                if self.attributes["CATCAM"] not in ["1", "2", "3", "4"]:
                    print(f"CATCAM :{self.attributes["CATCAM"]}, should be in 1, 2, 3, 4")
            else:
                print("This is a cardinal beacon, CATCAM should be defined")
        else:
            pass

        if "COLOUR" in self.attributes.keys():
            if "CATCAM" in self.attributes.keys():
                if (((self.attributes["CATCAM"] == "1") and (self.attributes["COLOUR"] == "2,6")) or
                    ((self.attributes["CATCAM"] == "2") and (self.attributes["COLOUR"] == "2,6,2")) or
                    ((self.attributes["CATCAM"] == "3") and (self.attributes["COLOUR"] == "6,2")) or
                    ((self.attributes["CATCAM"] == "4") and (self.attributes["COLOUR"] == "6,2,6"))
                   ):
                    # COLOUR is coherent with CATCAM
                    pass
                else:
                    print("CATCAM is not coherent with COLOUR")
                    print(self.attributes)

        #print(self.attributes)


@dataclass
class SHOMSeamark:
    """Class for SHOM seamark"""
    id: str
    aladin_id: str
    lat: float
    lon: float
    type: str
    category: str
    data: SHOMDescription
    height: float = None
    colour: str = None
    colour_pattern: str = None

    def __init__(self, shom_data):
        assert(re.match("BALISAGE_FR[0-9]{15}", shom_data["@gml:id"]))

        self.id = shom_data["@gml:id"].removeprefix("BALISAGE_")
        lat, lon = shom_data["tn:geometry"]["gml:Point"]["gml:pos"].split(" ")

        self.lat = float(lat)
        self.lon = float(lon)

        self.data = SHOMDescription(shom_data["gml:description"])

        if "numald" in self.data.attributes:
            if self.data.attributes["numald"] != '':
                self.aladin_id = self.data.attributes["numald"]

        if shom_data["type"] in ["beacon", "buoy"]:
            if "CATCAM" in self.data.attributes:
                # This is a cardinal seamark
                if shom_data["type"] == "beacon" and self.data.attributes["CATCAM"] in ["1", "2", "3", "4"]:
                    self.type = "beacon_cardinal"
                elif shom_data["type"] == "buoy" and self.data.attributes["CATCAM"] in ["1", "2", "3", "4"]:
                    self.type = "buoy_cardinal"
                else:
                    raise ValueError(f'Combination of seamark type ({shom_data["type"]}) and category ({self.data.attributes["CATCAM"]}) is not allowed for cardinal.')

                self.category = __CATCAM__[self.data.attributes["CATCAM"]]

            elif "CATLAM" in self.data.attributes:
                # This is a lateral seamark
                if shom_data["type"] == "beacon" and self.data.attributes["CATLAM"] in ["1", "2", "3", "4"]:
                    self.type = "beacon_lateral"
                elif shom_data["type"] == "buoy" and self.data.attributes["CATLAM"] in ["1", "2", "3", "4"]:
                    self.type = "buoy_lateral"
                else:
                    raise ValueError(f'Combination of seamark type ({shom_data["type"]}) and category ({self.data.attributes["CATLAM"]}) is not allowed for lateral')

                self.category = __CATLAM__[self.data.attributes["CATLAM"]]
            else:
                raise ValueError('CATCAM or CATLAM attributes must be pesent')

        # Check this is a cardinal beacon
        #assert(shom_data["gml:description"].find("BCNCAR") != -1)

        if "HEIGHT" in self.data.attributes:
            if self.data.attributes["HEIGHT"] != '':
                self.height = float(self.data.attributes["HEIGHT"])

        if "COLOUR" in self.data.attributes:
            if self.data.attributes["COLOUR"] != '':
                self.colour = __colours2txt__(self.data.attributes["COLOUR"])

        if "COLPAT" in self.data.attributes:
            if self.data.attributes["COLPAT"] != '':
                self.colour_pattern = __COLOUR_PATTERNS__[self.data.attributes["COLPAT"]]

    def validate(self):
        self.data.validate()

    def osm_dict(self, osm_id=None):
        osm_result = {"type": "node", "tags": {}}
        osm_result.update({"id": osm_id} if osm_id != None else {})
        osm_result.update({"lon": self.lon, "lat": self.lat})

        osm_result["tags"].update({"seamark:type": self.type})

        osm_result["tags"].update({"ref:inspire": f"http://www.shom.fr/BDML/BALISAGE/{self.id}"})

        if __ALADIN__:
            if self.aladin_id != None:
                osm_result["tags"].update({"ref:aladin": self.aladin_id})

        osm_result["tags"].update({f"seammark:{self.type}:category": self.category})

        if self.height != None:
            osm_result["tags"].update({f"height": self.height})

        osm_result["tags"].update({f"seammark:{self.type}:colour": self.colour})

        if self.colour_pattern != None:
            osm_result["tags"].update({f"seammark:{self.type}:colour_pattern": self.colour_pattern})

        return osm_result


if __name__ == '__main__':
    seamarks = SHOMSeamarkList.from_file(SHOM_FILE).filter(48.80773, -3.56122, 10000)

    print(f"Number of seamarks in the collection: {len(seamarks)}")

    for seamark in seamarks:
        print(seamark)
        print("OSM JSON:")
        print(json.dumps(seamark.osm_dict(), indent=2))
        seamark.validate()
