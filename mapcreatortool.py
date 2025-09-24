import arcpy
import configparser
import os
from datetime import datetime
import numpy

dir_name = os.path.dirname(__file__)

arcpy.AddMessage("Beginning script at {}".format(datetime.now().strftime("%H:%M:%S")))

config = configparser.ConfigParser()
config.read('config/local.ini')

# set input parameters
newmap = arcpy.GetParameterAsText(0)
mapdatefull = arcpy.GetParameterAsText(1)
refreshstatic = arcpy.GetParameterAsText(2)
gpinlist = arcpy.GetParameterAsText(3)
title = arcpy.GetParameterAsText(4)
desc1 = arcpy.GetParameterAsText(5)
desc2 = arcpy.GetParameterAsText(6)
desc3 = arcpy.GetParameterAsText(7)
mapscale = arcpy.GetParameterAsText(8)
maptype = arcpy.GetParameterAsText(9)
mapsize = arcpy.GetParameterAsText(10)

# define inputs
today_str = datetime.now().strftime("%Y%m%d")
mapdate = mapdatefull.split(' ', 1)[0]

# if another date is needed:
if newmap == 'No':
    mapdate_parts = mapdate.split("/")
    year = mapdate_parts[-1]
    month = str(mapdate_parts[0]).zfill(2)
    day = str(mapdate_parts[1]).zfill(2)
    mapdate_str = year + month + day
    project_gdb = str(mapdate_str) + ".gdb"
    parcel_date = mapdate
    refreshstatic = 'No'
else:
    project_gdb = today_str + ".gdb"
    parcel_date = datetime.now().strftime("%m/%d/%Y")

connections_folder = config.get('config', 'connections_folder')
projects_folder = config.get('config', 'projects_folder')
connections_path = os.path.join(dir_name, connections_folder)
project_gdb_path = os.path.join(dir_name, projects_folder, project_gdb)
static_gdb = os.path.join(dir_name, projects_folder, "staticdata.gdb")
tempparcels = os.path.join(project_gdb_path, 'tempparcels')
taxparcels = os.path.join(project_gdb_path, 'Parcels_with_Data')
tempparcels_merge = os.path.join(project_gdb_path, 'tempparcels_merge')
tempparcels_mp = os.path.join(project_gdb_path, 'tempparcels_mp')
centerpoint = os.path.join(project_gdb_path, 'centerpoint')


def gdb_check(folder):
    # create project gdb if needed
    if newmap == 'Yes' and refreshstatic == 'Yes':
        arcpy.AddMessage(f"All map data will be refreshed. Re-creating project geodatabase...")
        arcpy.env.overwriteOutput = True
        arcpy.CreateFileGDB_management(folder, today_str + ".gdb")
        arcpy.CreateFileGDB_management(folder, "staticdata.gdb")
    elif newmap == 'Yes' and refreshstatic == 'No':
        arcpy.AddMessage(f"Parcel data will be refreshed. Re-creating project geodatabase...")
        arcpy.env.overwriteOutput = True
        arcpy.CreateFileGDB_management(folder, today_str + ".gdb")
    else:
        arcpy.AddMessage(f"Data for {mapdate_str} will be used for map creation. Checking for gdb...")
        if not arcpy.Exists(os.path.join(folder, mapdate_str + ".gdb")):
            arcpy.AddError("Output gdb for selected date does not exist!")
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
            arcpy.AddMessage(f"Copying '{feature_sources[fc].split('.')[-1]}' to file gdb...")
            enterprise_fc = os.path.join(connections_path, feature_sources[fc])
            arcpy.CopyFeatures_management(enterprise_fc, feature_sources[fc].split('.')[-1])
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
        arcpy.AddMessage(f'Skipping refresh of parcel data. Data for {mapdate_str} will be used...')


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


def calc_fields(temp_mp):
    # extract ownership info from each selected parcel and concatenate to create ownership list
    def unique_values(table, field):
        data = arcpy.da.TableToNumPyArray(table, [field])
        return numpy.unique(data[field])

    try:
        ownerlist = unique_values(temp_mp, "OWN_NAME1")
    except Exception as e:
        ownerlist = "No ownership information"
        arcpy.AddMessage("Error: " + e.args[0])
    arcpy.AddMessage("Ownership List: " + str(ownerlist))
    # convert list to string
    owners = ', '.join([str(elem) for elem in ownerlist])

    # add and calculate temporary parcel fields
    gpins = str(gpinlist)
    whereclause = "OBJECTID IS NOT NULL"
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)

    arcpy.AddMessage("GPINs list: " + str(gpins))
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.AddField_management(tempparcels, "GPINs", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "title", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "owner", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc1", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc2", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "desc3", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "magdist", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "maptype", "TEXT", "#", "#", 255)
    arcpy.AddField_management(tempparcels, "mapdate", "TEXT", "#", "#", 255)
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)
    arcpy.CalculateField_management(tempparcels, "GPINs", '"' + str(gpins) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "title", '"' + str(title) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc1", '"' + str(desc1) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc2", '"' + str(desc2) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "desc3", '"' + str(desc3) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "maptype", '"' + str(maptype) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "owner", '"' + str(owners) + '"', "PYTHON3")
    arcpy.CalculateField_management(tempparcels, "mapdate", '"' + str(parcel_date) + '"', "PYTHON3")


def calc_overlay():
    # define static inputs
    magisterialdistrict = os.path.join(static_gdb, 'MAGISTERIAL_DISTRICTS')
    # determine magisterial district
    arcpy.MakeFeatureLayer_management(magisterialdistrict, 'magisterialdistrict_layer')
    arcpy.FeatureToPoint_management(tempparcels, centerpoint, "INSIDE")
    arcpy.SelectLayerByLocation_management('magisterialdistrict_layer', 'INTERSECT', centerpoint)

    with arcpy.da.SearchCursor('magisterialdistrict_layer', 'PROPDIST') as rows:
        for row in rows:
            magdist = str(row[0] + " Magisterial District")
            arcpy.AddMessage(f'Magisterial District: {magdist}')

    # calculate magisterial district layer to current magisterial district
    whereclause = "magdist = '" + str(magdist) + "'"
    arcpy.MakeFeatureLayer_management(tempparcels, "tempparcels_layer")
    arcpy.SelectLayerByAttribute_management("tempparcels_layer", "NEW_SELECTION", whereclause)
    arcpy.CalculateField_management(tempparcels, "magdist", '"' + str(magdist) + '"', "PYTHON3")


def set_map_appearance(scale):
    scalefeet = str(scale[6:9])
    # buffer centerpoint to use for scaling
    buffer = os.path.join(project_gdb, 'buffer_' + str(scale[6:9]))
    if arcpy.Exists(buffer):
        arcpy.Delete_management(buffer)

    arcpy.AddMessage("Creating buffer on parcel selection centerpoint to scale map to: " + str(scale))
    if mapsize == '8.5 x 11':
        size_config = 'buffer_sizes_8.5x11'
    elif mapsize == '11 x 14':
        size_config = 'buffer_sizes_11x14'

    size = config.get(size_config, scalefeet)
    # buffer centerpoint to use for scaling
    arcpy.PairwiseBuffer_analysis(centerpoint, buffer, size)

    # set extent
    arcpy.AddMessage("Scaling.")
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    project_path = aprx.filePath
    arcpy.AddMessage(f"Project: {os.path.basename(project_path)}.")

    # get correct layout for desired map print size
    layout = next(layout for layout in aprx.listLayouts() if layout.name == mapsize)
    arcpy.AddMessage(f"Layout: {layout.name}.")
    mapframe = layout.listElements("MAPFRAME_ELEMENT")[0]
    arcpy.AddMessage(f"Map Frame: {mapframe.name}.")
    mapcreator = aprx.listMaps()[0]
    arcpy.AddMessage(f"Map: {mapcreator.name}.")
    desc = arcpy.Describe(buffer)
    extent = desc.extent
    new_extent = arcpy.Extent(extent.XMin, extent.YMin, extent.XMax, extent.YMax)
    mapframe.camera.setExtent(new_extent)

    map_layer_names = config.get('layer_lists', maptype)
    fulllyrlist = mapcreator.listLayers()

    for lyr in fulllyrlist:
        if lyr.name in map_layer_names:
            if lyr.supports('VISIBLE'):
                lyr.visible = True
            else:
                arcpy.AddMessage(f"{lyr} layer visibility cannot be toggled.")
        else:
            lyr.visible = False


def reconfigure_layers(gdb):
    if newmap == 'Yes':
        arcpy.AddMessage("Re-sourcing map layers to today's geodatabase...")
    else:
        arcpy.AddMessage("Re-sourcing map layers to existing geodatabase for selected date...")
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    mapcreator = aprx.listMaps()[0]
    for lyr in mapcreator.listLayers():
        if lyr.supports("DATASOURCE"):
            # Example: Update a file geodatabase connection
            current_conn = os.path.dirname(lyr.dataSource)
            if current_conn != gdb:
                lyr.updateConnectionProperties(current_conn, gdb)


def temp_cleanup():
    # delete temp data
    arcpy.AddMessage("Deleting temp data.")
    arcpy.Delete_management(tempparcels_mp)
    arcpy.Delete_management(tempparcels_merge)
    arcpy.Delete_management(centerpoint)


def main():
    try:
        gdb_check(projects_folder)
        generate_sources(project_gdb_path)
        create_temp_parcels(taxparcels)
        calc_fields(tempparcels_mp)
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
