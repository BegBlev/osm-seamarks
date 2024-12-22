import re
import json
from dataclasses import dataclass
from geopy import distance

__ALADIN__ = True

SHOM_FILE="json-db/beacon-cardinal.json"

class SHOMSeamarkList(list):
    def __init__(self, seamarks):
            super().__init__(seamarks)

    @classmethod
    def from_file(cls, filename):
        # SHOM json file
        with open(filename, 'r') as shomfile:
            shom_seamarks = json.load(shomfile)

            return cls(SHOMBeacon(seamark) for seamark in shom_seamarks)

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


@dataclass
class SHOMBeacon:
    """Class for SHOM beacon"""
    id: str
    aladin_id: str
    lat: float
    lon: float
    type: str
    data: SHOMDescription

    def __init__(self, shom_data):
        assert(re.match("BALISAGE_FR[0-9]{15}", shom_data["@gml:id"]))

        self.id = shom_data["@gml:id"].removeprefix("BALISAGE_")
        self.lat, self.lon = shom_data["tn:geometry"]["gml:Point"]["gml:pos"].split(" ")

        self.data = SHOMDescription(shom_data["gml:description"])

        if "numald" in self.data.attributes:
            if self.data.attributes["numald"] != '':
                self.aladin_id = self.data.attributes["numald"]

        # Check this is a cardinal beacon
        #assert(shom_data["gml:description"].find("BCNCAR") != -1)

        type = shom_data["gml:description"][shom_data["gml:description"].find("CATCAM"):][len("CATCAM :"):len("CATCAM :")+1]

        if type == "1":
            self.type = "north"
        elif type == "2":
            self.type = "east"
        elif type == "3":
            self.type = "south"
        elif type == "4":
            self.type = "west"
        else:
            raise ValueError('Beacon type unknown')

    def validate(self):
        self.data.validate()

    def osm_dict(self, osm_id=None):
        osm_result = {"type:": "node"}
        osm_result.update({"id": osm_id} if osm_id != None else {})
        osm_result.update({"lon": self.lon, "lat": self.lat})

        osm_result.update({"tags": {"type": self.type}})

        if __ALADIN__:
            if self.aladin_id != None:
                osm_result["tags"].update({"ref:aladin": self.aladin_id})

        return osm_result


if __name__ == '__main__':
    seamarks = SHOMSeamarkList.from_file(SHOM_FILE).filter(48.80773, -3.56122, 10000)

    print(f"Number of seamarks in the collection: {len(seamarks)}")

    for seamark in seamarks:
        print(seamark)
        print(f"OSM JSON: {seamark.osm_dict()}")
        seamark.validate()
