import requests
import json
from dataclasses import dataclass

OVERPASS_URL="https://overpass-api.de/api/interpreter"

class OSMSeamarkList(list):
    def __init__(self, seamarks=[]):
            super().__init__(seamarks)

    @classmethod
    def from_file(cls, filename):
        # OSM json file
        with open(filename, 'r') as jsonfile:
            seamarks = json.load(jsonfile)

            return cls(OSMSeamark(seamark) for seamark in seamarks)

    @classmethod
    def from_api(cls, lat, lon, dist=10):
        result = requests.post(
                     OVERPASS_URL,
                     data=f"[out:json];node['seamark:type']['seamark:type'!='harbour']['seamark:type'!='rescue_station'](around:{dist},{lat},{lon});out;",
                 )

        return cls(OSMSeamark(seamark) for seamark in json.loads(result.text)["elements"])

    def filter(self, lat, lon, dist):
        return OSMSeamarkList(seamark for seamark in self if distance.distance((seamark.lat, seamark.lon), (lat, lon)).meters < dist)

    def filter_by_inspire(self, inspire):
        filtered_seamarks = OSMSeamarkList()

        for seamark in self:
            try:
                if seamark.__osm_data__["tags"]["ref:inspire"] == inspire:
                    filtered_seamarks.append(seamark)
            except KeyError:
                pass

        return filtered_seamarks

@dataclass
class OSMSeamark:
    """Class for OSM seamark"""
    id: str
    lat: float
    lon: float
    type: str
    category: str

    def __init__(self, osm_data):
        self.id = osm_data["id"]
        self.lat = osm_data["lat"]
        self.lon = osm_data["lon"]
        self.category = "N/A"
        self.__osm_data__ = osm_data

        assert("tags" in osm_data.keys())
        if "tags" in osm_data.keys():
            assert("seamark:type" in osm_data["tags"])

            self.type = osm_data["tags"]["seamark:type"]

            if self.type == "beacon_cardinal":
                assert("seamark:beacon_cardinal:category" in osm_data["tags"].keys())
                assert(osm_data["tags"]["seamark:beacon_cardinal:category"] in ["north", "east", "south", "west"])
                self.category = osm_data["tags"]["seamark:beacon_cardinal:category"]

                if "seamark:beacon_cardinal:colour" in osm_data["tags"].keys():
                    if osm_data["tags"]["seamark:beacon_cardinal:colour"] not in [
                        "yellow;black",
                        "yellow;black;yellow",
                        "black;yellow",
                        "black;yellow;black",
                    ]:
                        print(f"Warning: \"seamark:beacon_cardinal:colour\"bad value {osm_data["tags"]["seamark:beacon_cardinal:colour"]}")
                        print(osm_data)
                else:
                    print(f"Warning: \"seamark:beacon_cardinal:color\" should be present")
                    print(osm_data)

                if "seamark:beacon_cardinal:shape" not in osm_data["tags"].keys():
                    print(f"Warning: \"seamark:beacon_cardinal:shape\" should be present")
                    print(osm_data)

                print(osm_data)

    def osm_dict(self):
        return self.__osm_data__

if __name__ == '__main__':
    seamarks = OSMSeamarkList.from_api(48.80773, -3.56122, 1000)

    print(f"Number of seamarks in the collection: {len(seamarks)}")

    for seamark in seamarks:
        print(seamark)
        print(json.dumps(seamark.osm_dict(), indent=2))
