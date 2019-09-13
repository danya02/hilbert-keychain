import points_list_to_gcode
import hilbert_points

points = hilbert_points.hilbert_points(int(input('Curve order: ')), float(input('Encapsulating square length (any positive number if using cutout): ')))

if input('Type "Y" for polygonal cutout, anything else otherwise: ').lower() == 'y':
    rad, offset = None,None
    if input('Type "Y" if you want a hole in the shape, anything else otherwise: ').lower()=='y':
        rad = float(input('Hole radius (choose negative for no hole): '))
        offset = float(input('Hole center offset: '))
    gcode = points_list_to_gcode.points_to_gcode_with_outline(points, float(input('Cut height (will not cut if positive): ')), float(input('Cut speed: ')), float(input('Workpiece square dimension: ')), int(input('How many corners in the N-gon: ')), float(input('Cut out height: ')), float(input('Relative arc offset: ')) if input('Type "Y" for rounded corners, anything else otherwise: ').lower()=='y' else None, rad, offset)

else:
    gcode = points_list_to_gcode.points_to_gcode(points, float(input('Cut height (will not cut if positive): ')), float(input('Cut speed: ')), float(input('Relative arc offset: ')) if input('Type "Y" for rounded corners, anything else otherwise: ').lower()=='y' else None)


filename = input('Output file name: ')
with open(filename, 'w') as o:
    for i in gcode:
        print(i, file=o)

