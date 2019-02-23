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

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    board_X_mid = data['board']['width'] / 2
    board_Y_mid = data['board']['height'] / 2

    xhead = int(data['you']['body'][0]['x'])
    yhead = int(data['you']['body'][0]['y'])
    bottomBorder = int(data['board']['height']) - 1
    rightBorder = int(data['board']['width']) - 1

    direction = ''
    ranked_direction = []
    directions = ['up', 'down', 'left', 'right']

    """-----CREATE LIST OF COORDINATES TO AVOID-----"""
    avoid = []
    occupied = {}
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


    """-----MOVEMENT FUNCTIONS-----"""

    def go_to(location):    #goes straight to the target location
        closest = location
        xdir,ydir = xhead - closest['x'], yhead - closest['y']
        xabs,yabs = abs(xdir),abs(ydir)
                                                    #quadrant wrt head
        if xdir > 0 and ydir > 0 and xabs >= yabs:  #upper left x >= y
            ranked_direction.append('left')
            ranked_direction.append('up')
        elif xdir > 0 and ydir > 0 and xabs < yabs: #upper left x < y
            ranked_direction.append('up')
            ranked_direction.append('left')
                                                    #diagonals?
        elif xdir > 0 and ydir < 0 and xabs >= yabs:#lower left x >= y
            ranked_direction.append('left')
            ranked_direction.append('down')
        elif xdir > 0 and ydir < 0 and xabs < yabs: #lower left x < y
            ranked_direction.append('down')
            ranked_direction.append('left')

        elif xdir < 0 and ydir > 0 and xabs >= yabs:#upper right x >= y
            ranked_direction.append('right')
            ranked_direction.append('up')
        elif xdir < 0 and ydir > 0 and xabs < yabs: #upper right x < y
            ranked_direction.append('up')
            ranked_direction.append('right')

        elif xdir < 0 and ydir < 0 and xabs >= yabs:#lower right x >= y
            ranked_direction.append('right')
            ranked_direction.append('down')
        elif xdir < 0 and ydir < 0 and xabs < yabs: #lower right x < y
            ranked_direction.append('down')
            ranked_direction.append('right')

        elif xdir == 0 and ydir > 0:                #above
            ranked_direction.append('up')
            ranked_direction.append('up')
        elif xdir == 0 and ydir < 0:                #below
            ranked_direction.append('down')
            ranked_direction.append('down')
        elif xdir > 0 and ydir == 0:                #left
            ranked_direction.append('left')
            ranked_direction.append('left')
        elif xdir < 0 and ydir == 0:                #right
            ranked_direction.append('right')
            ranked_direction.append('right')
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
        # handle potential head on collisions

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
    #print data['you']['health']

    if data['you']['health'] < 40:
        go_to(nearest_food())
    else:
        go_to(chase_tail())
    avoid_snakes()
    corners()
    walls()


    #compare directions list with ranked directions and if ranked direction[0] is in directions go that direction
    #try:
    #    direction = random.choice(directions)
    #except:
    #    direction = random.choice(['up', 'down', 'left', 'right'])

    #Make this bit of code selecting from the different lists a function?
    #second direction didnt work
    if len(ranked_direction) != 0:
        for possible_dir in directions:
            if possible_dir == ranked_direction[0]:
                direction = ranked_direction[0]
        if len(direction) == 0:                         #if no direction assigned yet (probs not the best way to do this)
            for possible_dir2 in directions:            #not 100% sure grabbing the 2nd ranked direction works
                if possible_dir2 == ranked_direction[1]:
                    direction = ranked_direction[1]
                else:
                    direction = random.choice(directions)
    else:
        direction = random.choice(directions)

    print "Directions: ", directions
    print "Ranked Directions: ", ranked_direction
    print "Choice: ", direction
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
