GML_PATH := ./BALISAGE/GML
JSON_DB_PATH := json-db

JSON_DB_FILES := \
	${JSON_DB_PATH}/beacon-cardinal.json \
	${JSON_DB_PATH}/beacon-lateral.json \
	${JSON_DB_PATH}/buoy-cardinal.json \
	${JSON_DB_PATH}/buoy-lateral.json \

all: BALISAGE

BALISAGE: BALISAGE.7z
	7z x $?

BALISAGE.7z:
	wget https://services.data.shom.fr/INSPIRE/telechargement/prepackageGroup/BALISAGE_PACK_DL/prepackage/BALISAGE/file/BALISAGE.7z
	@echo Current md5 sum should be a8d43affce968b0b3f9803dcbaccd503
	md5sum BALISAGE.7z

.PHONY: db
db: ${JSON_DB_PATH} ${JSON_DB_FILES}

${JSON_DB_PATH}:
	mkdir -p ${JSON_DB_PATH}

${JSON_DB_PATH}/beacon-cardinal.json: ${GML_PATH}/tn-w_beacon_cardinal.gml
	xq-python '[."gml:FeatureCollection"."gml:featureMember"[]."tn-w:Beacon"+{"type": "beacon"}]' $< > $@

${JSON_DB_PATH}/beacon-lateral.json: ${GML_PATH}/tn-w_beacon_lateral.gml
	xq-python '[."gml:FeatureCollection"."gml:featureMember"[]."tn-w:Beacon"+{"type": "beacon"}]' $< > $@

${JSON_DB_PATH}/buoy-lateral.json: ${GML_PATH}/tn-w_buoy_lateral.gml
	xq-python '[."gml:FeatureCollection"."gml:featureMember"[]."tn-w:Buoy"+{"type": "buoy"}]' $< > $@

${JSON_DB_PATH}/buoy-cardinal.json: ${GML_PATH}/tn-w_buoy_cardinal.gml
	xq-python '[."gml:FeatureCollection"."gml:featureMember"[]."tn-w:Buoy"+{"type": "buoy"}]' $< > $@
