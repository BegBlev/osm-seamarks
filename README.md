# osm-seamarks
All French nautical navigation seamarks (such as beacons, buoys, etc.) are managed by a French governmental institution, 'Les Phares et Balises.' The seamarks database is made available to the public by another French governmental institution, the SHOM (Navy Hydrographic Service), as open data.

These French seamarks are not well represented in OpenStreetMap, and therefore, they are not accurate in OpenSeaMap. Various types of anomalies exist, including incorrect positions and missing seamarks in OSM.

This project provides tools and documentation to retrieve the SHOM database, obtain OSM data via the Overpass API, perform consistency checks, and submit modifications to OSM.

## Download DB
Database is located on SHOM website. This database is a set of XML files and a few documentation compressed as a `.7z` file. We use `make` in order to download and uncompress this database.
```
make
```

## Build JSON database
Building `.json` files from `.gml` is actually an xml query followed by a format convertion. This operation is launched using `make`.
```
make db
```

## OSM handling
OSM handling is made using `osm.py` code. This code allow to:
* get relevant OSM nodes (seamarks) in a specified area
* list the seamarks
* display data
* validate data

```
python3 osm.py
```
