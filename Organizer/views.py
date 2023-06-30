from django.shortcuts import render,redirect
from Guest.models import *
from Organizer.models import *
import networkx as nx
from Organizer import custom_filters
# Create your views here.
def home(request):
    if 'oid' in request.session:
        orgdata=organiser.objects.get(id=request.session["oid"])
        evendata=event.objects.filter(org=orgdata)
        return render(request,"Organizer/Home.html",{'data':evendata})
    else:
        return redirect("Guest:login")

def events(request):
    if 'oid' in request.session:
        if request.method=="POST":
            data=organiser.objects.get(id=request.session["oid"])
            event.objects.create(code=request.POST.get('txtcode'),rooms=request.POST.get('txtn'),org=data)
            counts=int(request.POST.get('txtn'))
            eventid=event.objects.filter(org=data).last()
            ids=eventid.id
            for i in range(1,counts+1):
                room.objects.create(number=i,events=eventid)
            request.session["events"]=ids
            return redirect("org:group")
        else:
            return render(request,"Organizer/Event.html")
    else:
        return redirect("Guest:login")

def group(request):
    eventadta=event.objects.get(id=request.session["events"])
    roomdata=room.objects.filter(events=eventadta)
    if request.method=="POST":
        return render(request,"Organizer/Group.html",{'mess':1})
    else:
        return render(request,"Organizer/Group.html",{'room':roomdata})

def capacity(request):
    data=request.GET.get('did')
    cap,gp=data.split(",")
    roomdata=room.objects.get(id=gp)
    roomdata.capacity=cap
    roomdata.save()
    return redirect("org:group")

def eventview(request,eid):
    data=event.objects.get(id=eid)
    return render(request,"Organizer/eventview.html",{'data':data})

def editevent(request,eid):
    data=event.objects.get(id=eid)
    if request.method=="POST":
        data.code=request.POST.get('txtcode')
        data.save()
        return redirect("org:home")
    else:
        return render(request,"Organizer/editevent.html",{'data':data})

def finishevent(request,eid):
    data=event.objects.get(id=eid)
    data.status=1
    data.save()
    return redirect("org:home")

def logout(request):
    del request.session["oid"]
    return redirect("Guest:home")
def allocate_groups(request,did):
    participents={}
    groups = {}
    mylist=[]
    eventdata=event.objects.get(id=did)
    eventdata=event.objects.get(id=did)
    pdatacount=participateuser.objects.filter(events=eventdata).count()
    if pdatacount>0:
        pdata=participateuser.objects.filter(events=eventdata)
        roomsdata=room.objects.filter(events=eventdata)
        for i in roomsdata:
            
            groups['Group'+str(i.number)]=i.capacity
        
        for  i in pdata:
            mylist=i.rooms.split(",")
            leng=len(mylist)
            for j in range(0,leng):
                mylist[j]="Group"+mylist[j]
            participents[i.user]=mylist
        print(groups)
        print(participents)
        B = nx.Graph()
        B.add_nodes_from(participents.keys(), bipartite=0)
        B.add_nodes_from(groups.keys(), bipartite=1)


        for participent_name, participent_groups in participents.items():
            for group_name in participent_groups:
                B.add_edge(participent_name, group_name, weight=1)
        
        matching = nx.bipartite.maximum_matching(B, top_nodes=participents.keys())

        allocations = {}
        for participent_name, group_name in matching.items():
            if group_name not in allocations:
                allocations[group_name] = []
            allocations[group_name].append(participent_name)
        
        for group_name, participents in allocations.items():
        
            print(f" - {participent_name}-{group_name}")
            print()
        
        
        return render(request,"Organizer/ViewPart.html",{'data':allocations,'room':roomsdata})
    else:
        return render(request,"Organizer/ViewPart.html")
    
    
    # eventdata=event.objects.get(id=did)
    # roomdata=room.objects.filter(events=eventdata)
    
    # print(groups)
    # return render(request,"Organizer/Home.html")
    

    