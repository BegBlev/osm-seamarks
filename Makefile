all: BALISAGE

BALISAGE: BALISAGE.7z
	7z x $?

BALISAGE.7z:
	wget https://services.data.shom.fr/INSPIRE/telechargement/prepackageGroup/BALISAGE_PACK_DL/prepackage/BALISAGE/file/BALISAGE.7z
	@echo Current md5 sum should be a8d43affce968b0b3f9803dcbaccd503
	md5sum BALISAGE.7z
