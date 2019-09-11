import turtle as t

def hilbert_points(depth, side_length):
    global x,y,direction

    x,y,direction = 0,0,2 # Direction is an int in [0,1,2,3], where 0 is up, 1 is right, 2 is down and 3 is left.

    points = []
    def append():
        if (x,y) not in points:
            points.append((x,y))

    def l(v):
        global x,y,direction
        append()
        if v>0:
            direction -= 1
            if direction < 0:
                direction = 3
        else:
            r(-x)
    def r(v):
        global x,y,direction
        append()
        if v>0:
            direction += 1
            if direction > 3: 
                direction = 0

    def f(v):
        global x,y,direction
        append()
        if direction==0:
            y-=1
        elif direction==1:
            x+=1
        elif direction==2:
            y+=1
        elif direction==3:
            x-=1

    def hilbert(length, parity, depth):
        if depth==0:
                return
        l(parity)
        hilbert(length, -parity, depth-1)
        f(length)
        r(parity)
        hilbert(length, parity, depth-1)
        f(length)
        hilbert(length, parity, depth-1)
        r(parity)
        f(length)
        hilbert(length, -parity, depth-1)
        l(parity)
    hilbert(1,1,depth)


    maxp = max([i[1] for i in points]+[i[0] for i in points])
    minp = min([i[1] for i in points]+[i[0] for i in points])

    unit_len = side_length / (maxp-minp)
    points = [(point[0]*unit_len, point[1]*unit_len) for point in points]
    
    minvx = min([i[0] for i in points])
    minvy = min([i[1] for i in points])
    points = [(point[0]-minvx, point[1]-minvy) for point in points]
    return points

if __name__=='__main__':
    print(hilbert_points(int(input('depth: ')), float(input('side length:'))))
