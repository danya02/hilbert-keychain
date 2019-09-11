def points_to_gcode(points, cut_depth, cut_speed):
    outp = []
    def o(c):
        print(c,end='\r\n')
        outp.append(c)
    o('T1M6') # some magic initialization codes, idk \_(``/)_/
    o('G90')
    o('G17')

    o('G0 X0Y0') #starting position: head at 0,0 at height 10
    o('G0 Z10')
    
    o(f'G1 Z{cut_depth}F{cut_speed}') # prepare for engraving: start the machine at speed and lower it to depth
    cx,cy = 0,0
    for i in points:
        dx = i[0]-cx
        dy = i[1]-cy
        cx,cy = i
        o(f'G1 X{cx}Y{cy}F{cut_speed}') # move to next point to engrave
    o('G0 Z10') # raise head to safe distance
    o('G0 X0Y0') # revert to start position
    o('M30') # stop operation
    return outp

if __name__ == '__main__':
    points_to_gcode(eval(input()), -1, 100)

