# Developer guide to maintaining the VC planner

## Finding Resources

### Image Sources:

 - VC Backgrounds: `UI/TarotCampaign/MAP/TC-<crusade>-BG-Large.dds`<br>
   You'll need to convert this manually to a `.jpg` file. Retain the size.

 - VC Icons: `UI/Artifacts/Map_shard_<crusade>_common.dds`<br>
   You'll need to convert this manually to a `.jpg` file. Retain the size.

### Minimaps:

 - Pre-generated minimaps: `UI/MosaicMap/Maps/<crusade-initials>_*.dds`<br>
   You'll need to run both `convert-dds-to-png.py` and `rename-files.py` on these.

### Data files:

 - `voidcrusade.cfg`: `Cfg/OpenWorld/voidcrusade.cfg`

 - Map files: `Cfg/Map/TarotCampaign/<crusade>/<garbled-mission-name>.cfg`<br>
   You'll need to run `rename-files.py` on these.

## Modifications:
