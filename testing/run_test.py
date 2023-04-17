import subprocess
import time
import random
import requests 
request_list=[100,200,300,350]



for request in request_list:

    total = 0
    f = open("time.txt", "w")
#f.write("Curre time: "+current_time+"\n")
    f.write(str(total)+"\n")
    f.close()
    command=""

    for c in range(0,request):
        command=command+"python upload_dum.py & "

    print("Run request #: "+str(request))
    #print(command)
    subprocess.run(command, shell=True)



    with open("time.txt") as log:
        for line in log:
            time=float(line)
            total+=time
        
    f = open("time_vote_v2.txt", "a")
    #f.write("Curre time: "+current_time+"\n")
    f.write(str(request)+" : "+str(total)+"\n")
    f.close()        
        
