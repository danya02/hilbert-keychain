import sys

from math import sqrt

# from https://www.toptal.com/python/computational-geometry-in-python-from-theory-to-implementation
def ccw(A, B, C):
    """Tests whether the turn formed by A, B, and C is ccw"""
    return (B[0] - A[0]) * (C[1] - A[1]) > (B[1] - A[1]) * (C[0] - A[0])

def scale(vec,scal):
    return (vec[0]*scal, vec[1]*scal)

def add(a,b):
    return (a[0]+b[0], a[1]+b[1])

def points_to_gcode(points, cut_depth, cut_speed, curve_relative_radius=None):
    outp = []
    if curve_relative_radius is not None and curve_relative_radius>0.5:
        print('warning: curve\'s relative radius is greater than 0.5, which may cause overlap', file=sys.stderr)
    def o(c):
        print(c,end='\r\n')
        outp.append(c)
    o('T1M6') # some magic initialization codes, idk \_(``/)_/
    o('G90')
    o('G17')

    o('G0 X0Y0') #starting position: head at 0,0 at height 10
    o('G0 Z10')
    
    o(f'G1 Z{cut_depth}F{cut_speed}') # prepare for engraving: start the machine at speed and lower it to depth

    if not curve_relative_radius: # no curvature for engraving, so taking each point as-is
        for i in points:
            o(f'G1 X{i[0]}Y{i[1]}F{cut_speed}') # move to next point to engrave
    else: # curvature is enabled, so need to consider each corner
        # DANGER: this assumes that all angles are 90 degrees and parallel to the workpiece! If this is not true, the curved corners will not be continuous!
        for i in range(len(points)-2):
            p1,p2,p3 = points[i],points[i+1],points[i+2]
            d12 = sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) #distances to vertex
            d23 = sqrt((p3[0]-p2[0])**2 + (p3[1]-p2[1])**2)
            dist = min(d12,d23)*curve_relative_radius # radius is relative to least distance

            v21 = (p1[0]-p2[0], p1[1]-p2[1]) # vectors between points
            v23 = (p3[0]-p2[0], p3[1]-p2[1])
            unitv21 = scale(v21, 1/d12) # normalized vectors
            unitv23 = scale(v23, 1/d23)
            startx,starty = add(p2,scale(unitv21, dist)) # start point is "radius" away from vertex along first ray
            endx,endy = add(p2,scale(unitv23, dist)) # similar for 2nd ray
            if abs(startx-endx)<0.0001 or abs(starty-endy)<0.0001: # if start and end are on the horizontal or vertical
                o(f'G1 X{endx}Y{endy}') # then there is no sense in curving to it
            else:
                o(f'G1 X{startx}Y{starty}') # move to the start point of the curve
                o(f'G{"3" if ccw(p1,p2,p3) else "2"} X{endx}Y{endy}R{dist}') # and curve to the endpoint
        # the head is now above the last curve point
        o(f'G1 X{points[-1][0]}Y{points[-1][1]}') # so we just draw a line to the final point

        
            
    o('G0 Z10') # raise head to safe distance
    o('G0 X0Y0') # revert to start position
    o('M30') # stop operation
    return outp

if __name__ == '__main__':
    points_to_gcode(eval(input()), -1, 100)

