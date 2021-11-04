#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ctracey
#
# Created:     20/09/2021
# Copyright:   (c) ctracey 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# import models
import arcpy
from arcpy import env
from arcpy.sa import *

# To allow overwriting outputs change overwriteOutput option to True.
arcpy.env.overwriteOutput = True

refLayer = "W:\\Heritage\\Conservation_Planning\\HabitatMap\\ReferenceLayers.gdb\\snap_raster_10m"
arcpy.env.cellSize = refLayer
arcpy.env.snapRaster = refLayer
arcpy.env.mask = refLayer
arcpy.env.extent = "-80672.322784879 138824.548045481 -69355.52 147921.18"  

# Check out any necessary licenses.
#arcpy.CheckOutExtension("spatial")

arcpy.env.workspace = r'T:\\HabitatMapUpdate\\DevelopedLand\\DevelopedLand.gdb'

############################################################################################################################
# Developed Open Space - this section takes the low vegetation category from the High resolution landcover and intersects it with the
# Developed open space class from the NLCD, hopefully resulting in a layer that shows open space within urban areas.
print("Beginning work on Developed Open Space")
nlcd = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap02_ProcessedLayers.gdb\\nlcd2016_Clip_processed'
highreslc = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap02_ProcessedLayers.gdb\\landcover_2013_PA_hires_10m_processed'

# extract hi res developed
attUrban_highreslc = ExtractByAttributes(highreslc, "Value = 7 Or Value = 8 Or Value = 9 Or Value = 10 Or Value = 11 Or Value = 12") # 7 = structures; 8 = other impervious

# Execute ExtractByAttributes
print("- extracting HiRes landcover and NLCD by open space attributes")
attExtract_nlcd = ExtractByAttributes(nlcd, "NLCD_Land_Cover_Class LIKE 'Developed%'")
attExtract_highreslc = ExtractByAttributes(highreslc, "Value = 5") # 5 = low veg
outReclass1 = Reclassify(attExtract_nlcd, "Value", RemapValue([[21,1],[22,1],[23,1],[24,1]]))
#outReclass1.save("landuse_rcls")

outCombine = Combine([outReclass1, attExtract_highreslc])


print("- calculating the intersection...")
# If either A or B are null it will give you 0 if not 1, all the ones should show where A and B have values.
devopenspace = arcpy.sa.Con(((IsNull(attExtract_nlcd))|(IsNull(attExtract_highreslc))),1)
devopenspace1 = arcpy.sa.SetNull(devopenspace, devopenspace, "VALUE=0")

# Save the output
print("- saving...")
devopenspace1.save("T:\\HabitatMapUpdate\\DevelopedLand\\DevelopedLand.gdb\\devopenspace_intersection")
print("- saved...")

##########################################################################################################################
# roads and other transportation infrastructure
print("working on the roads")

roads_local = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap06_SrcData_Misc.gdb\\PaLocalRoads2021_03'
roads_state = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap06_SrcData_Misc.gdb\\PaStateRoads2020_12'
railroads = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap06_SrcData_Misc.gdb\\PaLocalRoads2021_03'
osm_roads = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_osm_roads_free_1'
osm_railroads = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_osm_railways_free_1'
osm_traffic = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_osm_traffic_a_free_1'
osm_transport = "W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_osm_transport_a_free_1"

tmp_roads_local_buffer = "tmp_roads_local_buffer123"
tmp_roads_state_buffer = "tmp_roads_state_buffer123"
tmp_railroads_buffer = "tmp_railroads_buffer123"
tmp_osm_roads_buffer = "tmp_osm_roads123"
tmp_osm_railroads_buffer = "tmp_osm_railroads123"
tmp_osm_traffic = "tmp_osm_traffic123"
tmp_osm_transport = "tmp_osm_transport123"


# local roads
print("- local roads")
arcpy.analysis.Buffer(roads_local, tmp_roads_local_buffer, "6 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
arcpy.management.CalculateField(in_table=tmp_roads_local_buffer, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]

# state roads
print("- state roads")
arcpy.analysis.Buffer(roads_state, tmp_roads_state_buffer, "6 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
arcpy.management.CalculateField(in_table=tmp_roads_state_buffer, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]

# railroads
print("- railroads")
arcpy.analysis.Buffer(railroads, tmp_railroads_buffer, "6 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
arcpy.management.CalculateField(in_table=tmp_railroads_buffer, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]

# openstreetmap roads and railroads
arcpy.analysis.Buffer(osm_roads, tmp_osm_roads_buffer, "6 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
arcpy.management.CalculateField(in_table=tmp_osm_roads_buffer, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]

arcpy.analysis.Buffer(osm_railroads, tmp_osm_railroads_buffer, "6 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
arcpy.management.CalculateField(in_table=tmp_osm_railroads_buffer, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]

# openstreetmap traffic polygons
arcpy.management.CopyFeatures(osm_traffic, tmp_osm_traffic) 
arcpy.management.CalculateField(in_table=tmp_osm_traffic, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]
arcpy.management.CopyFeatures(osm_transport, tmp_osm_transport) 
arcpy.management.CalculateField(in_table=tmp_osm_transport, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]



##########################################################################################################################
# places
print("working on other development")

osm_poi = "W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_osm_pois_a_free_1"
tmp_osm_poi = "tmp_osm_poi123"

#arcpy.management.MakeFeatureLayer(osm_poi, tmp_osm_poi, where_clause="fclass <> 'battlefield' And fclass <> 'park' And fclass <> 'university'")
osm_poi_layer = arcpy.management.SelectLayerByAttribute(in_layer_or_view=osm_poi, selection_type="NEW_SELECTION", where_clause="fclass <> 'battlefield' And fclass <> 'park' And fclass <> 'university'", invert_where_clause="")
arcpy.management.CopyFeatures(osm_poi_layer, tmp_osm_poi)
arcpy.management.CalculateField(in_table=tmp_osm_poi, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]
#arcpy.conversion.PolygonToRaster(in_features=tmp_osm_poi, value_field="ClassVal", out_rasterdataset="dev_draster", cell_assignment="MAXIMUM_COMBINED_AREA", priority_field="NONE", build_rat="BUILD")



##########################################################################################################################
# merge everything
arcpy.Merge_management([tmp_roads_local_buffer, tmp_roads_state_buffer, tmp_railroads_buffer, tmp_osm_roads_buffer, tmp_osm_railroads_buffer, tmp_osm_traffic, tmp_osm_transport, tmp_osm_poi], "dev_merge_test", "", "ADD_SOURCE_INFO")

arcpy.analysis.PairwiseDissolve("dev_merge_test", "dev_dissolve") 
arcpy.management.CalculateField(in_table="dev_dissolve", field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]
arcpy.conversion.PolygonToRaster(in_features="dev_dissolve", value_field="ClassVal", out_rasterdataset="dev_raster", cell_assignment="MAXIMUM_COMBINED_AREA", priority_field="NONE", build_rat="BUILD")


arcpy.management.MosaicToNewRaster("attUrban_highreslc;dev_raster;outCombine", r"T:\HabitatMapUpdate\DevelopedLand\DevelopedLand.gdb", "testmerge1", 'PROJCS["alber",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["Standard_Parallel_1",40.0],PARAMETER["Standard_Parallel_2",42.0],PARAMETER["latitude_of_origin",39.0],UNIT["Meter",1.0]]', "8_BIT_UNSIGNED", None, 1, "MAXIMUM", "FIRST")
outReclass2 = Reclassify("testmerge1", "Value", RemapRange([[1,100,1]]), "NODATA")



############################################################################################################################
### buildings
##
##print("Beginning work on Buildings")
##
### input layers
##buildings_Microsoft = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap04_SrcData_OSM.gdb\\gis_MicrosoftBuildings'
##buildings_Huntingdon = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\HuntingdonCounty_Structures202108.shp'
##buildings_Washington = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\WashingtonCounty_Buildings202104.shp'
##buildings_Lancaster = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\LancasterCountyBuildings2018_01.shp'
##buildings_Lehigh = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\LehighCounty_BuildingFootprints202108.shp'
##buildings_Allegheny = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\AlleghenyCounty_Footprints202109.shp'
##buildings_Chester = r'T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\ChesterCounty_BuildingFootprints2015.shp'
##
### output layers
##tmp_buildings_HuntingdonBuff = "T:\\HabitatMapUpdate\\OtherLandcover\\Buildings\\HuntingdonCounty_Buffer.shp"
##out_DevelopedBuilding = "T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\tmpBuilding"
##
### Buffer the Huntingdon points into polygons
##print("- buffering the Huntingdon polygons")
##buildings_HuntingdonSelection = arcpy.SelectLayerByLocation_management(buildings_Huntingdon, "INTERSECT", buildings_Microsoft, "0 Meters", "NEW_SELECTION", "INVERT") 
##arcpy.analysis.Buffer(in_features=buildings_HuntingdonSelection, out_feature_class=tmp_buildings_HuntingdonBuff, buffer_distance_or_field="5 Meters", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
##
### Process: Merge (Merge) (management)
##print("- merging all the layers together")
##arcpy.management.Merge(inputs=[buildings_Washington, buildings_Lancaster, buildings_Lehigh, buildings_Allegheny, buildings_Chester, buildings_HuntingdonOut, buildings_Microsoft], output=tmpBuilding, field_mappings="GlobalID \"GlobalID\" true true false 38 Text 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,GlobalID,0,38;EDITOR \"EDITOR\" true true false 10 Text 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,EDITOR,0,10;UPDATE_TYP \"UPDATE_TYP\" true true false 50 Text 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,UPDATE_TYP,0,50;YEAR \"YEAR\" true true false 5 Long 0 5,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,YEAR,-1,-1;UPDATE_DAT \"UPDATE_DAT\" true true false 8 Date 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,UPDATE_DAT,-1,-1;SPEC \"SPEC\" true true false 5 Long 0 5,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,SPEC,-1,-1;HEIGHT \"HEIGHT\" true true false 19 Double 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,HEIGHT,-1,-1;SHAPE_area \"SHAPE_area\" true true false 19 Double 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,SHAPE_area,-1,-1,BuildingFootprints\\LehighCounty_BuildingFootprints202108,Shape_Area,-1,-1,BuildingFootprints\\AlleghenyCounty_Footprints202109,Shape_Area,-1,-1;SHAPE_len \"SHAPE_len\" true true false 19 Double 0 0,First,#,BuildingFootprints\\LancasterCountyBuildings2018_01,SHAPE_len,-1,-1;OBJECTID \"OBJECTID\" true true false 7 Long 0 7,First,#,BuildingFootprints\\WashingtonCounty_Buildings202104,OBJECTID,-1,-1,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,OBJECTID,-1,-1;Shape__Are \"Shape__Are\" true true false 24 Double 15 23,First,#,BuildingFootprints\\WashingtonCounty_Buildings202104,Shape__Are,-1,-1,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,Shape__Are,-1,-1;Shape__Len \"Shape__Len\" true true false 24 Double 15 23,First,#,BuildingFootprints\\WashingtonCounty_Buildings202104,Shape__Len,-1,-1,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,Shape__Len,-1,-1;PIN \"PIN\" true true false 12 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,PIN,0,12;PARNUM \"PARNUM\" true true false 5 Long 0 5,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,PARNUM,-1,-1;STNUM \"STNUM\" true true false 10 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,STNUM,0,10;STPRE \"STPRE\" true true false 2 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,STPRE,0,2;STNAME \"STNAME\" true true false 50 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,STNAME,0,50;STTYPE \"STTYPE\" true true false 10 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,STTYPE,0,10;STSUF \"STSUF\" true true false 4 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,STSUF,0,4;UNITNUM \"UNITNUM\" true true false 10 Text 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,UNITNUM,0,10;Shape_Leng \"Shape_Leng\" true true false 19 Double 0 0,First,#,BuildingFootprints\\LehighCounty_BuildingFootprints202108,Shape_Leng,-1,-1,BuildingFootprints\\AlleghenyCounty_Footprints202109,Shape_Leng,-1,-1;status \"status\" true true false 20 Text 0 0,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,status,0,20,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Status,0,50;prev_area \"prev_area\" true true false 19 Double 0 0,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,prev_area,-1,-1;pct_change \"pct_change\" true true false 19 Double 0 0,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,pct_change,-1,-1;CLASS \"CLASS\" true true false 254 Text 0 0,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,CLASS,0,254,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,CLASS,0,8;LUC \"LUC\" true true false 19 Double 0 0,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,LUC,-1,-1;FEATURECOD \"FEATURECOD\" true true false 5 Long 0 5,First,#,BuildingFootprints\\AlleghenyCounty_Footprints202109,FEATURECOD,-1,-1;HEIGHT_STD \"HEIGHT_STD\" true true false 24 Double 15 23,First,#,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,HEIGHT_STD,-1,-1;HEIGHT_EST \"HEIGHT_EST\" true true false 3 Short 0 3,First,#,BuildingFootprints\\ChesterCounty_BuildingFootprints2015,HEIGHT_EST,-1,-1;STRU_NUM \"STRU_NUM\" true false false 19 Double 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,STRU_NUM,-1,-1;TYPE \"TYPE\" true false false 3 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,TYPE,0,3;HSENUMBER \"HSENUMBER\" true false false 19 Double 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,HSENUMBER,-1,-1;PREFIXDIR \"PREFIXDIR\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,PREFIXDIR,0,2;STREETNAME \"STREETNAME\" true false false 40 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,STREETNAME,0,40;STREETSUF \"STREETSUF\" true false false 4 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,STREETSUF,0,4;POSTDIR \"POSTDIR\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,POSTDIR,0,2;EDIT \"EDIT\" true false false 5 Long 0 5,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,EDIT,-1,-1;ADDEXT \"ADDEXT\" true false false 16 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,ADDEXT,0,16;STREET \"STREET\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,STREET,0,50;NOTES \"NOTES\" true false false 70 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,NOTES,0,70;MUNI \"MUNI\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,MUNI,0,50;LOCATION \"LOCATION\" true false false 30 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LOCATION,0,30;ADDRESS \"ADDRESS\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,ADDRESS,0,50;created_us \"created_us\" true false false 254 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,created_us,0,254;created_da \"created_da\" true true false 8 Date 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,created_da,-1,-1;last_edite \"last_edite\" true false false 254 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,last_edite,0,254;last_edi_1 \"last_edi_1\" true true false 8 Date 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,last_edi_1,-1,-1;HOUSE_SUFF \"HOUSE_SUFF\" true false false 10 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,HOUSE_SUFF,0,10;DiscrpAgID \"DiscrpAgID\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,DiscrpAgID,0,75;DateUpdate \"DateUpdate\" true true false 8 Date 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,DateUpdate,-1,-1;Effective \"Effective\" true true false 8 Date 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Effective,-1,-1;Expire \"Expire\" true true false 8 Date 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Expire,-1,-1;Site_NGUID \"Site_NGUID\" true false false 254 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Site_NGUID,0,254;Country \"Country\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Country,0,2;State \"State\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,State,0,2;County \"County\" true false false 40 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,County,0,40;AddCode \"AddCode\" true false false 6 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,AddCode,0,6;AddDataURI \"AddDataURI\" true false false 254 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,AddDataURI,0,254;Inc_Muni \"Inc_Muni\" true false false 100 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Inc_Muni,0,100;Uninc_Comm \"Uninc_Comm\" true false false 100 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Uninc_Comm,0,100;Nbrhd_Comm \"Nbrhd_Comm\" true false false 100 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Nbrhd_Comm,0,100;AddNum_Pre \"AddNum_Pre\" true false false 15 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,AddNum_Pre,0,15;Add_Number \"Add_Number\" true false false 6 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Add_Number,0,6;AddNum_Suf \"AddNum_Suf\" true false false 15 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,AddNum_Suf,0,15;St_PreMod \"St_PreMod\" true false false 15 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PreMod,0,15;St_PreDir \"St_PreDir\" true false false 9 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PreDir,0,9;St_PreTyp \"St_PreTyp\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PreTyp,0,50;St_PreSep \"St_PreSep\" true false false 20 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PreSep,0,20;St_Name \"St_Name\" true false false 60 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_Name,0,60;St_PosTyp \"St_PosTyp\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PosTyp,0,50;St_PosDir \"St_PosDir\" true false false 9 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PosDir,0,9;St_PosMod \"St_PosMod\" true false false 25 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,St_PosMod,0,25;LSt_PreDir \"LSt_PreDir\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LSt_PreDir,0,2;LSt_Name \"LSt_Name\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LSt_Name,0,75;LSt_Type \"LSt_Type\" true false false 4 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LSt_Type,0,4;LSt_PosDir \"LSt_PosDir\" true false false 2 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LSt_PosDir,0,2;ESN \"ESN\" true false false 5 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,ESN,0,5;MSAGComm \"MSAGComm\" true false false 30 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,MSAGComm,0,30;Post_Comm \"Post_Comm\" true false false 40 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Post_Comm,0,40;Post_Code \"Post_Code\" true false false 7 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Post_Code,0,7;Post_Code4 \"Post_Code4\" true false false 4 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Post_Code4,0,4;Building \"Building\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Building,0,75;Floor \"Floor\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Floor,0,75;Unit \"Unit\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Unit,0,75;Room \"Room\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Room,0,75;Seat \"Seat\" true false false 75 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Seat,0,75;Addtl_Loc \"Addtl_Loc\" true false false 225 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Addtl_Loc,0,225;LandmkName \"LandmkName\" true false false 150 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,LandmkName,0,150;Milepost \"Milepost\" true false false 150 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Milepost,0,150;Place_Type \"Place_Type\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Place_Type,0,50;Placement \"Placement\" true false false 25 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Placement,0,25;Long \"Long\" true false false 19 Double 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Long,-1,-1;Lat \"Lat\" true false false 19 Double 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Lat,-1,-1;Elev \"Elev\" true false false 10 Long 0 10,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,Elev,-1,-1;TaxAuth \"TaxAuth\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,TaxAuth,0,50;UPI \"UPI\" true false false 50 Text 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,UPI,0,50;BUFF_DIST \"BUFF_DIST\" true true false 0 Double 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,BUFF_DIST,-1,-1;ORIG_FID \"ORIG_FID\" true true false 0 Long 0 0,First,#,T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\HuntingdonCounty_Structures2,ORIG_FID,-1,-1", add_source="NO_SOURCE_INFO")
##
### Process: Calculate Field (9) (Calculate Field) (management)
##tmpBuilding_2_ = arcpy.management.CalculateField(in_table=tmpBuilding, field="ClassVal", expression="1", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]
##
##print("- converting to a raster")
##arcpy.PolygonToRaster_conversion(tmpBuilding, "ClassVal", 'T:\\HabitatMapUpdate\\HabitatMapUpdate.gdb\\tmpBuildings_ras', "MAXIMUM_AREA")
##
### Save the output
###print("- saving...")
###devopenspace1.save("T:\\HabitatMapUpdate\\DevelopedLand\\DevelopedLand.gdb\\devopenspace_intersection")
###print("- saved...")
##
##
#######################
### infrastructure from the NHD
##NHDArea = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap05_SrcData_NHD.gdb\\NHDArea'
##
### spillways (FTYPE=455); Flume (362), Dam (343
##arcpy.management.SelectLayerByAttribute(NHDArea, 'NEW_SELECTION', 'FType = 455 Or FType = 362 Or FType = 343 Or FType = ')
##
##
##
