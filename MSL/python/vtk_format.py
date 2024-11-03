'''
#!################### THE VTK FORMAT ##################
#! RectilinearGrid WholeExtent
Specifies its extent within the datasets whole extent
-> <x1, x2, y1, y2, z1, z2>
e.g.: <RectilinearGrid WholeExtent="0 119 0 43 0 2">
#! Piece Extent
Specifies its extent within the whole data extent range.
-> <x1, x2, y1, y2, z1, z2>
e.g.: <Piece Extent="0 119 0 43 0 2">
#* PointData within piece
Pointdata passed in binary / ASCII format
e.g:    <DataArray type="Float32" Name="E-Field" NumberOfComponents="3" format="binary" RangeMin="0" RangeMax="0">
        BgAAAACAAACAZgAANAAAADQAAAA0AAAANAAAADQAAAAwAAAAeJztwQEBAAAAgJD+r+4ICgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYgAAAAXic7cEBAQAAAICQ/q/uCAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGIAAAAF4nO3BAQEAAACAkP6v7ggKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABiAAAABeJztwQEBAAAAgJD+r+4ICgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYgAAAAXic7cEBAQAAAICQ/q/uCAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGIAAAAF4nO3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB4NGaAAAE=
        <InformationKey name="L2_NORM_RANGE" location="vtkDataArray" length="2">
          <Value index="0">
            0
          </Value>
          <Value index="1">
            0
          </Value>
        </InformationKey>
      </DataArray>

This point stores the actual values at the grid vertices.
In our example: 
- RangeMin is 0 everywhere
- RangeMax Varies from almost 0 to 10.8415
#* Min Max values
Indicate the actual Min-Max values
#! DataArray under coordinates
Contains each of the coordinates.
This is visible through 
- the RangeMin coordinates
- the RangeMax coordinates
Having a fixed minimum and maximum, as well as the actual float data being the same everywhere.
VERY IMPORTANT: what needs to happen here is in fact changing the colour scaling of the electric field range.

'''

