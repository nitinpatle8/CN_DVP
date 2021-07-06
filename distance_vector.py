import threading
import os
import time
import sys

buffer = [] # queue
events = {} 

def is_all_nbrs_sent_dvr(nbrs):
    status = True
    for i in nbrs :
        if nbrs[i] == 0:
            status = False
    return status 

def reset_nbrs(nbrs):
    for i in nbrs :
        nbrs[i] = 0
    
        
def task1(mat , costs , lock , router_names): 
    
    myRname = threading.current_thread().name
    dvr = {}    
    nbrs = []
    fwt_table = []
    mark_nbrs = {}
    nbrs_dvr = {}
    
    ##################### router initialization at  start 
    for i in router_names :
        dvr[i] = 1000
    
    dvr[myRname] = 0
    
    for i in costs :
        dvr[i] = costs[i]
        nbrs.append(i)
    ##############################################33   
      
    
    for itr in range(3):
        # send distance to every neighbour
        for i in nbrs :
            lock.acquire()
            fwt_table = [ myRname , i , dvr]
            buffer.append(fwt_table)        
            mark_nbrs[i] = 0
            lock.release()

	

        while is_all_nbrs_sent_dvr(mark_nbrs) == False :
            lock.acquire()           

            if len(buffer) > 0 :
                if buffer[0][1] == myRname :
                    mark_nbrs[ buffer[0][0]] = 1
                    nbrs_dvr[ buffer[0][0] ] = buffer[0][2]
                    buffer.pop(0)
                    lock.release()
                    if len(buffer) > 0 :
                        events[ buffer[0][1]].set()

                else :                
                    events[ buffer[0][1] ].set()
                    lock.release()
                    events[myRname].wait()





        lock.acquire()
        
        print("********************************** \n")        
        print(str(itr)+" : "+myRname)
        print(" my dvr")        
        print(dvr)
       
        print(" *******************************  \n")
        
        
        # updation  code dist vector : bellman  ford
        
        for i in dvr :
            for j in nbrs :
                if dvr[i] > mat[myRname][j] + nbrs_dvr[j][i] :
                    dvr[i] = mat[myRname][j] + nbrs_dvr[j][i]
            
        
        lock.release()

        time.sleep(5)
    
    

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
    router_names, path_costs = parseFile(filename)
    no_of_routers = len(router_names)
    print(router_names)
    print(path_costs)
    
    
    lock = threading.Lock()
    t = []  
    
    # MATRIX final path cost n*n
    mat = {}    
    for i in router_names :
        mat[i] = {}
        for j in router_names:
            mat[i][j] = 1000
            if i == j :
                mat[i][j] = 0
    
    
    
    for i in path_costs :
        for j in path_costs[i]:
            mat[i][j] =path_costs[i][j]
    
   
    
    
    for i in range(no_of_routers):
        t.append(threading.Thread(target=task1,args=(mat , path_costs[ router_names[i] ] , lock , router_names), name=router_names[i]))
        events[ router_names[i] ] = threading.Event() 
        
    for i in range(no_of_routers):
        t[i].start()
  
    for i in range(no_of_routers):
        t[i].join()
