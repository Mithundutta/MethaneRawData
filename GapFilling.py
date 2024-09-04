import os
import shutil
import arcpy
from arcpy.sa import *

# Check out Spatial Analyst license:
try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        print ("Checked out \"Spatial\" Extension")
    else:
        raise LicenseError
except LicenseError:
    print ("Spatial Analyst license is unavailable")
except:
    print (arcpy.GetMessages(2))

# User Parameters
folder = r"C:\Users\jacob\Documents\MSG\CPE\MethaneProject"
timescale = "Weekly" # Options are "Weekly" and "Monthly"

# Set other parameters
inFolder = os.path.join(folder, timescale, "Images")
outFolder = os.path.join(folder, timescale, "Interpolated")
outTemp = os.path.join(folder, timescale, "temp")
mask = os.path.join(folder, "mask.tif")

# Create outFolder and outTemp
if not os.path.exists(outFolder):
  # Create a new directory because it does not exist 
  os.makedirs(outFolder)
if not os.path.exists(outTemp):
  # Create a new directory because it does not exist 
  os.makedirs(outTemp)

# Set environments
arcpy.env.workspace = inFolder

for raster in arcpy.ListRasters("*"):
    ras = Raster(raster)
    # Output should be same pixel size as input
    arcpy.env.cellSize = ras
    # Load mask raster
    maskRas = Raster(mask)
    # Convert data to points
    point = os.path.join(outTemp, "points.shp")
    arcpy.RasterToPoint_conversion(ras, point, "Value")
    # IDW interpolation on points
    idwRas = Idw(point, "grid_code", ras, 2, RadiusVariable(7, 150000))
    # Fill gaps with Idw values
    outRaster = Con((IsNull(ras) & maskRas == 1), idwRas, ras)
    outRaster.save(os.path.join(outFolder, raster))

# Remove temporary folder
if os.path.exists(outTemp):
    #os.rmdir(outTemp)
    shutil.rmtree(outTemp)



