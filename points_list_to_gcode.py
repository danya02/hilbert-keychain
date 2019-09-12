import sys
from shapely.geometry import Polygon, box

from math import sqrt, sin, cos, pi

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
    
    o(f'G0 X{points[0][0]}Y{points[0][1]}') # move to the first point
    
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
                o(f'G0{"3" if ccw(p1,p2,p3) else "2"} X{endx}Y{endy}R{dist}F{cut_speed}') # and curve to the endpoint
        # the head is now above the last curve point
        o(f'G1 X{points[-1][0]}Y{points[-1][1]}') # so we just draw a line to the final point

        
            
    o('G0 Z10') # raise head to safe distance
    o('G0 X0Y0') # revert to start position
    o('M30') # stop operation
    return outp

def points_to_gcode_with_outline(points, cut_depth, cut_speed, workpiece_dimension, cutout_corners, cutout_depth, curve_relative_radius=None):
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
    
    pointxmax = float('-inf') # find x and y bounds of points
    pointxmin = float('inf')
    pointymax = float('-inf')
    pointymin = float('inf')
    for i in points:
        pointxmax = max(pointxmax, i[0])
        pointymax = max(pointymax, i[1])
        pointxmin = min(pointxmin, i[0])
        pointymin = min(pointymin, i[1])

    pointcx = (pointxmin + pointxmax)/2 # find center of all points
    pointcy = (pointymin + pointymax)/2

    pointxmax -= pointcx
    pointymax -= pointcy
    pointxmin -= pointcx
    pointymin -= pointcy
    points = [(i[0]-pointcx, i[1]-pointcy) for i in points] # and move the points so that center is at 0,0

    # next, find the n-gon to inscribe in the square

    ngon = []

    def polar_to_cartesian(theta, r):
        return (r*cos(theta), r*sin(theta))
    angle = pi # initial angle is 180 degrees
    angle_offset = (2*pi)/cutout_corners # the arc of each side
    for i in range(cutout_corners):
        ngon.append(polar_to_cartesian(angle, workpiece_dimension/2))
        angle+=angle_offset


    ngonxmax = float('-inf') # while the circle has radius 1,
    ngonxmin = float('inf') # the bounds of the ngon may be different
    ngonymax = float('-inf') # (for example, consider the sides of a pentagon)
    ngonymin = float('inf') # and the area it intersects with a disk
    for i in ngon:
        ngonxmax = max(ngonxmax, i[0])
        ngonymax = max(ngonymax, i[1])
        ngonxmin = min(ngonxmin, i[0])
        ngonymin = min(ngonymin, i[1])
    ngoncx = (ngonxmin+ngonxmax)/2
    ngoncy = (ngonymin+ngonymax)/2

    
    ngon = [(i[0]-ngoncx, i[1]-ngoncy) for i in ngon] # move the ngon so its center coincides with the workpiece's center

    # the shape needs to be scaled down so it is contained
    # inside of the ngon

    # FIXME: my solution involves sequential scaling down. there might be
    # a better solution, but I don't know it. if you do, please submit a PR

    # also, this solution puts the shape in the center of the cutout,
    # which doesn't mean it will occupy the largest area. again,
    # I don't know how to fix it. the workaround is not to use ngons with
    # fewer than around 6 points.

    fac = 10.0
    step = 0.001 # can be varied to make more precise

    ngonpoly = Polygon(ngon)
    shape = box(pointxmin,pointymin,pointxmax,pointymax)

    while not shape.within(ngonpoly):
        fac -= step
        if fac<0:
            raise ValueError('Scale factor reached negative values')
        shape = box(pointxmin*fac,pointymin*fac,pointxmax*fac,pointymax*fac)
    


    points = [(i[0]*fac, i[1]*fac) for i in points] # scale all points relative to the center
    

    mx,my = 0,0 # now find the minimal coordinates
    for i in points+ngon:
        mx = min(mx,i[0])
        my = min(my,i[1])
    
    
    points = [(i[0]-mx, i[1]-my) for i in points] # and offset all points by that amount
    ngon = [(i[0]-mx, i[1]-my) for i in ngon]

    o(f'G0 X{points[0][0]}Y{points[0][1]}') # move to the first point

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
                o(f'G0{"3" if ccw(p1,p2,p3) else "2"} X{endx}Y{endy}R{dist}F{cut_speed}') # and curve to the endpoint
        # the head is now above the last curve point
        o(f'G1 X{points[-1][0]}Y{points[-1][1]}') # so we just draw a line to the final point

    
    # now it is time to cut the ngon
    o('G0 Z10') # raise the head to safe distance
    o(f'G0 X{ngon[0][0]}Y{ngon[0][1]}') # move over to the first point of the cutout
    o(f'G1 Z{cutout_depth}') # and lower to the cutout depth
    for i in ngon:
        o(f'G1 X{i[0]}Y{i[1]}') # cut to the next point
    o(f'G1 X{ngon[0][0]}Y{ngon[0][1]}') # cut the final edge
    
    # at this point the workpiece has probably separated from the base plate

    o('G0 Z10') # so raise head to safe distance
    o('G0 X0Y0') # revert to start position
    o('M30') # stop operation
    return outp
if __name__ == '__main__':
    points_to_gcode(eval(input()), -1, 100)

