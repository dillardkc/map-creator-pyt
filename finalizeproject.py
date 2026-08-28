import arcpy
import configparser
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import ctypes

arcpy.AddMessage("Beginning script at {}".format(datetime.now().strftime("%H:%M:%S")))

config = configparser.ConfigParser()
project_directory_path = r"\\hanovergov\gisprojects\Community Dev\Planning\Case Maps\pn-case-map-pyt"
config_path = os.path.join(project_directory_path, 'config', 'config.ini')

read_files = config.read(config_path)
if not read_files:
    arcpy.AddError(f"Failed to read config file at: {config_path}")


def parse_code(input_string):
    """
    Parses strings like 'AAA0000-anystringhere' or 'AA0000-anystringhere'
    into type (2-3 letters) and year (4 digits).
    """
    match = re.match(r'^([A-Za-z]{2,3})(\d{4})-(.*)$', input_string)
    if not match:
        raise ValueError(f"Input '{input_string}' does not match expected format")

    casetype = match.group(1)
    year = match.group(2)
    rest = match.group(3)

    return casetype, year, rest


def reconfigure_all_layers(database, aprx):
    arcpy.AddMessage("Re-sourcing all map layers to the new project geodatabase...")
    for m in aprx.listMaps():
        for lyr in m.listLayers():
            if lyr.supports("DATASOURCE"):
                current_conn = os.path.dirname(lyr.dataSource)
                if current_conn != database:
                    lyr.updateConnectionProperties(current_conn, database)


def show_popup(header, message, icon="warning"):
    icon_flags = {"info": 0x40, "warning": 0x30, "error": 0x10}
    flags = icon_flags.get(icon, 0x30) | 0x1000 | 0x40000  # MB_SYSTEMMODAL | MB_TOPMOST
    ctypes.windll.user32.MessageBoxW(0, message, header, flags)


def main():
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        project_path = aprx.filePath
        project_filename = os.path.basename(project_path)
        casenumber = Path(project_path).stem
        arcpy.AddMessage(f"Project filename: {project_filename}")
        gdb_location = Path(project_path).parent
        gdb = os.path.join(gdb_location, "data.gdb")
        casetype, year, rest = parse_code(project_filename)
        final_location = (config.get('config', 'final_location').replace("yyyy", year).replace
                          ("casetype", casetype).replace("casenumber", casenumber))
        arcpy.AddMessage(f"Final location path will be: {final_location}")
        final_location_path = Path(final_location)
        final_location_path.mkdir(parents=True, exist_ok=True)

        # Save a copy of the project and the gdb to the new location
        final_project_path = os.path.join(final_location, project_filename)
        aprx.saveACopy(final_project_path)
        final_gdb = os.path.join(final_location, "data.gdb")
        if os.path.exists(final_gdb):
            shutil.rmtree(final_gdb)
        shutil.copytree(gdb, final_gdb, ignore=shutil.ignore_patterns('*.lock'))

        arcpy.AddMessage(f"Copied data.gdb to {final_gdb}")
        final_project = arcpy.mp.ArcGISProject(final_project_path)

        # Re-source layers
        reconfigure_all_layers(final_gdb, final_project)

        arcpy.AddMessage(f"Project saved to {final_location}")
        show_popup("Notice", "The final project has been saved to" + str(final_location) + ". Remember to "
                            "delete this version from the Monthly Case Files folder now that it has been finalized.")

    except Exception as e:
        arcpy.AddError(str(e))
        raise e


if __name__ == "__main__":
    main()
