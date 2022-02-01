#!/usr/bin/python3

# import socket
import threading
import socketserver

import numpy as np

def calc_bounding_rectangle_area(person_coords):
  if type(person_coords) == list:
    person_coords = person_coords[0]


  # assuming upper left is 0,0
  left_x = 999999
  right_x = 0
  top_y = 999999
  bot_y = 0

  for coord in person_coords:
    x,y = coord
    
    if x==-1 or y==-1:
      continue

    if x < left_x:
      left_x = x
    if x > right_x:
      right_x = x
    if y < top_y:
      top_y = y
    if y > bot_y:
      bot_y = y
  return (right_x - left_x) * (bot_y - top_y)

def choose_largest_person(people_coords):
  # dumb method to calc largest person by largest bounding rectangle area.
  # future methods should consider scale and joint distance
  if len(people_coords) == 0:
    return None, 0
  elif len(people_coords) == 1:
    return people_coords, calc_bounding_rectangle_area(people_coords)
  else:
    max_idx = 0
    max_area = 0
    for idx, person_coords in enumerate(people_coords):
      person_area = calc_bounding_rectangle_area(person_coords)
      if person_area > max_area:
        max_area = person_area
        max_idx = idx
    return people_coords[max_idx], max_area

def get_closest_to_center(person_coords):
  if type(person_coords) == list:
    x = person_coords[0]
  else:
    x = person_coords
  if x[17,0] != -1:
    return x[17]
  else:
    return [0,0]

def get_closest_to_center_overkill(person_coords):

  #### return 80% of shoulder to neck distance if data exists ####
  # print(type(person_coords))
  if type(person_coords) == np.ndarray:
    x = person_coords[0]
  else:
    x = person_coords
  center_frame_coord = [3264 / 2, 2464 / 2]

  todo = [0,0]
  
  # print(x[0])

  # check if neck data exists
  if x[17,0]!=-1:
    # return neck as todo for now until future work done
    todo = x[17]
    if x[5,0]!=-1:    # check if left shoulder exists
      return todo # return coord 80% of shoulder to neck dist orthogonal start from neck
    elif x[6,0]!=-1:  # check if right should exists
      return todo # return coord 80% of shoulder to neck dist orthogonal start from neck
    elif x[0,0]!=1:   # check if nose exists
      return todo # return coord 80% of nose to neck dist in line with vector from nose to neck
    else:
      return x[17] # just return neck if no other info
      
  # otherwise check if nose data and eye data exists
  elif x[0,0]!=-1 and x[1,0]!=-1 and x[2,0]!=-1:
    todo = x[0] # make todo nose for now
    return todo # 3* eye-to-eye distance in vector perpendicular to midpoint of eyes towards nose direction
  else:
    #return center frame coordinate? or maybe a null assuming can be handled upstream
    return center_frame_coord

def dist_between_points(point1, point2):
  diff = point1 - point2
  return np.sqrt(np.dot(diff.T, diff))


def parse_byte_string_msg(byte_str):
  ''' 
  to be replaced once i switch to a more data efficient (and cpu efficient) struct method.
  but for now here we are because it was faster to develop. this is why we can't have nice things
  '''
  msg = byte_str.decode("utf-8") 
  # print(f'got message: {msg}\n')
  
  # msg = '[(200,66),(253,9),(-1,-1),(517,16),(-1,-1),(805,271),(325,321),(1147,473),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(555,294),]\
  # [(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(201,865),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),]'

  spl = msg.split('[')
  # isolate people strings
  people = [x[:x.find(']')].strip(',') for x in spl[1:]]
  people_coords = []
  for person in people:
    no_parens = [x.strip('),') for x in person.split('(')[1:] ]
    coords = np.array( [np.fromstring(x,dtype=int,sep=',') for x in no_parens] )
    if type(coords) != np.ndarray:
      coords = coords[0]
    people_coords.append(coords)

  
  # for person_coords in people_coords:
  #   print(person_coords)
  
  

  largest_person_coords, largest_bbox_area = choose_largest_person(people_coords)
  # print('largeset person coords: ')
  # print(largest_person_coords)
  frame_w, frame_h = 3264, 2464
  area_thresh = frame_w * frame_h / 25 #(frame_w / 8) * (frame_h / 8)
  if largest_bbox_area > area_thresh:
    centercoord = get_closest_to_center(largest_person_coords)
    print(f'center coord: {centercoord}')
  else:
    print('')

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print(f'client {self.client_address}\n\twrote {data}\n\tto {self.server.server_address}')

        # send to another function for handling
        parse_byte_string_msg(data)

        # send back message in uppercase as confirmation (comment out if not needed)
        socket.sendto(data.upper(), self.client_address)

def start_udpserv(port=6969):
  with socketserver.UDPServer(('127.0.0.1', port), MyUDPHandler) as server:
    print(f'now listening on {server.server_address}')
    server.serve_forever()


# test here
#testmsg =  b'[(801,374),(937,310),(769,325),(1176,439),(-1,-1),(1515,859),(751,1039),(2127,1261),(618,1615),(1707,2114),(197,1786),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(1131,950),]'
# testmsg = b'[(715,201),(-1,-1),(-1,-1),(1200,88),(-1,-1),(1594,677),(555,769),(2006,1397),(433,1516),(1936,1966),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(1074,722),]\n[(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(342,1722),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),]'
# parse_byte_string_msg(testmsg)
# exit(1)

# create udp server for each port in port_list
port_list = [6969]
threads = [threading.Thread(target=start_udpserv, args=(p,)) for p in port_list]

# start threads to listen
print(f"running port listening on threads:\n\t{port_list}\n")
for t in threads:
  t.start()
