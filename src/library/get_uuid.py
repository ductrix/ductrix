#!/usr/bin/python

import sys
import atexit
import os
import time
import logging
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect


####################
def getcontent(name, user, passwd, resource, vcenter=None, uuid=None):
####################
   ''' 
    Get the vsphere object associated with a given text name
   ''' 

   if vcenter:
      try:
#         print "host="+vcenter + ", user="+ user + ", pwd="+passwd
         si = SmartConnect(host=vcenter, user="{0}".format(user), pwd="{0}".format(passwd))
      except IOError, e:
         sys.exit("Unable to connect to vsphere server. Error message: %s" % e)
      atexit.register(Disconnect, si)
      content = si.RetrieveContent()
      root_folder = si.content.rootFolder
      for data_center in root_folder.childEntity:
        search_index = si.content.searchIndex
        return search_index.FindAllByDnsName(data_center, name)
      
#      print "content="+content+", resource="+resource+", name="+name+", uuid="+uuid
      obj = get_obj(content=content, resource=resource, name=name, uuid=uuid)

      if obj:
         return v, obj, content
            
   
####################
def get_obj(content, resource, name=None, uuid=None):
####################

   view_ref = content.viewManager.CreateContainerView(container=content.rootFolder, type=resource, recursive=True) 

   # convert list to variable
   for i in resource:  
      obj_type = i 
      break

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
   property_spec.type = obj_type

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


print getcontent(sys.argv[1], 'vsphere.local\\administrator', 'Ram1sita!', vim.VirtualMachine, vcenter='192.168.1.160', uuid=None)
