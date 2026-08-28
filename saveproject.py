import arcpy
import configparser
import os
import shutil
from datetime import datetime
from pathlib import Path

arcpy.AddMessage("Beginning script at {}".format(datetime.now().strftime("%H:%M:%S")))

config = configparser.ConfigParser()
project_directory_path = r"\\hanovergov\gisprojects\Community Dev\Planning\Case Maps\pn-case-map-pyt"
config_path = os.path.join(project_directory_path, 'config', 'config.ini')

read_files = config.read(config_path)
if not read_files:
    arcpy.AddError(f"Failed to read config file at: {config_path}")

# set input parameters
tempparcel_layer = arcpy.GetParameter(0)


projects_folder = config.get('config', 'projects_folder')
projects_folder_path = os.path.join(project_directory_path, projects_folder)
static_gdb = os.path.join(projects_folder_path, "staticdata.gdb")


def consolidate_gdbs(gdb1, gdb2, out_folder):

    # Create the new file geodatabase
    if not arcpy.Exists(os.path.join(out_folder, "data.gdb")):
        arcpy.management.CreateFileGDB(out_folder, "data")
    new_gdb = os.path.join(out_folder, "data.gdb")

    for source_gdb in (gdb1, gdb2):
        arcpy.AddMessage(f"Copying feature classes from {source_gdb}...")
        arcpy.env.workspace = source_gdb

        # Feature classes at the root of the gdb
        for fc in arcpy.ListFeatureClasses():
            copy_feature_class(source_gdb, fc, new_gdb)

        # Feature classes inside feature datasets
        for fds in arcpy.ListDatasets(feature_type="Feature"):
            arcpy.env.workspace = os.path.join(source_gdb, fds)
            for fc in arcpy.ListFeatureClasses():
                copy_feature_class(os.path.join(source_gdb, fds), fc, new_gdb)
            arcpy.env.workspace = source_gdb  # reset before next dataset

    arcpy.AddMessage("Consolidation complete.")
    return new_gdb


def copy_feature_class(source_workspace, fc_name, dest_gdb):
    in_fc = os.path.join(source_workspace, fc_name)
    out_fc = os.path.join(dest_gdb, fc_name)

    if arcpy.Exists(out_fc):
        arcpy.AddWarning(f"'{fc_name}' already exists in destination; skipping copy.")
    else:
        out_fc = arcpy.CreateUniqueName(fc_name, dest_gdb)
        arcpy.management.CopyFeatures(in_fc, out_fc)


def get_current_location(lyr):
    path = lyr.dataSource
    while path and not path.lower().endswith(".gdb"):
        parent = os.path.dirname(path)
        if parent == path:  # reached root without finding a .gdb
            return None
        path = parent
    return path


def get_title_values(lyr, field="title", delimiter="_ "):
    values = []
    with arcpy.da.SearchCursor(lyr, [field]) as cursor:
        for row in cursor:
            if row[0] is not None:
                values.append(str(row[0]))

    unique_values = set(values)
    if len(unique_values) == 1:
        return unique_values.pop()
    else:
        return delimiter.join(values)


def normalize(p):
    return os.path.normcase(os.path.normpath(p))


def reconfigure_all_layers(gdb, aprx):
    arcpy.AddMessage("Re-sourcing all map layers in the review project to the new project geodatabase...")

    for m in aprx.listMaps():
        for lyr in m.listLayers():
            if lyr.supports("DATASOURCE"):
                current_conn = os.path.dirname(lyr.dataSource)
                if current_conn != gdb:
                    lyr.updateConnectionProperties(current_conn, gdb)


def main():
    try:
        current_gdb = get_current_location(tempparcel_layer)
        title = get_title_values(tempparcel_layer)
        save_location = os.path.join(config.get('config', 'save_location'), title)
        save_location_path = Path(save_location)
        save_location_path.mkdir(parents=True, exist_ok=True)
        arcpy.AddMessage(f"Consolidating layers in new gdb location...")
        project_gdb = consolidate_gdbs(current_gdb, static_gdb, save_location)

        # get path to current toolbox
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        project_toolbox_path = aprx.defaultToolbox

        # make a copy of the current toolbox as 'case number + .atbx' in the save location
        new_toolbox_path = os.path.join(save_location_path, title + ".atbx")
        shutil.copy2(project_toolbox_path, new_toolbox_path)
        shutil.copy2(project_toolbox_path, new_toolbox_path)

        # save the project in the save location as 'case number + .aprx'
        new_project = os.path.join(save_location, title + ".aprx")
        aprx.saveACopy(new_project)

        # reset the saved project's default toolbox to 'case number + .tbx'
        arcpy.AddMessage(f"Re-setting default toolbox...")
        new_aprx = arcpy.mp.ArcGISProject(new_project)
        new_default_tbx_path = new_aprx.defaultToolbox
        new_aprx.updateConnectionProperties(new_default_tbx_path, new_toolbox_path)

        # Set the new toolbox as default
        new_aprx.defaultToolbox = new_toolbox_path

        # Remove every toolbox except the new one
        arcpy.AddMessage(f"Removing unneeded toolboxes...")
        kept_toolboxes = [tbx for tbx in new_aprx.toolboxes if
                          normalize(tbx['toolboxPath']) == normalize(new_toolbox_path)]
        new_aprx.updateToolboxes(kept_toolboxes)

        # save the project to the review location
        new_aprx.save()
        arcpy.AddMessage(f"Project saved to {save_location}.")
        reconfigure_all_layers(project_gdb, new_aprx)
        arcpy.AddMessage(f"Project layers re-pointed to new geodatabase.")
        new_aprx.save()

    except Exception as e:
        arcpy.AddError(str(e))
        raise e


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    main()
