import points_list_to_gcode
import hilbert_points

points = hilbert_points.hilbert_points(int(input('Curve order: ')), float(input('Encapsulating square length: ')))
gcode = points_list_to_gcode.points_to_gcode(points, float(input('Cut height (will not cut if positive): ')), float(input('Cut speed: ')))
filename = input('Output file name: ')
with open(filename, 'w') as o:
    for i in gcode:
        print(i, file=o)

