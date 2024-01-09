import vtk

# Specify the input VTK file (unstructured grid)
input_file = "input.vtk"

# Specify the output VTP file
output_file = "output.vtp"

# Create a reader for the VTK file with unstructured grid data
reader = vtk.vtkUnstructuredGridReader()
reader.SetFileName(input_file)

# Read the VTK file
reader.Update()

# Get the unstructured grid from the reader
unstructured_grid = reader.GetOutput()

# Convert the unstructured grid to polydata (if needed)
geometry_filter = vtk.vtkGeometryFilter()
geometry_filter.SetInputData(unstructured_grid)
geometry_filter.Update()

# Get the polydata from the geometry filter
polydata = geometry_filter.GetOutput()

# Create a writer for the VTP file
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(output_file)

# Set the input polydata for the writer
writer.SetInputData(polydata)

# Write the VTP file
writer.Write()
