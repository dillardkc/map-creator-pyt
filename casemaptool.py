import arcpy
import configparser
import os
import re
from datetime import datetime

arcpy.AddMessage("Beginning script at {}".format(datetime.now().strftime("%H:%M:%S")))

config = configparser.ConfigParser()
project_directory_path = r"\\hanovergov\gisprojects\Community Dev\Planning\Case Maps\pn-case-map-pyt"
config_path = os.path.join(project_directory_path, 'config', 'config.ini')

read_files = config.read(config_path)
if not read_files:
    arcpy.AddError(f"Failed to read config file at: {config_path}")

# set input parameters
newmap = arcpy.GetParameterAsText(0)
mapdatefull = arcpy.GetParameterAsText(1)
refreshstatic = arcpy.GetParameterAsText(2)
gpinlist = arcpy.GetParameterAsText(3)
title = arcpy.GetParameterAsText(4)
owners = arcpy.GetParameterAsText(5)
desc1 = arcpy.GetParameterAsText(6)
desc2 = arcpy.GetParameterAsText(7)
desc3 = arcpy.GetParameterAsText(8)
mapscale = arcpy.GetParameterAsText(9)
maptype = arcpy.GetParameterAsText(10)

if newmap.strip().lower() == "no":
    refreshstatic = "No"

# Parse the date parameter once — ArcGIS date parameters come in as 'MM/DD/YYYY HH:MM:SS'
map_dt = datetime.strptime(mapdatefull.split(' ', 1)[0], "%m/%d/%Y") if newmap == 'No' else datetime.now()

project_gdb = map_dt.strftime("%Y%m%d") + ".gdb"
parcel_date = map_dt.strftime("%m/%d/%Y")
mapdate_str = map_dt.strftime("%Y%m%d")

connections_folder = config.get('config', 'connections_folder')
projects_folder = config.get('config', 'projects_folder')
projects_folder_path = os.path.join(project_directory_path, projects_folder)
connections_path = os.path.join(project_directory_path, connections_folder)
project_gdb_path = os.path.join(project_directory_path, projects_folder, project_gdb)
static_gdb = os.path.join(project_directory_path, projects_folder, "staticdata.gdb")
tempparcels = os.path.join(project_gdb_path, 'tempparcels')
taxparcels = os.path.join(project_gdb_path, 'Parcels_with_Data')
tempparcels_merge = os.path.join(project_gdb_path, 'tempparcels_merge')
tempparcels_mp = os.path.join(project_gdb_path, 'tempparcels_mp')
centerpoint = os.path.join(project_gdb_path, 'centerpoint')


def gdb_check(folder):
    if newmap == 'Yes' and refreshstatic == 'Yes':
        arcpy.AddMessage("All map data will be refreshed. Re-creating project geodatabase...")
        arcpy.env.overwriteOutput = True
        arcpy.CreateFileGDB_management(folder, project_gdb)
        arcpy.CreateFileGDB_management(folder, "staticdata.gdb")
    elif newmap == 'Yes' and refreshstatic == 'No':
        arcpy.AddMessage("Parcel data will be refreshed. Re-creating project geodatabase...")
        arcpy.env.overwriteOutput = True
        arcpy.CreateFileGDB_management(folder, project_gdb)
    else:
        arcpy.AddMessage(f"Data for {mapdate_str} will be used for map creation. Checking for gdb...")
        if not arcpy.Exists(os.path.join(folder, project_gdb)):
            arcpy.AddError(f"Output gdb for selected date does not exist: {project_gdb}")
        else:
            arcpy.AddMessage("Output gdb for selected date exists.")


def generate_sources(gdb):
    # generate static sources
    if refreshstatic == 'Yes':
        arcpy.AddMessage(f"Refreshing static data sources...")
        arcpy.env.workspace = static_gdb
        arcpy.env.overwriteOutput = True
        feature_sources = config['static_inputs']
        for fc in feature_sources:
            fcname = feature_sources[fc].split('\\')[-1]
            arcpy.AddMessage(f"Copying '{fcname}' to file gdb...")
            enterprise_fc = os.path.join(connections_path, feature_sources[fc])
            arcpy.CopyFeatures_management(enterprise_fc, fcname)
    else:
        arcpy.AddMessage('Skipping refresh of static data...')

    # generate dynamic sources
    if newmap == 'Yes':
        arcpy.AddMessage('Refreshing parcel data...')
        arcpy.env.workspace = gdb
        arcpy.env.overwriteOutput = True
        feature_sources = config['dynamic_inputs']
        for fc in feature_sources:
            fcname = feature_sources[fc].split('\\')[-1]
            arcpy.AddMessage(f"Copying '{fcname}' to file gdb...")
            enterprise_fc = os.path.join(connections_path, feature_sources[fc])
            arcpy.CopyFeatures_management(enterprise_fc, fcname)
    else:
        arcpy.AddMessage(f'Skipping refresh of parcel data. Existing data for {mapdate_str} will be used...')


def create_temp_parcels(fullparcels):
    # make parcel selection
    arcpy.AddMessage("Selecting parcels.")
    if ',' in str(gpinlist):
        selectionstatement = "GPIN = '" + str(gpinlist).replace(", ", "' or GPIN = '") + "'"

    else:
        selectionstatement = "GPIN = '" + str(gpinlist) + "'"

    # create temporary parcels from selection
    arcpy.AddMessage("Creating temporary parcel layer from selection.")
    arcpy.MakeFeatureLayer_management(fullparcels, "taxparcels_layer")
    arcpy.SelectLayerByAttribute_management("taxparcels_layer", 'NEW_SELECTION', selectionstatement)
    arcpy.CopyFeatures_management("taxparcels_layer", tempparcels_mp)

    # dissolve selected parcels
    arcpy.MakeFeatureLayer_management(tempparcels_mp, "tempparcels_mp_layer")
    arcpy.Dissolve_management("tempparcels_mp_layer", tempparcels_merge)
    arcpy.CopyFeatures_management(tempparcels_merge, tempparcels)


def calc_fields():
    # add and calculate temporary parcel fields
    gpins = str(gpinlist)
    whereclause = "OBJECTID IS NOT NULL"
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)

    arcpy.AddMessage("GPINs list: " + str(gpins))
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.AddField_management(tempparcels, "GPINs", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "title", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "owners", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc1", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc2", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc3", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "magdist", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "maptype", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "mapdate", "TEXT", "#", "#", 255)
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)
    arcpy.CalculateField_management(tempparcels, "GPINs", '"GPINs: ' + str(gpins) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "title", '"' + str(title) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "owners", '"' + str(owners) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc1", '"' + str(desc1) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc2", '"' + str(desc2) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc3", '"' + str(desc3) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "maptype", '"' + str(maptype) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "mapdate", '"' + str(parcel_date) + '"', "PYTHON3")


def calc_overlay():
    # define static inputs
    magisterialdistrict = os.path.join(static_gdb, 'MAGISTERIAL_DISTRICTS')
    # determine magisterial district
    arcpy.MakeFeatureLayer_management(magisterialdistrict, 'magisterialdistrict_layer')
    arcpy.FeatureToPoint_management(tempparcels, centerpoint, "INSIDE")
    arcpy.SelectLayerByLocation_management('magisterialdistrict_layer', 'INTERSECT', centerpoint)

    magdist = "Unknown Magisterial District"
    with arcpy.da.SearchCursor('magisterialdistrict_layer', 'PROPDIST') as rows:
        for row in rows:
            magdist = str(row[0] + " Magisterial District")
            arcpy.AddMessage(f'Magisterial District: {magdist}')

    # calculate magisterial district layer to current magisterial district
    whereclause = "OBJECTID IS NOT NULL"
    # whereclause = "magdist = '" + str(magdist) + "'"
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)
    arcpy.CalculateField_management(tempparcels, "magdist", '"' + str(magdist) + '"', "PYTHON3")


def set_map_appearance(scale):
    match = re.search(r'(\d+)ft', scale)
    if match:
        scalefeet = str(match.group(1))
    else:
        arcpy.AddWarning(f"Could not parse feet from scale: {scale}. Using scale 1in = 500ft.")
        scalefeet = "500"

    # buffer centerpoint to use for scaling
    buffer = os.path.join(project_gdb_path, 'buffer_' + scalefeet)
    if arcpy.Exists(buffer):
        arcpy.Delete_management(buffer)

    arcpy.AddMessage("Creating buffer on parcel selection centerpoint to scale map to: " + str(scale))
    size = config.get('buffer_sizes', scalefeet)
    # buffer centerpoint to use for scaling
    arcpy.PairwiseBuffer_analysis(centerpoint, buffer, size)

    # set extent
    arcpy.AddMessage("Scaling.")
    aprx = arcpy.mp.ArcGISProject("CURRENT")

    # get correct layout for desired map print size
    layout = next(layout for layout in aprx.listLayouts() if layout.name == maptype)
    arcpy.AddMessage(f"Layout: {layout.name}.")
    mapframe_list = layout.listElements("MAPFRAME_ELEMENT")
    if not mapframe_list:
        arcpy.AddError(f"No map frame found in layout '{layout.name}'.")
        return
    mapframe = mapframe_list[0]
    desc = arcpy.Describe(buffer)
    extent = desc.extent
    new_extent = arcpy.Extent(extent.XMin, extent.YMin, extent.XMax, extent.YMax)
    cam = mapframe.camera  # type: ignore
    cam.setExtent(new_extent)
    mapframe.camera = cam  # type: ignore


def reconfigure_layers(gdb):
    if newmap == 'Yes':
        arcpy.AddMessage("Re-sourcing map layers to today's geodatabase...")
    else:
        arcpy.AddMessage("Re-sourcing map layers to existing geodatabase for selected date...")

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    for maps in aprx.listMaps():
        for lyr in maps.listLayers():
            if lyr.supports("DATASOURCE"):
                # Example: Update a file geodatabase connection
                current_conn = os.path.dirname(lyr.dataSource)
                if current_conn != gdb:
                    lyr.updateConnectionProperties(current_conn, gdb)
        for lyr in maps.listLayers():
            if lyr.supports("DATASOURCE"):
                current_conn = os.path.dirname(lyr.dataSource)
                if current_conn != static_gdb:
                    lyr.updateConnectionProperties(current_conn, static_gdb)


def temp_cleanup():
    # delete temp data
    arcpy.AddMessage("Deleting temp data.")
    arcpy.Delete_management(tempparcels_mp)
    arcpy.Delete_management(tempparcels_merge)
    arcpy.Delete_management(centerpoint)


def main():
    try:
        gdb_check(projects_folder_path)
        generate_sources(project_gdb_path)
        create_temp_parcels(taxparcels)
        calc_fields()
        calc_overlay()
        set_map_appearance(mapscale)
        reconfigure_layers(project_gdb_path)
        temp_cleanup()

    except Exception as e:
        arcpy.AddError(str(e))
        raise e


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    main()
