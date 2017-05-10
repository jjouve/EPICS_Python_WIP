#
# filename: CaChannel.py
# created : 07/25/99
# author  : Geoff Savage
#
# Wrapper class for EPICS channel access.
#
# 09/10/99 - Geoff Savage: Minimized interface.
# Instead of wrapping each caPython call, wrap the most generic calls.
# Implement more specific calls in Python as needed.
#

# Get the wrapped raw channel access calls
import ca
import time

# Exception string.  CaChannelException is thrown on errors along
# with an extra parameter, the CA status of the offending action.
CaChannelException = "CaChannelException"

class CaChannel:
# class timeout
    ca_timeout = 1.0	# in seconds

# Conversion dictionary.  A class variable. 
    dbr_d = {}

# Initialize conversion dictionary.  This is done once on import.
#	'c_type' = used with SWIG pointer library to allocate C space
#	'convert' = used to convert Python values to match the DBR_XXXX type
# Use the C type in the SWIG pointer library:
#	CaChannel.dbr_d[dbrType]['c_type']
# Use the converter to convert Python types
#	newValue = CaChannel.dbr_d[dbrType]['convert'](value)
    dbr_d[ca.DBR_SHORT] = \
		{'c_type' : "short",	# dbr_short_t
		 'convert' : int}
    dbr_d[ca.DBR_INT] = \
		{'c_type' : "short",		# dbr_int_t = dbr_short_t
		 'convert' : int}
    dbr_d[ca.DBR_LONG] = \
		{'c_type' : "int",		# dbr_long_t
		 'convert' : int}
    dbr_d[ca.DBR_FLOAT] = \
		{'c_type': "float",		# dbr_float_t
		 'convert' : float}
    dbr_d[ca.DBR_DOUBLE] = \
		{'c_type': "double",		# dbr_double_t
		 'convert' : float}
    dbr_d[ca.DBR_CHAR] = \
		{'c_type': "short",             # treat as an 8-bit field
		 'convert' : int}
    dbr_d[ca.DBR_STRING] = \
		{'c_type': "char",
		 'convert' : str}
    dbr_d[ca.DBR_ENUM] = \
		{'c_type': "short",
		 'convert' : int}
    def __init__(self):
	# Un-initialized channel id structure
	self.__chid = ca.new_chid()
	# Monitor event id
	self.__evid = None
	self.__timeout = None  # override g (class timeout)
	
    def __del__(self):
	# Clear the channel
	if (ca.state(self.__chid) == ca.cs_conn):
	    ca.clear_channel(self.__chid)
	    self.pend_io()
	# Release event id structure
	if (None != self.__evid):
	    ca.free_evid(self.__evid)
	ca.free_chid(self.__chid)

    def version(self):
        print "CaChannel, version v00-02-02"
#
# Class helper methods
#
    # Set the default timeout value.
    # Used by default if no timeout is specified where needed.
    def setTimeout(self, timeout):
	if ((timeout >= 0) or (timeout == None)):
	    self.__timeout = timeout
	else:
	    raise ValueError

    # Retrieve the default timeout value
    def getTimeout(self):
	return self.__timeout

    # Build and initialize a C array using the SWIG pointer library.
    # The Array length is keyed on the number of items in vals.
    # If EPICS array is longer than len(vals) the values at the
    # end will not be overwritten.
    def __build_array(self, vals, req_type):
	nitems = len(vals)
        print 'nitems =', nitems
	pvals = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'], 0, nitems)
	i = 0
	for item in vals:
	    ca.ptrset(pvals, CaChannel.dbr_d[req_type]['convert'](item), i)
	    i = i + 1
        print 'i=', i
	return pvals
	
    # Build and initialize a Python list from a SWIG pointer to a C array.
    def __build_list(self, pvals, nitems):
        l = []
	for i in range(0, nitems):
	    l.append(ca.ptrvalue(pvals, i))
	return l

    # Use the swig pointer library to allocate and initialize
    # C variables to hold the value to be written.
    def __setup_put(self, value, req_type):
	if(ca.DBR_STRING == req_type):
	    count = 1
	    length = len(str(value)) + 1  # space for string terminator
 	    pval = ca.captrcreate(CaChannel.dbr_d[req_type]['c_type'],
				CaChannel.dbr_d[req_type]['convert'](value),
				length)
#	elif(ca.DBR_CHAR == req_type):
#	    count = 1
# 	    pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'],
#				CaChannel.dbr_d[req_type]['convert'](value),
#				1)
	else:
	    count = self.element_count()
	    if (1 == count):
		pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'],
				    CaChannel.dbr_d[req_type]['convert'](value),
				    count)
	    else:
	        count = len(value)
		pval = self.__build_array(value, req_type)
	return count, pval

    # Use the swig pointer library to allocate C variables
    # to hold the data read.
    def __setup_get(self, req_type):
	if(ca.DBR_STRING == req_type):
	    count = 1	# each string is one element, never an array of strings
	    pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'], ' ', 1024)
#	elif(ca.DBR_CHAR == req_type):
#	    count = 1
#	    pval = ca.ptrcreate('int', 0, 1)
#	    pval = ca.ptrcreate('char', ' ', 2)
	else:
	    count = self.element_count()
	    pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'], 0, count)
	return count, pval


#
# *************** Channel access methods ***************
#

#
# Connection methods
#	search_and_connect
#	search
#	clear_channel
#

    def search_and_connect(self, pvName, callback, *user_args):
        args = (callback, user_args)   # user_args is a tuple
    	status = ca.search_and_connect(pvName, self.__chid, 0, args)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def search(self, pvName):
    	status = ca.search(pvName, self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def clear_channel(self):
	status = ca.clear_channel(self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Write methods
#	array_put
#	array_put_callback
#

    def array_put(self, value, req_type=None, count=None):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count, pval = self.__setup_put(value, req_type) # determine count
	else:
	    dummy, pval = self.__setup_put(value, req_type) # user count
	status = ca.array_put(req_type, count, self.__chid, pval)
	ca.ptrfree(pval)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def array_put_callback(self, value, req_type, count, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count, pval = self.__setup_put(value, req_type) # determine count
	else:
	    dummy, pval = self.__setup_put(value, req_type) # user count
        args = (callback, user_args)
	status = ca.array_put_callback(req_type, count, self.__chid, pval, 0, args)
	ca.ptrfree(pval)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Read methods
#	getValue
#	array_get
#	array_get_callback
#

    # Obtain read value after ECA_NORMAL is returned on an array_get().
    def getValue(self):
	try:
	    if(1 == self.getCount):
		retVal = ca.ptrvalue(self.getVal)
	    else:
		retVal = self.__build_list(self.getVal, self.getCount)
	    ca.ptrfree(self.getVal)
	    del self.getVal
	    del self.getCount
	    return retVal
	except NameError:
	    return None	

    # Value(s) read are placed in C variables and should not be accessed until
    # ECA_NORMAL is recived from pend_event().  Once this occurs use getValue()
    # to retrive the value(s) read.
    # SWIG pointers to the C variables are created here and used to retrieve
    # the value(s) in getValue().
    def array_get(self, req_type=None, count=None):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    self.getCount, self.getVal = self.__setup_get(req_type) # determine count
	else:
	    dummy, self.getVal = self.__setup_get(value, req_type) # user count
	    self.getCount = count
	status = ca.array_get(req_type, self.getCount, self.__chid, self.getVal)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(self.getVal)
	    raise CaChannelException, status

    def array_get_callback(self, req_type, count, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count = self.element_count()
        args = (callback, user_args)
	status = ca.array_get_callback(req_type, count, self.__chid, 0, args)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Event methods
#	add_masked_array_event
#	clear_event
#

    # Creates a new event id and stores it on self.__evid.  Only one event registered
    # per CaChannel object.  If an event is already registered the event is cleared
    # before registering a new event.
    def add_masked_array_event(self, req_type, count, mask, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count = self.element_count()
	if(None != self.__evid):
	    self.clear_event()
	    self.pend_io()
 	self.__evid = ca.new_evid()
        self.__args = (callback, user_args)
	status = ca.add_masked_array_event(req_type, count, self.__chid,
				0, self.__args, 0,0,0, self.__evid, mask)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def clear_event(self):
	status = ca.clear_event(self.__evid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
	ca.del_evid(self.__evid)
	self.__evid = None

#
# Execute methods
#	pend_io
#	test_io
#	pend_event
#	poll
#	flush_io
#

    def pend_io(self, timeout=None):
	if timeout is None:
	    if self.__timeout is None:
		timeout = CaChannel.ca_timeout
	    else:
		timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status


    def pend_event(self, timeout=None):
	if timeout is None:
	    timeout = 0.1
	status = ca.pend_event(timeout)
	return status

    def poll(self):
	status = ca.poll()
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def flush_io(self):
	status = ca.flush_io()
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Channel Access Macros
# Only macros that require the channel id as an argument.
#	field_type
#	element_count
#	name
#	state
#	host_name
#	read_access
#	write_access
#
    def field_type(self):
	return ca.field_type(self.__chid)

    def element_count(self):
        return ca.element_count(self.__chid)

    def name(self):
        return ca.name(self.__chid)

    def state(self):
	return ca.state(self.__chid)

    def host_name(self):
	return ca.host_name(self.__chid)

    def read_access(self):
	return ca.read_access(self.__chid)

    def write_access(self):
	return ca.write_access(self.__chid)

#
# Wait functions
#
# These functions wait for completion of the requested action.
#
    def searchw(self, pvName):
    	status = ca.search(pvName, self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def putw(self, value, req_type=None):
	if(None == req_type):
	    req_type = self.field_type()
	# strings - null terminated array of char
	# chars - null terminated char
	# values - one of a type or an array of types
        count, pval = self.__setup_put(value, req_type)
	status = ca.array_put(req_type, count, self.__chid, pval)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	ca.ptrfree(pval)

    def getw(self, req_type=None):
	if(None == req_type):
	    req_type = ca.field_type(self.__chid)
	count, pval = self.__setup_get(req_type)
	status = ca.array_get(req_type, count, self.__chid, pval)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if(1 == count):
	    value = ca.ptrvalue(pval)
	else:
	    value = self.__build_list(pval, count)
	ca.ptrfree(pval)
	return value






