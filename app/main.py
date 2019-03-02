import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#00FF00"
    head = "bendr"
    tail = "sharp"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    #board_X_mid = data['board']['width'] / 2
    #board_Y_mid = data['board']['height'] / 2

    xhead = int(data['you']['body'][0]['x'])
    yhead = int(data['you']['body'][0]['y'])
    bottomBorder = int(data['board']['height']) - 1
    rightBorder = int(data['board']['width']) - 1

    direction = ''
    fastest_direction = []
    directions = ['up', 'down', 'left', 'right']        #Directions are global, do not change with snake direction
    dangerous_direction = []    #ranked from most dangerous move to least dangerous

    """-----CREATE LIST OF COORDINATES TO AVOID-----"""
    avoid = []
    occupied = {}
    borders = []
    for b in data['board']['snakes']:                #search through all snakes and store xy coord pairs in avoid
        for c in b['body'][:-1]:
            occupied = {'x':int(c['x']), 'y':int(c['y'])}
            avoid.append(occupied)



    """-----OBJECT AVOIDANCE-----"""

    def avoid_snakes():      #Traverse the 'avoid' list and eliminate directions that would steer snake into a list entry
        for i in avoid:
            xi,yi = int(i['x']), int(i['y'])
            xdif = xhead - xi
            ydif = yhead - yi
            if (xdif == 1 or xdif == 0 or xdif == -1) and (ydif == 1 or ydif == 0 or ydif == -1):
                if xdif == 1 and ydif == 0 and 'left' in directions:        #left of head
                    directions.remove('left')
                elif xdif == -1 and ydif == 0 and 'right' in directions:    #right of head
                    directions.remove('right')
                elif xdif == 0 and ydif == 1 and 'up' in directions:        #above head
                    directions.remove('up')
                elif xdif == 0 and ydif == -1 and 'down' in directions:     #below head
                    directions.remove('down')

    def head_on_collision():

        return


    def corners():
        if yhead == 0 and xhead == 0:
            directions.remove('up')
            directions.remove('left')
        elif yhead == 0 and xhead == rightBorder:
            directions.remove('up')
            directions.remove('right')
        elif yhead == bottomBorder and xhead == 0:
            directions.remove('down')
            directions.remove('left')
        elif yhead == bottomBorder and xhead == rightBorder:
            directions.remove('down')
            directions.remove('right')
        else:
            return

    def walls():
        if yhead == 0 and 'up' in directions:
            directions.remove('up')
        elif yhead == bottomBorder and 'down' in directions:
            directions.remove('down')
        elif xhead == 0 and 'left' in directions:
            directions.remove('left')
        elif xhead == rightBorder and 'right' in directions:
            directions.remove('right')
        else:
            return

    """-----DANGEROUS MOVES-----"""

    def dangerous():        # Handles cases where up to 2 cells on right, left or above are occupied
        """
        [(-1,-1),(0,-1),(1,-1)]
        [(-1,0), (HEAD), (1,0)]
        [(-1,1), (0, 1), (1,1)]
        """

        grid = [1,0,-1]     # coordinates wrt snakehead used for both x and y traversing left to right top to bottom
        dangerous_cells = []
        nearby_cells = []
        cell = {}

        xneck, yneck = int(data['you']['body'][1]['x']), int(data['you']['body'][1]['y'])
        tail = data['you']['body'][int(len(data['you']['body'])) - 1]

        for y in grid:
            for x in grid:
                if (x != 0 or y != 0) and ((xhead - x) != xneck or (yhead - y) != yneck):   #if not on head or neck node
                    cell = {'x':xhead - x, 'y':yhead - y}   # create a list of coords for nearby cells, set all to safe
                    nearby_cells.append(cell)

        for i in avoid:
            if i in nearby_cells:
                dangerous_cells.append(i)

        print "Dangerous cells: ", dangerous_cells

        #dangerous cell counter variables
        dleft = 0   #dangerous on left
        dright = 0  #dangerous on right
        dup = 0     #dangerous above
        ddown = 0   #dangerous below


        #NEED TO ADD BORDERS TO DANGEROUS CELLS LIST
        #ADD tail awareness

        for j in dangerous_cells:
            xj,yj = xhead - j['x'], yhead - j['y']
            if (xj >= 1 or xj == 0 or xj <= -1) and (yj >= 1 or yj == 0 or yj <= -1):
                if xj >= 1:             #left of head
                    if yj >= 1:
                        dleft += 1
                        dup += 1
                    elif yj <= -1:
                        dleft += 1
                        ddown += 1
                    elif yj == 0:
                        dleft += 1
                elif xj <=1:            #right of head
                    if yj >= 1:
                        dright += 1
                        dup += 1
                    elif yj <= -1:
                        dright += 1
                        ddown += 1
                    elif yj == 0:
                        dright += 1
                elif xj == 0:           #above or below head
                    if yj >= 1:
                        dup += 1
                    elif yj <= -1:
                        ddown += 1


        #Rank most dangerous directions
        print "Left, right, up, down", dleft, dright, dup, ddown

        #add fatal directions??

        consider = [dleft, dright, dup, ddown]

        for k in range(1,4):
            if max(consider) != 0:
                if dleft == max(consider) and 'left' not in dangerous_direction and dleft != 1:
                    dangerous_direction.append('left')
                    consider.remove(dleft)
                elif dright == max(consider) and 'right' not in dangerous_direction and dright != 1:
                    dangerous_direction.append('right')
                    consider.remove(dright)
                elif dup == max(consider) and 'up' not in dangerous_direction and dup != 1:
                    dangerous_direction.append('up')
                    consider.remove(dup)
                elif ddown == max(consider) and 'down' not in dangerous_direction and ddown != 1:
                    dangerous_direction.append('down')
                    consider.remove(ddown)

        if abs(xhead - tail['x']) <= 1 and abs(yhead - tail['y']) <= 1:     #if tail is within 1 radius of head
            if tail['x'] == xhead and tail['y'] == yhead - 1 and 'up' in dangerous_direction:
                dangerous_direction.remove('up')
            elif tail['x'] == xhead and tail['y'] == yhead + 1 and 'down' in dangerous_direction:
                dangerous_direction.remove('down')
            elif tail['x'] == xhead - 1 and tail['y'] == yhead and 'left' in dangerous_direction:
                dangerous_direction.remove('left')
            elif tail['x'] == xhead + 1 and tail['y'] == yhead and 'right' in dangerous_direction:
                dangerous_direction.remove('right')

        return


    """-----MOVEMENT FUNCTIONS-----"""

    def go_to(location):    #goes straight to the target location
        closest = location
        xdir,ydir = xhead - closest['x'], yhead - closest['y']
        xabs,yabs = abs(xdir),abs(ydir)
                                                    #quadrant wrt head
        if xdir > 0 and ydir > 0 and xabs >= yabs:  #upper left x >= y
            fastest_direction.append('left')
            fastest_direction.append('up')
        elif xdir > 0 and ydir > 0 and xabs < yabs: #upper left x < y
            fastest_direction.append('up')
            fastest_direction.append('left')
                                                    #diagonals?
        elif xdir > 0 and ydir < 0 and xabs >= yabs:#lower left x >= y
            fastest_direction.append('left')
            fastest_direction.append('down')
        elif xdir > 0 and ydir < 0 and xabs < yabs: #lower left x < y
            fastest_direction.append('down')
            fastest_direction.append('left')

        elif xdir < 0 and ydir > 0 and xabs >= yabs:#upper right x >= y
            fastest_direction.append('right')
            fastest_direction.append('up')
        elif xdir < 0 and ydir > 0 and xabs < yabs: #upper right x < y
            fastest_direction.append('up')
            fastest_direction.append('right')

        elif xdir < 0 and ydir < 0 and xabs >= yabs:#lower right x >= y
            fastest_direction.append('right')
            fastest_direction.append('down')
        elif xdir < 0 and ydir < 0 and xabs < yabs: #lower right x < y
            fastest_direction.append('down')
            fastest_direction.append('right')

        elif xdir == 0 and ydir > 0:                #above
            fastest_direction.append('up')
        elif xdir == 0 and ydir < 0:                #below
            fastest_direction.append('down')
        elif xdir > 0 and ydir == 0:                #left
            fastest_direction.append('left')
        elif xdir < 0 and ydir == 0:                #right
            fastest_direction.append('right')
        return


    def nearest_food():
        closest = {'x':int(data['board']['food'][0]['x']), 'y':int(data['board']['food'][0]['y'])}
        #print "closest food", closest
        for i in data['board']['food']:
            if (abs(xhead - int(i['x'])) + abs(yhead - int(i['y']))) < (abs(xhead - int(closest['x'])) + abs(yhead - int(closest['y']))):
                closest = {'x':int(i['x']), 'y':int(i['y'])}
            #could add elif: food is equal distance away append to closest
        return closest

    def chase_tail(): #to make snake chase tail, call this as a param. in the go_to function go_to(chase_tail())
        tail = data['you']['body'][int(len(data['you']['body'])) - 1]
        return tail

        # add avoid trapping function for between snake and borders (arc ranking system from snakehead?? create a score to judge left or right action)
        # create danger ranking for moves. i.e compare occupied spaces left and right and add to dangerous list

        # count open spaces vs empty spaces in a quadrant, create a go_to_space function?
            # or count open spaces wrt direction snakehead can go?
            # or check adjacent squares for occupied adjacent squares?
        # chase tail
        # circle board
        # handle head on collisions
        # headhunter function? to kill time between 100-40 health instead of chase tail
        # change food aggressiveness based on snake length
        # change headhunter duration based on snake length


##  PRINT DATA  ##
    #print data
    #print(json.dumps(data))

    print data['turn']
    print data['you']['name']
    print "Health: ",data['you']['health']

    if data['you']['health'] < 40:
        go_to(nearest_food())
    else:
        go_to(chase_tail())
    avoid_snakes()
    corners()
    walls()
    dangerous()


    #compare directions list with ranked directions and if ranked direction[0] is in directions go that direction
    #try:
    #    direction = random.choice(directions)
    #except:
    #    direction = random.choice(['up', 'down', 'left', 'right'])

    #Make this bit of code selecting from the different lists a function?
    #second direction didnt work

    print "Directions: ", directions
    print "Fastest Directions: ", fastest_direction
    print "Dangerous moves: ",dangerous_direction



    safe_direction = [i for i in directions if i not in dangerous_direction]
    good_direction = [j for j in safe_direction if j in fastest_direction]



    if len(good_direction) != 0:
        direction = random.choice(good_direction)
    else:
        if len(safe_direction) != 0:
            direction = random.choice(safe_direction)
        elif len(directions) != 0:
            direction = random.choice(directions)
        else:
            direction = 'down'

    #this breaks chase_tail()
    #add check if number of dangerous spaces is less than a certain number to take fastest?


    #if only 2 directions use path_search()

    print "Safe directions: ",safe_direction
    print "Good directions: ",good_direction
    print "Choice: ", direction
    print direction
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
