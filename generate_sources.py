import arcpy
import os
import json

dir_name = os.path.dirname(__file__)
with open(os.path.join(dir_name, 'config/shared.json')) as config_file:
    shared_config = json.load(config_file)
with open(os.path.join(dir_name, shared_config['env'])) as config_file:
    env_config = json.load(config_file)

# define inputs
taxparcelsmp = os.path.join(env_config['gishanover'], shared_config['parcels_fc'])
roads = os.path.join(env_config['gisgen'], shared_config['roads_fc'])
countyboundary = os.path.join(env_config['gisgen'], shared_config['countyboundary_fc'])
subgrid = os.path.join(env_config['gishanover'], shared_config['subgrid_fc'])
grid = os.path.join(env_config['gishanover'], shared_config['grid_fc'])
buildings = os.path.join(env_config['gishanover'], shared_config['buildings_fc'])
airportoverlay = os.path.join(env_config['gishanover'], shared_config['airport_fc'])
US1overlay = os.path.join(env_config['gishanover'], shared_config['US1overlay_fc'])
urbanoverlay = os.path.join(env_config['gishanover'], shared_config['urbanoverlay_fc'])
ashlandoverlay = os.path.join(env_config['gishanover'], shared_config['ashlandoverlay_fc'])
ashlandtown = os.path.join(env_config['gishanover'], shared_config['ashlandtown_fc'])
historicaldistrict = os.path.join(env_config['gishanover'], shared_config['historicaldistrict_fc'])
magisterialdistrict = os.path.join(env_config['gishanover'], shared_config['magisterialdistrict_fc'])
zoning = os.path.join(env_config['gishanover'], shared_config['zoning_fc'])
landuse = os.path.join(env_config['gishanover'], shared_config['landuse_fc'])
cup = os.path.join(env_config['gishanover'], shared_config['cup_fc'])
treelines = os.path.join(env_config['gishanover'], shared_config['treelines_fc'])
waterfeatures = os.path.join(env_config['gishanover'], shared_config['waterfeatures_fc'])

# define outputs
projectgdb = os.path.join(dir_name, 'CaseMap.gdb')
localgrid = os.path.join(projectgdb, 'grid')
localsubgrid = os.path.join(projectgdb, 'subgrid')
localcountyboundary = os.path.join(projectgdb, 'countyboundary')
localparcels = os.path.join(projectgdb, 'taxparcels')
localroads = os.path.join(projectgdb, 'roads')
localbuildings = os.path.join(projectgdb, 'buildings')
localairportoverlay = os.path.join(projectgdb, 'airportoverlay')
localUS1overlay = os.path.join(projectgdb, 'US1overlay')
localurbanoverlay = os.path.join(projectgdb, 'urbanoverlay')
localashlandoverlay = os.path.join(projectgdb, 'ashlandoverlay')
localashlandtown = os.path.join(projectgdb, 'ashlandtown')
localhistoricaldistrict = os.path.join(projectgdb, 'historicaldistrict')
localmagisterialdistrict = os.path.join(projectgdb, 'magisterialdistrict')
localzoning = os.path.join(projectgdb, 'zoning')
locallanduse = os.path.join(projectgdb, 'landuse')
localcup = os.path.join(projectgdb, 'cup')
localtreelines = os.path.join(projectgdb, 'treelines')
localwaterfeatures = os.path.join(projectgdb, 'waterfeatures')

# copy needed layers from sde sources
arcpy.AddMessage('------------------------------------------------------------')
arcpy.AddMessage('** Copy source layer schema from Enterprise **')

if arcpy.Exists(localroads) == True:
    arcpy.DeleteFeatures_management(localroads)
else:
    arcpy.CopyFeatures_management(roads, localroads)
    arcpy.DeleteFeatures_management(localroads)

if arcpy.Exists(localgrid) == True:
    arcpy.DeleteFeatures_management(localgrid)
else:
    arcpy.CopyFeatures_management(grid, localgrid)
    arcpy.DeleteFeatures_management(localgrid)

if arcpy.Exists(localsubgrid) == True:
    arcpy.DeleteFeatures_management(localsubgrid)
else:
    arcpy.CopyFeatures_management(subgrid, localsubgrid)
    arcpy.DeleteFeatures_management(localsubgrid)

if arcpy.Exists(localcountyboundary) == True:
    arcpy.DeleteFeatures_management(localcountyboundary)
else:
    arcpy.CopyFeatures_management(countyboundary, localcountyboundary)
    arcpy.DeleteFeatures_management(localcountyboundary)

if arcpy.Exists(localparcels) == True:
    arcpy.DeleteFeatures_management(localparcels)
else:
    arcpy.CopyFeatures_management(taxparcelsmp, localparcels)
    arcpy.DeleteFeatures_management(localparcels)

if arcpy.Exists(localbuildings) == True:
    arcpy.DeleteFeatures_management(localbuildings)
else:
    arcpy.CopyFeatures_management(buildings, localbuildings)
    arcpy.DeleteFeatures_management(localbuildings)

if arcpy.Exists(airportoverlay) == True:
    arcpy.DeleteFeatures_management(localairportoverlay)
else:
    arcpy.CopyFeatures_management(airportoverlay, localairportoverlay)
    arcpy.DeleteFeatures_management(localairportoverlay)

if arcpy.Exists(localUS1overlay) == True:
    arcpy.DeleteFeatures_management(localUS1overlay)
else:
    arcpy.CopyFeatures_management(US1overlay, localUS1overlay)
    arcpy.DeleteFeatures_management(localUS1overlay)

if arcpy.Exists(localurbanoverlay) == True:
    arcpy.DeleteFeatures_management(localurbanoverlay)
else:
    arcpy.CopyFeatures_management(urbanoverlay, localurbanoverlay)
    arcpy.DeleteFeatures_management(localurbanoverlay)

if arcpy.Exists(localashlandoverlay) == True:
    arcpy.DeleteFeatures_management(localashlandoverlay)
else:
    arcpy.CopyFeatures_management(ashlandoverlay, localashlandoverlay)
    arcpy.DeleteFeatures_management(localashlandoverlay)

if arcpy.Exists(localashlandtown) == True:
    arcpy.DeleteFeatures_management(localashlandtown)
else:
    arcpy.CopyFeatures_management(ashlandtown, localashlandtown)
    arcpy.DeleteFeatures_management(localashlandtown)

if arcpy.Exists(localhistoricaldistrict) == True:
    arcpy.DeleteFeatures_management(localhistoricaldistrict)
else:
    arcpy.CopyFeatures_management(historicaldistrict, localhistoricaldistrict)
    arcpy.DeleteFeatures_management(localhistoricaldistrict)

if arcpy.Exists(localmagisterialdistrict) == True:
    arcpy.DeleteFeatures_management(localmagisterialdistrict)
else:
    arcpy.CopyFeatures_management(magisterialdistrict, localmagisterialdistrict)
    arcpy.DeleteFeatures_management(localmagisterialdistrict)

if arcpy.Exists(localzoning) == True:
    arcpy.DeleteFeatures_management(localzoning)
else:
    arcpy.CopyFeatures_management(zoning, localzoning)
    arcpy.DeleteFeatures_management(localzoning)

if arcpy.Exists(locallanduse) == True:
    arcpy.DeleteFeatures_management(locallanduse)
else:
    arcpy.CopyFeatures_management(landuse, locallanduse)
    arcpy.DeleteFeatures_management(locallanduse)

if arcpy.Exists(localcup) == True:
    arcpy.DeleteFeatures_management(localcup)
else:
    arcpy.CopyFeatures_management(cup, localcup)
    arcpy.DeleteFeatures_management(localcup)

if arcpy.Exists(localtreelines) == True:
    arcpy.DeleteFeatures_management(localtreelines)
else:
    arcpy.CopyFeatures_management(treelines, localtreelines)
    arcpy.DeleteFeatures_management(localtreelines)

if arcpy.Exists(localwaterfeatures) == True:
    arcpy.DeleteFeatures_management(localwaterfeatures)
else:
    arcpy.CopyFeatures_management(waterfeatures, localwaterfeatures)
    arcpy.DeleteFeatures_management(localwaterfeatures)

arcpy.AddMessage('------------------------------------------------------------')
arcpy.AddMessage('** Append current data from Enterprise **')

arcpy.Append_management(roads, localroads, "NO_TEST")
arcpy.Append_management(grid, localgrid, "NO_TEST")
arcpy.Append_management(subgrid, localsubgrid, "NO_TEST")
arcpy.Append_management(countyboundary, localcountyboundary, "NO_TEST")
arcpy.Append_management(taxparcelsmp, localparcels, "NO_TEST")
arcpy.Append_management(buildings, localbuildings, "NO_TEST")
arcpy.Append_management(airportoverlay, localairportoverlay, "NO_TEST")
arcpy.Append_management(US1overlay, localUS1overlay, "NO_TEST")
arcpy.Append_management(urbanoverlay, localurbanoverlay, "NO_TEST")
arcpy.Append_management(ashlandoverlay, localashlandoverlay, "NO_TEST")
arcpy.Append_management(ashlandtown, localashlandtown, "NO_TEST")
arcpy.Append_management(historicaldistrict, localhistoricaldistrict, "NO_TEST")
arcpy.Append_management(magisterialdistrict, localmagisterialdistrict, "NO_TEST")
arcpy.Append_management(zoning, localzoning, "NO_TEST")
arcpy.Append_management(landuse, locallanduse, "NO_TEST")
arcpy.Append_management(cup, localcup, "NO_TEST")
arcpy.Append_management(treelines, localtreelines, "NO_TEST")
arcpy.Append_management(waterfeatures, localwaterfeatures, "NO_TEST")

arcpy.AddMessage('------------------------------------------------------------')
arcpy.AddMessage('** Done. **')
