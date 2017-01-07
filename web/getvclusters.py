
import sys
import atexit
import os
import time
import logging
import requests
import ssl 
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
requests.packages.urllib3.disable_warnings()


####################
def getcontent(name, user, passwd, resource, vcenter=None, uuid=None):
####################
   ''' 
    Get the vsphere object associated with a given text name
   ''' 
   if vcenter:
      s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
      s.verify_mode = ssl.CERT_NONE
      try:
         si = SmartConnect(host=vcenter, user=user, pwd=passwd)
      except IOError as e:
         si = SmartConnect(host=vcenter, user=user, pwd=passwd, sslContext=s)
      except:
         return ("Unable to connect to vsphere server. Error message:", sys.exc_info()[0])
      content = si.RetrieveContent()
      atexit.register(Disconnect, si)
      
      obj = get_obj(content=content, resource=resource, name=name, uuid=uuid)

      if obj:
         return obj
   return ("Could not located %s with name %s" % (resource, name)), ""
            
   
####################
def get_obj(content, resource, name=None, uuid=None):
####################

   view_ref = content.viewManager.CreateContainerView(container=content.rootFolder, type=[resource], recursive=True) 

   collector = content.propertyCollector

   # Create object specification to define the starting point of
   # inventory navigation
   obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
   obj_spec.obj = view_ref
   obj_spec.skip = True

   # Create a traversal specification to identify the path for collection
   traversal_spec = vmodl.query.PropertyCollector.TraversalSpec()
   traversal_spec.name = 'traverseEntities'
   traversal_spec.path = 'view'
   traversal_spec.skip = False
   traversal_spec.type = view_ref.__class__
   obj_spec.selectSet = [traversal_spec]

   # Identify the properties to the retrieved
   property_spec = vmodl.query.PropertyCollector.PropertySpec()
   property_spec.type = resource

   # Only vim.virtual machine have summry.config.instanceUUID
   if uuid:
      property_spec.pathSet = ["name","summary.config.instanceUuid"]
   else:
      property_spec.pathSet = ["name"]

   # Add the object and property specification to the
   # property filter specification
   filter_spec = vmodl.query.PropertyCollector.FilterSpec()
   filter_spec.objectSet = [obj_spec]
   filter_spec.propSet = [property_spec]

   # Retrieve properties
   props = collector.RetrieveContents([filter_spec])

   data = []
   for obj in props:
      properties = {}
      for prop in obj.propSet:
         properties[prop.name] = prop.val
         properties['obj'] = obj.obj

      data.append(properties)

   if name:
      for i in data:
         if i['name'] == name:
            return i['obj']
   elif uuid:
      for i in data:
         if i['summary.config.instanceUuid'] == uuid:
            return i['obj']
   else:
      return data

class getlist():
   def __init__(self):
      self.user = None
      self.passwd = None
      self.vcenter = None
      self.cluster = None
      self.cluslist = {}

   def getobj(self, res):
      obj = getcontent(name=None, user=self.user, passwd=self.passwd, resource=res, vcenter=self.vcenter)
      return obj
   
   def getclusterlist(self): 
      obj = self.getobj(vim.ClusterComputeResource)
      clus = []
      for c in obj:
         self.cluslist[c['name']] = c['obj']

      for key in self.cluslist:
         clus.append(key)

      return sorted(clus)

   def getdatacenter(self, cluster_nm): 
      cluster = self.cluslist[cluster_nm]
      return (cluster.parent).parent.name

   def getnetworklist(self, cluster_nm): 
      cluster = self.cluslist[cluster_nm]
      nics = []
      for i in cluster.network:
         nics.append(i.name)
      return sorted(nics)
   def getdatastorelist(self,cluster_nm): 
      cluster = self.cluslist[cluster_nm]
      dlist = []
      for s in cluster.datastore:
         dlist.append(s.name)
      return sorted(dlist)

   def storeuser(self, user):
      self.user = user

   def storepass(self, passwd):
      self.passwd = passwd

   def storevcenter(self, vcenter):
      self.vcenter = vcenter
