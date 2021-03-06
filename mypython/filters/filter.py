class Filter:
    """Define a class filter to handle filter transmission curves"""

    def __init__(self,id=1):
        #filters are handled by ID in the master.FILTER.RES.info file
        self.id=id
        self.filter=None

    def loadtrans(self):
        """Function to load the desired transmission curve"""

        import os
        import numpy as np

        #load the info file  
        path=os.environ['MYPYTHON']
        fil=open(path+'/filters/data/master.FILTER.RES.info','r')
        fil_info=fil.readlines()
        fil.close()

        #get the start/end of the filter
        fields=fil_info[self.id-1].split()
        
        #read the actual filter file 
        data_start=int(fields[1].replace(":",""))
        data_end=int(fields[2])
        fil=open(path+'/filters/data/master.FILTER.RES','r')
        data=fil.readlines()[data_start:data_start+data_end-1]
        fil.close()

        #store in dictionary 
        wv=[]
        tr=[]
        for i in range(data_end-1):
            wv.append(float(data[i].split()[1]))
            tr.append(float(data[i].split()[2]))
            
        filter={'wave':np.array(wv),'tran':np.array(tr)}
        self.filter=filter    


        #import matplotlib.pyplot as plt    
        #plt.plot(filter['wave'],filter['tran'])
        #plt.show()


    def convolve(self,listin,wavein):

        """ Given an input listin,wavein, perform the intergal: 
            (int listin*filter*dl)/(int filter*dl) 

            The intergal is done where filter transmission >5d-4, or 
            where listin overlaps with filter (if smaller interval)

            Precision of integration is set to 1e-4.

        """      
      
        if (self.filter==None): 
            self.loadtrans()

        import numpy as np
        from scipy.interpolate import interp1d
        from scipy import integrate 
     
        #find absolute min/max for integration
        index=np.nonzero(self.filter['tran'] >= 5e-4)
        minwf=np.min(self.filter['wave'][index])
        maxwf=np.max(self.filter['wave'][index])
        minwl=np.min(wavein)
        maxwl=np.max(wavein)
        minint=np.max([minwl,minwf])
        maxint=np.min([maxwl,maxwf])

        
        print("Filter wave range ", minwf, maxwf)
        print("Data wave range ", minwl, maxwl)
        print("Actual integration ", minint, maxint)

        #create interpolation function 
        listint = interp1d(wavein,listin)
        filtint = interp1d(self.filter['wave'],self.filter['tran'])

        numer = integrate.quad(lambda x: listint(x)*filtint(x), minint, maxint, limit=100, epsabs=1e-4, epsrel=1e-4)
        denom = integrate.quad(lambda x: filtint(x), minint, maxint, limit=100,epsabs=1e-4, epsrel=1e-4)
        integ=numer[0]/denom[0]
        
        return integ
