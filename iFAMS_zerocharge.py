import numpy as np
import matplotlib.pyplot as mp
import os
import argparse
import ast
from scipy import interpolate as interpolate


###### system arguments ################
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="name of the file")
ap.add_argument("-cs", "--charge_states", required=True, help="the charge states")
ap.add_argument("-f", "--flipped", default = "no", help="x and y flipped??")


args = vars(ap.parse_args())
###### system arguments ################

chargestatesr= ast.literal_eval(args["charge_states"]) #the charge states
file_name = args["input"]
namebase = os.path.splitext(file_name)[0]
xfull = []
yfull = []
# 
# I notice you call range(0,len(l)) a lot and it is unnecessary as python handles list iteration for you.
# Try this instead:
#   chargestateints = [int(chargestate) for chargestate in chargestatesr]
chargestateints = [int(chargestatesr[i]) for i in range(0,len(chargestatesr))]

######### opens each ifft file, and makes one list of lists composed of all of the files ###################
# Try this instead:
#   for chargestate in chargestatesr:
# but it's not clear to me why you are iterating over one list and then using values for the other parallel list.
# is it really necessary to have two parallel lists? maybe you could just to the float(?)->int()->str() conversion
# inline?
for i in range (0,len(chargestatesr)):
    ifftfilename = 0
    iftstring = "IFFT"
    ifftfilename = namebase + iftstring + str(chargestateints[i]) + ".csv"
    f = open(ifftfilename, 'r')
    if args["flipped"] == "yes":
        y,x = np.loadtxt(f,
                          unpack=True,
                          delimiter=',')
    else:
        x,y = np.loadtxt(f,
                          unpack=True,
                          delimiter=',')
    xfull.append(x)
    yfull.append(y)
######### opens each ifft file, and makes one list of lists composed of all of the files ###################


######### makes files the same size, although this should be the case if you're using the files from iFAMS##
MaxLenX = []
for i in range (0,len(xfull)):
    MaxLenXtemp = len(xfull[i])
    MaxLenX.append(MaxLenXtemp)

MaxLenXFin = max(MaxLenX)

for i in range (0,len(xfull)):

    if len(xfull[i]) != MaxLenXFin:
        space = (max(xfull[i])-min(xfull[i]))/len(xfull[i])
        extra = float(MaxLenXFin-len(xfull[i]))
        print (space*extra)
        add = (max(xfull[i])+(space*extra)+space)
        new = np.linspace(max(xfull[i])+space,(max(xfull[i])+(space*extra)),extra)
        xfull[i] = np.append(xfull[i],new)
        newY = np.zeros(int(extra))
        yfull[i]= np.append(yfull[i],newY)
    else:
        continue
######### makes files the same size, although this should be the case if you're using the files from iFAMS##


######### multiplies each x component by its charge state #############################
for i in range (0,len(xfull)):
    for j in range (0,len(xfull[0])):
        xfull[i][j] = chargestatesr[i] * xfull[i][j]
######### multiplies each x component by its charge state #############################

######### interpolates that data to make them equally spaced ##########################
xnewfinal = []
ynewfinal = []
for i in range (0,len(xfull)):
    datainterpolation = interpolate.InterpolatedUnivariateSpline(xfull[i], yfull[i], k=3)
    xnew = np.linspace(np.min(xfull[i]), np.max(xfull[i]), np.size(xfull), endpoint=True) #number of equally-spaced m/z
                                                                                          #values is equal to number of
                                                                                          # m/z values in original data
    xnewfinal.append(xnew)
    ynew = datainterpolation(xnew)
    ynewfinal.append(ynew)
######### interpolates that data to make them equally spaced ##########################


######### creates range in 10's for the entire zero charge spectrum ######
xmax = []
xmin = []
for i in range (0,len(xnewfinal)):
    xmax.append(xnewfinal[i][-1]/10)
    xmin.append(xnewfinal[i][0]/10)
xmaxfinal = (np.ceil(xmax))*10
xminfinal = (np.floor(xmin))*10
xrange = np.arange((min(xminfinal)),(max(xmaxfinal)+10),10)
######### creates range in 10's for the entire zero charge spectrum ######

########### creates charge specific x axis in 10's for each charge state###########
xrangespec = []
xmin = np.floor(xmin)*10
xmax = np.ceil(xmax)*10
yrangespec = []
for i in range (0,len(xmin)):
    xrangespectemp = np.arange(xmin[i],xmax[i]+10,10)
    xrangespec.append(xrangespectemp)
for i in range (0,len(xrangespec)):
    datainterpolation = interpolate.InterpolatedUnivariateSpline(xfull[i], yfull[i], k=3)
    yrangespectemp = datainterpolation(xrangespec[i])
    yrangespec.append(yrangespectemp)
########### creates charge specific x axis in 10's fir each charge state###########

####### places a zero if the data is outside the range of the original charge state specific spectrum #######
for i in range (0,len(xrangespec)):
    Ytempnum = (max(xrange)-max(xrangespec[i]))/10
    yzerosright = np.zeros(int(Ytempnum))
    yrangespec[i] = np.append(yrangespec[i],yzerosright)
    Ytempnum2 = (min(xrangespec[i])-min(xrange))/10
    yzerosleft = np.zeros(int(Ytempnum2))
    yrangespec[i] = np.append(yzerosleft,yrangespec[i])
    mp.plot(xrange,yrangespec[i],label=chargestateints[i])
yfinal =np.zeros(len(yrangespec[0]))
for i in range(len(yrangespec)):
    yfinal += yrangespec[i]
####### places a zero if the data is outside the range of the original charge state specific spectrum #######

for i in range (0, len(chargestateints)):
    ifftfilename = 0
    iftstring = "zerocharge"
    ifftfilename = namebase + iftstring + str(chargestateints[i]) + ".csv"
    ifftforexport = 0
    ifftforexport = np.transpose([xrange,yrangespec[i]])
    np.savetxt(ifftfilename,ifftforexport,fmt='%10.6f', delimiter=',') #outputs each charge-state-specific spectrum to
                                                                       # its own csv file
    print("file was exported")
ifftfilename = 0
iftstring = "zerocharge"
ifftfilename = namebase + iftstring + ".csv"
ifftforexport = 0
ifftforexport = np.transpose([xrange,yfinal])
np.savetxt(ifftfilename,ifftforexport,fmt='%10.6f', delimiter=',')
mp.plot(xrange,yfinal,label="zero charge spectrum")
mp.legend(loc='upper right', title='Charge State')
mp.show()







