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

arcpy.env.workspace = r'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb'


NHDLine = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap05_SrcData_NHD.gdb\\NHDLine'
NHDFlowline = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap05_SrcData_NHD.gdb\\NHDFlowline'
NHDArea = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap05_SrcData_NHD.gdb\\NHDArea'
NHDWaterbody = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap05_SrcData_NHD.gdb\\NHDWaterbody'

cliplayer = r'W:\Heritage\Conservation_Planning\HabitatMap\ReferenceLayers.gdb\clip_layer'

# NHD AREA
print("Beginning work on NHD Area polygons")
# subset to StreamRiver (FTYPE 460), Submerged Stream (FTYPE 461), Rapids (FTYPE 431)
arcpy.Clip_analysis(NHDArea, cliplayer, 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDArea_clip')
arcpy.management.MakeFeatureLayer('T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDArea_clip', 'NHDArea_sel', 'FType = 460 Or FType = 461 Or FType = 431')
arcpy.PolygonToRaster_conversion('NHDArea_sel', "FType", 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDArea_ras', "MAXIMUM_AREA")

# NHD Waterbody
print("Beginning work on NHD Waterbody polygons")
# subset to Lake/Pond (FTYPE 390), Reservoir: Reservoir Type = Water Storage; Construction Material = Earthen; Hydrographic Category = Perennial (FCODE 43615),
arcpy.Clip_analysis(NHDWaterbody, cliplayer, 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_clip')
arcpy.management.MakeFeatureLayer('T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_clip', 'NHDWaterbody_sel', 'FType = 390 Or FCode = 43615')
arcpy.PolygonToRaster_conversion('NHDWaterbody_sel', "FType", 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_ras', "MAXIMUM_AREA")

# Water from High Res Landcover
highreslc = r'W:\\Heritage\\Conservation_Planning\\HabitatMap\\HabitatMap02_ProcessedLayers.gdb\\landcover_2013_PA_hires_10m_processed'
attWater_highreslc = ExtractByAttributes(highreslc, "Value = 1")


# NHD flowlines for background data
print("Beginning work on NHD Flowlines")
arcpy.Clip_analysis(NHDFlowline, cliplayer, 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDFlowline_clip')
arcpy.analysis.Buffer('T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDFlowline_clip', 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDFlowline_buffer', '6 meters')
arcpy.PolygonToRaster_conversion('T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDFlowline_buffer', "FType", 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDFlowline_ras', "MAXIMUM_AREA")





####################### FUTURE WETLAND WORK
# NHD Waterbody
#arcpy.Clip_analysis(NHDWaterbody, cliplayer, 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_clip')
#arcpy.management.MakeFeatureLayer('T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_clip', 'NHDWaterbody_sel', 'FType = 466')
#arcpy.PolygonToRaster_conversion('NHDWaterbody_sel', "FType", 'T:\\HabitatMapUpdate\\HabitatMapWater\\HabitatMapWater.gdb\\NHDWaterbody_ras', "MAXIMUM_AREA")
