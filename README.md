# osm-seamarks

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
