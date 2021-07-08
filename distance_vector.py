import threading
import os
import time
import sys

buffer = [] # this buffer will be shared 
events = {} 

# used in target
# nbrs -> neighbours
# if all neighbours send their distance vector then return True else False
def is_all_nbrs_sent_dvr(mark_nbrs):
    status = True
    for i in mark_nbrs :
        if mark_nbrs[i] == 0:
            status = False
    return status 

# reset all nbrs

def reset_nbrs(nbrs):
    for i in nbrs :
        nbrs[i] = 0
    
# target of threads 

def task1(mat , costs , lock , router_names): 
    
    # router name 
    myRname = threading.current_thread().name

    # distance vector of this router contains all router list  e.g. for 'A' {'A': 0, 'B': 5, 'C': 7, 'D': 1000, 'E': 1000}
    dvr = {}    
    # nbrs is a list of router names which contains router names of the current router 
    nbrs = []
    # forwarding table is a list of router name, the neighbour to which it is sent, distance vector
    fwt_table = []
    
    mark_nbrs = {}
    # mark neighbours
    nbrs_dvr = {}
    
    ## router initialization at  start 
    for i in router_names :
        dvr[i] = 1000
    
    # self distance is 0
    dvr[myRname] = 0
    
    for i in costs:
        # initial values  in cost 
        dvr[i] = costs[i]
        # whichever router are present in costs those will be neighbours eg ['D', 'C']
        nbrs.append(i)


    # 3 epochs 
    for itr in range(3):
        # send distance to every neighbour
        for i in nbrs :
            # myroutername, neighbour name, distance vector of my router
            fwt_table = [myRname, i, dvr]

            lock.acquire()
            # critical section
            # buffer is a shared queue
            buffer.append(fwt_table)        
            lock.release()

        
            mark_nbrs[i] = 0


        while is_all_nbrs_sent_dvr(mark_nbrs) == False :
            
            lock.acquire()           

            if len(buffer) > 0 :
                # buffer[0] will be forwarding table/routing table
                # if buffer[0] is meant for my router
                # then mark neighbour 1 
                # buffer[0][0] will be router name who is sending forwarding table 
                # buffer[0][1] is router to which its distance vector is sent
                if buffer[0][1] == myRname :
                    # mark the neighbour
                    mark_nbrs[ buffer[0][0]] = 1
                    # assign distance vector to nbrs_dvr
                    nbrs_dvr[ buffer[0][0] ] = buffer[0][2]
                    buffer.pop(0)
                    lock.release()
                    if len(buffer) > 0 :
                        # my router name
                        events[buffer[0][1]].set()

                else :    
                    # not my name so set event of the corresponding router            
                    events[ buffer[0][1] ].set()
                    lock.release()
                    events[myRname].wait()


        lock.acquire()
        
        # print("********************************** \n")        
        print(str(itr)+" : "+myRname)
        print("distance vector of this Router")        
        print(dvr)
       
        print(" *******************************  \n")
        
        lock.release()
        # updation  code dist vector : bellman  ford
        
        # dvr - distance vector of my router
        for i in dvr :
            for j in nbrs :
                if dvr[i] > mat[myRname][j] + nbrs_dvr[j][i] :
                    dvr[i] = mat[myRname][j] + nbrs_dvr[j][i]
            
        

        time.sleep(2)
    
    

def parseFile(filename):
    routers_count = 0
    router_names = []
    path_costs = {}
    
    file = open(filename, 'r')
    line_no = 0

    for line in file:
        line_no += 1
        inputs = line.split()

        if line_no == 1:
            routers_count = int(inputs[0])
        elif line_no == 2:
            router_names = inputs.copy()
            for r in router_names:
                path_costs[r] = {}
        else:
            if len(inputs) > 1:

                if inputs[0] in path_costs:
                    path_costs[inputs[0]][inputs[1]] = int(inputs[2])
                
                if inputs[1] in path_costs:
                    path_costs[inputs[1]][inputs[0]] = int(inputs[2])

            elif inputs[0] == "EOF":
                break

    file.close()
    return router_names, path_costs
  

if __name__ == "__main__":
    
    filename = sys.argv[1]

    # router_names is a list of router names
    # path_costs is a dictionary of distance cost eg {'A':{'B': 5, 'C': 7}}
    router_names, path_costs = parseFile(filename)

    no_of_routers = len(router_names)   
    
    # lock 
    lock = threading.Lock()

    # t is a list of threads

    t = []  
    
    # MATRIX final path cost n*n
    # its a dictionary mapping eg {'A': {'A': 0, 'B': 1000, 'C':1000, 'E': 1000}, 'B': ....}
    mat = {}    
    for i in router_names :
        mat[i] = {}
        for j in router_names:
            mat[i][j] = 1000
            if i == j :
                mat[i][j] = 0
    
    # initialize mat with given costs 
    for i in path_costs :
        for j in path_costs[i]:
            mat[i][j] =path_costs[i][j]
    
    # create threads and events 
    # arguments to the thread are 
    #      |   |    |   |
    #      |   |    |    o ---- mat(our matrix which denotes all costs)
    #      |   |    o--------------pathcost of that router to all routers
    #      |   o---------------------lock
    #      o----------------------------router_names
    # argument to thread is also passed for thread name (identifying name of the router)

    for i in range(no_of_routers):
        # giving names to each thread as routers have names
        # name can be used as an identifier
        t.append(threading.Thread(target=task1,args=(mat , path_costs[ router_names[i] ] , lock , router_names), name=router_names[i]))
        events[ router_names[i] ] = threading.Event() 
        
    for i in range(no_of_routers):
        t[i].start()
  
    for i in range(no_of_routers):
        # if not join then program will exit without exiting the thread 
        t[i].join()
