/*
 * filename: ca_internal_functions.c
 * created : 07/26/99
 * author  : Geoff Savage
 *
 * modified: 02/17/00 V.Sirotenko, add DBR_GR, _CTRL and _TIME data types
 *
 * Functions needed to implement EPICS channel access in python.
 * These functions are only used internally to the wrapped functions.
 * Callbacks and data conversion.
 *
Callback documentation:
EPICS CA functions that utilize callbacks specify two pieces of data:
	1. The callback function to call
	2. User data to pass to the callback function
The goal is to allow a user to write callback functions in Python.  Since C
doesn't understand how to call a Python function we must put a layer between the
CA callback mechanism and Python.  The layer functions are:
	1. connectCallback
	2. putCallaback
	3. getCallaback
These functions are forced to be called in ca.i.

Each function must:
	1. Retrieve the function to be called.
	2. Build a dictionary of the return values.
	3. Put the dictionary and user values together in a tuple.
	4. Call the function with the tuple as an argument
 */

#define DEBUG
 
/* Dictionary Macros*/
#define PV_STATUS	"pv_status"
#define PV_SEVERITY	"pv_severity"
#define PV_VALUE	"pv_value"

#define	PV_UNITS		"pv_units"
#define	PV_UPDISLIM		"pv_updislim"
#define	PV_LODISLIM		"pv_lodislim"
#define	PV_UPALARMLIM	"pv_upalarmlim"
#define	PV_LOALARMLIN	"pv_loalarmlim"
#define	PV_UPWARNLIM	"pv_upwarnlim"
#define	PV_LOWARNLIM	"pv_lowarnlim"
#define	PV_RISCPAD		"pv_riscpad"
#define	PV_RISCPAD0		"pv_riscpad0"
#define PV_PRECISION	"pv_precision"			
#define PV_NOSTRINGS    "pv_nostrings"
#define PV_STATESTRINGS "pv_statestrings"
#define	PV_UPCTRLLIM    "pv_upctrllim"
#define PV_LOCTRLLIM	"pv_loctrllim"
#define	PV_SECONDS      "pv_seconds"
#define PV_NSECONDS		"pv_nseconds"

#define GET_STATUS	"status"
#define GET_TYPE	"type"
#define GET_COUNT	"count"
#define GET_CHID	"chid"

#define STR_LEN		128

/*
struct	connection_handler_args{
	struct channel_in_use	*chid;	Channel id
	long			op;	External codes for CA op
};
*/
void connectCallback(struct connection_handler_args connect_args)
{
    PyObject *func, *args, *retVals, *val;
    PyObject *pyTup, *result;
    char _ptemp[STR_LEN];
    
#ifdef DEBUG
    switch(connect_args.op){
        case CA_OP_CONN_UP:
	    printf("connectCallback: Connected\n");
	    break;
        case CA_OP_CONN_DOWN:
	    printf("connectCallback: Disconnected\n");
	    break;
	default:
	    printf("connectCallback: Unknown connection transition\n");
    }
#endif

    /* Create a swigged pointer to the channel identifier */
    SWIG_MakePtr(_ptemp, (char *) &(connect_args.chid), "_chid_p");
    /* Build a tuple of CA values to return to the callback routine */
    retVals = Py_BuildValue("(si)", _ptemp, connect_args.op);

    pyTup = (PyObject *) ca_puser(connect_args.chid);
    func = PyTuple_GetItem(pyTup, 0);
    if(2 == PyTuple_Size(pyTup))
	args = Py_BuildValue("(OO)", retVals, PyTuple_GetItem(pyTup, 1));
    else
	args = Py_BuildValue("(O)", retVals); /* no user arguments */
    result = PyEval_CallObject(func, args);
    if (NULL == result)
        printf("***** PyEval_CallObject failed *****\n");
    Py_XDECREF(args);
    Py_XDECREF(result);
    Py_XDECREF(pyTup);
    
} /* end connectCallback() */


/*
typedef struct	event_handler_args{
	void		*usr;	User argument supplied when event added
	struct channel_in_use *chid;	Channel id
	long		type;	the type of the value returned 
	long		count;	the element count of the item returned
	READONLY void	*dbr;	Pointer to the value returned
	int		status;	ECA_XXX Status of the requested op from server
};
*/

void putCallback(struct event_handler_args event_args)
{
    PyObject *func, *args, *retVals, *val;
    PyObject *pyTup, *result;
    char _ptemp[STR_LEN];
    
    /* Create a swigged pointer to the channel identifier */
    SWIG_MakePtr(_ptemp, (char *) &(event_args.chid), "_chid_p");
    /* Build a dictionary of CA values to return to the callback routine */
    retVals = Py_BuildValue("{s:s, s:i, s:i, s:i}",
    				GET_CHID, _ptemp,
				GET_TYPE, event_args.type,
    				GET_COUNT, event_args.count,
				GET_STATUS, event_args.status);
    pyTup = (PyObject *) event_args.usr;
    func = PyTuple_GetItem(pyTup, 0);
    if(2 == PyTuple_Size(pyTup))
	args = Py_BuildValue("(OO)", retVals, PyTuple_GetItem(pyTup, 1));
    else
	args = Py_BuildValue("(O)", retVals);
    /* Now that args references the dictionary remove the retVals reference.*/
    Py_XDECREF(retVals);
    result = PyEval_CallObject(func, args);
    if (NULL == result)
        printf("***** PyEval_CallObject failed *****\n");
    Py_XDECREF(args);
    Py_XDECREF(result);
    Py_XDECREF(pyTup);
    
} /* end putCallback() */



PyObject *
varToObject(void *pinData, chtype dbrType)
{
   PyObject *pyObj;
   
   switch(dbrType) {
      case DBR_STRING:
         pyObj = PyString_FromString((char *) pinData);
         break;
      case DBR_CHAR:
         pyObj = PyInt_FromLong((long) *((dbr_char_t *) pinData));
         break;
      case DBR_ENUM:
      case DBR_SHORT:
   /* case DBR_INT: Same as DBR_SHORT */
         pyObj = PyInt_FromLong((long) *((dbr_short_t *) pinData));
         break;
      case DBR_LONG:
         pyObj = PyInt_FromLong((long) *((dbr_long_t *) pinData));
         break;
      case DBR_FLOAT:
         pyObj = PyFloat_FromDouble((double) *((dbr_float_t *)pinData));
         break;
      case DBR_DOUBLE:
         pyObj = PyFloat_FromDouble((double) *((dbr_double_t *)pinData));
         break;
      default:
         printf("varToObject: Unknown DBR type\n");
   } /* end switch */

   return pyObj;

} /* end varToObject() */


PyObject *
arrayToTuple(int dbrType, int count, void *dataArray)
{
   int i;
   void *pData;
   PyObject *pyTup, *pyObj;
   
   pyTup = PyTuple_New(count);
   
   for (i=0; i<count; i++)
   {
      switch (dbrType) {
         case DBR_SHORT:
	    pData = &(((dbr_short_t *)dataArray)[i]);
	    break;
         case DBR_LONG:
	    pData = &(((dbr_long_t *)dataArray)[i]);
	    break;
         case DBR_FLOAT:
	    pData = &(((dbr_float_t *)dataArray)[i]);
	    break;
         case DBR_DOUBLE:
	    pData = &(((dbr_double_t *)dataArray)[i]);
	    break;
      }
      pyObj = varToObject(pData, dbrType);
      if (NULL == pyObj)
         return NULL;
      PyTuple_SetItem(pyTup, i, pyObj);
      Py_XDECREF(pyObj); /* tuple now owns the item */
   }

   return pyTup;
  
} /* end arrayToTuple() */



/*
	dbr_string_t		strval;		string max size	     
	dbr_short_t		shrtval;	short		     
	dbr_short_t		intval;		short		     
	dbr_float_t		fltval;		IEEE Float		     
	dbr_enum_t		enmval;		item number		     
	dbr_char_t		charval;	character		     
	dbr_long_t		longval;	long, no this is an int			     
	dbr_double_t		doubleval;	double		     
*/
PyObject *unpackPlainGet(union db_access_val *pBuf, chtype dbrType, int count)
{
    PyObject 	*d,   /* dictionary */
		*t,   /* tuple */
		*pyVal;
    int i;
    
    if(1==count) {
	switch (dbrType) {
	    case DBR_STRING:
	        d = Py_BuildValue("{s:s}", PV_VALUE, (char *)pBuf->strval);
	        break;
	    case DBR_CHAR:
		d = Py_BuildValue("{s:b}", PV_VALUE, (int)pBuf->charval);
		break;
	    /* case DBR_SHORT: = DBR_INT */
	    case DBR_INT:
		d = Py_BuildValue("{s:h}", PV_VALUE, (int)pBuf->intval);
		break;
	    case DBR_ENUM:
		d = Py_BuildValue("{s:h}", PV_VALUE, (int)pBuf->enmval);
		break;
	    case DBR_LONG:
		d = Py_BuildValue("{s:i}", PV_VALUE, (int)pBuf->longval);
		break;
	    case DBR_FLOAT:
		d = Py_BuildValue("{s:d}", PV_VALUE, (double)pBuf->fltval);
		break;
	    case DBR_DOUBLE:
		d = Py_BuildValue("{s:d}", PV_VALUE, (double)pBuf->doubleval);
		break;
	    default:
		printf("unpackPlainGet: Unknown DBR type\n");
	} /* end switch (requestType) */
    } /* end if */
    else {
	t = PyTuple_New(count);
        for(i = 0; i < count; ++i) {
	    switch (dbrType) {
		/* case DBR_STRING: No arrays of strings in EPICS*/
		case DBR_CHAR:
		    pyVal = Py_BuildValue("b", (int)*(&(pBuf->charval) + i));
		    break;
		/* case DBR_SHORT: = DBR_INT */
		case DBR_INT:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->intval) + i));
		    break;
		case DBR_ENUM:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->enmval) +i));
	    	    break;
		case DBR_LONG:
		    pyVal = Py_BuildValue("i", (int)*(&(pBuf->longval) + i));
		    break;
		case DBR_FLOAT:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->fltval) + i));
		    break;
		case DBR_DOUBLE:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->doubleval) + i));
		break;
	    } /* end switch */
	    PyTuple_SetItem(t, i, pyVal);
	    Py_XDECREF(pyVal);  /* tuple now references the value */
	} /* end for */
	d = Py_BuildValue("{s:O}", PV_VALUE, t);
	Py_XDECREF(t);  /* dictionary now references the tuple */
    } /* end else */
    return d;

}  /* end unpackPlainGet() */

/*
	struct dbr_sts_string	sstrval;	string field with status
	struct dbr_sts_short	sshrtval;	short field with status
	struct dbr_sts_float	sfltval;	float field with status
	struct dbr_sts_enum	senmval;	item number with status
	struct dbr_sts_char	schrval;	char field with status
	struct dbr_sts_long	slngval;	long field with status
	struct dbr_sts_double	sdblval;	double field with status

struct dbr_sts_string{
	dbr_short_t	status;	 		status of value
	dbr_short_t	severity;		severity of alarm
	dbr_string_t	value;			current value
};

*/

/* Take the data received from a status callback and unpack it.  */
/* This is messy because this callback must handle all the 
   channel access types.  */
PyObject *unpackStatusGet(union db_access_val *pBuf, chtype dbrType, int count)
{
    PyObject *d, *t, *pyVal;
    int i;
    
    if(1 == count) {
	switch(dbrType) {
	    case DBR_STS_STRING: /* sstrval */
		d = Py_BuildValue("{s:i, s:i, s:s}",
				PV_STATUS, (int)pBuf->sstrval.status,
				PV_SEVERITY, (int)pBuf->sstrval.severity,
				PV_VALUE, (char *)pBuf->sstrval.value);
	    break;
	    case DBR_STS_CHAR: /* schrval */
	        d = Py_BuildValue("{s:i, s:i, s:b}",
				PV_STATUS, (int)pBuf->schrval.status,
				PV_SEVERITY, (int)pBuf->schrval.severity,
				PV_VALUE, (int)pBuf->schrval.value);
	    break;
	    case DBR_STS_INT: /* sshrtval */
		d = Py_BuildValue("{s:i, s:i, s:h}",
				PV_STATUS, (int)pBuf->sshrtval.status,
				PV_SEVERITY, (int)pBuf->sshrtval.severity,
				PV_VALUE, (int)pBuf->sshrtval.value);
	    break;
	    case DBR_STS_ENUM: /* senmval */
		d = Py_BuildValue("{s:i, s:i, s:h}",
				PV_STATUS, (int)pBuf->senmval.status,
				PV_SEVERITY, (int)pBuf->senmval.severity,
				PV_VALUE, (int)pBuf->senmval.value);
	    break;
	    case DBR_STS_LONG: /* slngval */
		d = Py_BuildValue("{s:i, s:i, s:i}",
				PV_STATUS, (int)pBuf->slngval.status,
				PV_SEVERITY, (int)pBuf->slngval.severity,
				PV_VALUE, (int)pBuf->slngval.value);
	    break;
	    case DBR_STS_FLOAT: /* sfltval */
		d = Py_BuildValue("{s:i, s:i, s:d}",
				PV_STATUS, (int)pBuf->sfltval.status,
				PV_SEVERITY, (int)pBuf->sfltval.severity,
				PV_VALUE, (double)pBuf->sfltval.value);
	    break;
	    case DBR_STS_DOUBLE: /* sdblval */
		d = Py_BuildValue("{s:i, s:i, s:d}",
				PV_STATUS, (int)pBuf->sdblval.status,
				PV_SEVERITY, (int)pBuf->sdblval.severity,
				PV_VALUE, (double)pBuf->sdblval.value);
	    break;
	    default:  /* conversion not possible, failure */
		printf("unpackStatusGet: Unknown DBR type\n");

	} /* end switch(requestType) */
    } /* end if */
    else {
	switch(dbrType) {
	    case DBR_STS_STRING: /* sstrval */
		d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->sstrval.status,
				PV_SEVERITY, (int)pBuf->sstrval.severity);
	    break;
	    case DBR_STS_CHAR: /* schrval */
	        d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->schrval.status,
				PV_SEVERITY, (int)pBuf->schrval.severity);
	    break;
	    case DBR_STS_INT: /* sshrtval */
		d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->sshrtval.status,
				PV_SEVERITY, (int)pBuf->sshrtval.severity);
	    break;
	    case DBR_STS_ENUM: /* senmval */
		d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->senmval.status,
				PV_SEVERITY, (int)pBuf->senmval.severity);
	    break;
	    case DBR_STS_LONG: /* slngval */
		d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->slngval.status,
				PV_SEVERITY, (int)pBuf->slngval.severity);
	    break;
	    case DBR_STS_FLOAT: /* sfltval */
		d = Py_BuildValue("{s:i, s:i}",
				PV_STATUS, (int)pBuf->sfltval.status,
				PV_SEVERITY, (int)pBuf->sfltval.severity);
	    break;
	    case DBR_STS_DOUBLE: /* sdblval */
		d = Py_BuildValue("{s:i, s:i, s:d}",
				PV_STATUS, (int)pBuf->sdblval.status,
				PV_SEVERITY, (int)pBuf->sdblval.severity);
	    break;
	    default:  /* conversion not possible, failure */
		printf("unpackStatusGet: Unknown DBR type\n");

	} /* end switch(requestType) */
	t = PyTuple_New(count);
        for(i = 0; i < count; ++i) {
	    switch (dbrType) {
		/* case DBR_STRING: No arrays of strings in EPICS*/
		case DBR_STS_CHAR:
		    pyVal = Py_BuildValue("b", (int)*(&(pBuf->schrval.value) + i));
		    break;
		/* case DBR_SHORT: = DBR_INT */
		case DBR_STS_INT:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->sshrtval.value) + i));
		    break;
		case DBR_STS_ENUM:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->senmval.value) +i));
	    	    break;
		case DBR_STS_LONG:
		    pyVal = Py_BuildValue("i", (int)*(&(pBuf->slngval.value) + i));
		    break;
		case DBR_STS_FLOAT:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->sfltval.value) + i));
		    break;
		case DBR_STS_DOUBLE:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->sdblval.value) + i));
		break;
	    } /* end switch */
	    PyTuple_SetItem(t, i, pyVal);
	    Py_XDECREF(pyVal);  /* tuple now references the value */
	} /* end for */
	PyDict_SetItemString(d, PV_VALUE, t);
    } /* end else */

    return d;

}  /* end unpackStatusGet() */

/* Take the data received from a Status & Time callback and unpack it.  */
/* This is also messy because we must handle all the channel access types. */
PyObject *unpackTimeGet(union db_access_val *pBuf, chtype dbrType, int count)
{
    PyObject *d, *t, *pyVal;
    int i;
    
    if(1 == count) {
	switch(dbrType) {
		case DBR_TIME_STRING: /* tstrval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:i, s:i}",
				PV_STATUS, pBuf->tstrval.status,
				PV_SEVERITY, pBuf->tstrval.severity,
				PV_VALUE, pBuf->tstrval.value,
				PV_SECONDS, pBuf->tstrval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tstrval.stamp.nsec);
	    break;
	    case DBR_TIME_CHAR: /* tchrval */
			d = Py_BuildValue("{s:h, s:h, s:b, s:b, s:b, s:i, s:i}",
				PV_STATUS, pBuf->tchrval.status,
				PV_SEVERITY, pBuf->tchrval.severity,
				PV_VALUE, pBuf->tchrval.value,
				PV_RISCPAD0, pBuf->tchrval.RISC_pad0,
				PV_RISCPAD, pBuf->tchrval.RISC_pad1,
				PV_SECONDS, pBuf->tchrval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tchrval.stamp.nsec);
		break;
	    case DBR_TIME_SHORT: /* tshrtval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tshrtval.status,
				PV_SEVERITY, pBuf->tshrtval.severity,
				PV_VALUE, pBuf->tshrtval.value,
				PV_SECONDS, pBuf->tshrtval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tshrtval.stamp.nsec);
		break;
	    case DBR_TIME_FLOAT: /* tfltval */
			d = Py_BuildValue("{s:h, s:h, s:f, s:i, s:i}",
				PV_STATUS, pBuf->tfltval.status,
				PV_SEVERITY, pBuf->tfltval.severity,
				PV_VALUE, pBuf->tfltval.value,
				PV_SECONDS, pBuf->tfltval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tfltval.stamp.nsec);
		break;
	    case DBR_TIME_ENUM: /* tenmval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tenmval.status,
				PV_SEVERITY, pBuf->tenmval.severity,
				PV_VALUE, pBuf->tenmval.value,
				PV_RISCPAD, pBuf->tenmval.RISC_pad,
				PV_SECONDS, pBuf->tenmval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tenmval.stamp.nsec);
		break;
	    case DBR_TIME_LONG: /* tlngval */
			d = Py_BuildValue("{s:h, s:h, s:l, s:i, s:i}",
				PV_STATUS, pBuf->tlngval.status,
				PV_SEVERITY, pBuf->tlngval.severity,
				PV_VALUE, pBuf->tlngval.value,
				PV_SECONDS, pBuf->tlngval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tlngval.stamp.nsec);
		break;
	    case DBR_TIME_DOUBLE: /* tdblval */
			d = Py_BuildValue("{s:h, s:h, s:d, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tdblval.status,
				PV_SEVERITY, pBuf->tdblval.severity,
				PV_VALUE, pBuf->tdblval.value,
				PV_RISCPAD, pBuf->tdblval.RISC_pad,
				PV_SECONDS, pBuf->tdblval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tdblval.stamp.nsec);
		break;
	    default:  /* conversion not possible, failure */
		printf("unpackTimeGet: Unknown DBR type\n");

	} /* end switch(requestType) */
    } /* end if */
    else {
		switch(dbrType) {
		case DBR_TIME_STRING: /* tstrval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tstrval.status,
				PV_SEVERITY, pBuf->tstrval.severity,
				PV_SECONDS, pBuf->tstrval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tstrval.stamp.nsec);
	    break;
	    case DBR_TIME_CHAR: /* tchrval */
			d = Py_BuildValue("{s:h, s:h, s:b, s:b, s:i, s:i}",
				PV_STATUS, pBuf->tchrval.status,
				PV_SEVERITY, pBuf->tchrval.severity,
				PV_RISCPAD0, pBuf->tchrval.RISC_pad0,
				PV_RISCPAD, pBuf->tchrval.RISC_pad1,
				PV_SECONDS, pBuf->tchrval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tchrval.stamp.nsec);
		break;
	    case DBR_TIME_SHORT: /* tshrtval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tshrtval.status,
				PV_SEVERITY, pBuf->tshrtval.severity,
				PV_SECONDS, pBuf->tshrtval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tshrtval.stamp.nsec);
		break;
	    case DBR_TIME_FLOAT: /* tfltval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tfltval.status,
				PV_SEVERITY, pBuf->tfltval.severity,
				PV_SECONDS, pBuf->tfltval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tfltval.stamp.nsec);
		break;
	    case DBR_TIME_ENUM: /* tenmval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tenmval.status,
				PV_SEVERITY, pBuf->tenmval.severity,
				PV_RISCPAD, pBuf->tenmval.RISC_pad,
				PV_SECONDS, pBuf->tenmval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tenmval.stamp.nsec);
		break;
	    case DBR_TIME_LONG: /* tlngval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tlngval.status,
				PV_SEVERITY, pBuf->tlngval.severity,
				PV_SECONDS, pBuf->tlngval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tlngval.stamp.nsec);
		break;
	    case DBR_TIME_DOUBLE: /* tdblval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:i, s:i}",
				PV_STATUS, pBuf->tdblval.status,
				PV_SEVERITY, pBuf->tdblval.severity,
				PV_RISCPAD, pBuf->tdblval.RISC_pad,
				PV_SECONDS, pBuf->tdblval.stamp.secPastEpoch,
				PV_NSECONDS, pBuf->tdblval.stamp.nsec);
		break;
		default:  /* conversion not possible, failure */
		printf("unpackTimeGet: Unknown DBR type\n");
		} /* end switch(requestType) */
	t = PyTuple_New(count);
        for(i = 0; i < count; ++i) {
	    switch (dbrType) {
		/* case DBR_STRING: No arrays of strings in EPICS*/
		case DBR_TIME_CHAR:
		    pyVal = Py_BuildValue("b", (char)*(&(pBuf->gchrval.value) + i));
		    break;
		case DBR_TIME_SHORT:
		    pyVal = Py_BuildValue("h", (short)*(&(pBuf->gshrtval.value) + i));
		    break;
		case DBR_TIME_ENUM:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->genmval.value) +i));
	    	    break;
		case DBR_TIME_LONG:
		    pyVal = Py_BuildValue("i", (long)*(&(pBuf->glngval.value) + i));
		    break;
		case DBR_TIME_FLOAT:
		    pyVal = Py_BuildValue("f", (float)*(&(pBuf->gfltval.value) + i));
		    break;
		case DBR_TIME_DOUBLE:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->gdblval.value) + i));
		break;
	    } /* end switch */
	    PyTuple_SetItem(t, i, pyVal);
	    Py_XDECREF(pyVal);  /* tuple now references the value */
	} /* end for */
	PyDict_SetItemString(d, PV_VALUE, t);
    } /* end else */

    return d;

}  /* end unpackTimeGet() */

/* Take the data received from a Status & Graphic callback and unpack it.  */
/* This is also messy because we must handle all the channel access types. */
PyObject *unpackGraphicGet(union db_access_val *pBuf, chtype dbrType, int count)
{
    PyObject *d, *t, *pyVal;
    int i;
 
    if(1 == count) {
	switch(dbrType) {
		case DBR_GR_STRING: /* gstrval */
			d = Py_BuildValue("{s:h, s:h, s:s}",
				PV_STATUS, pBuf->gstrval.status,
				PV_SEVERITY, pBuf->gstrval.severity,
				PV_VALUE, pBuf->gstrval.value);
	    break;
	    case DBR_GR_CHAR: /* gchrval */
			d = Py_BuildValue("{s:h, s:h, s:b, s:s, s:b, s:b, s:b, s:b, s:b, s:b, s:b}",
				PV_STATUS, pBuf->gchrval.status,
				PV_SEVERITY, pBuf->gchrval.severity,
				PV_VALUE, pBuf->gchrval.value,
				PV_UNITS, pBuf->gchrval.units,
				PV_UPDISLIM, pBuf->gchrval.upper_disp_limit,
				PV_LODISLIM, pBuf->gchrval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gchrval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gchrval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gchrval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gchrval.lower_warning_limit,
				PV_RISCPAD, pBuf->gchrval.RISC_pad );
		break;
	    case DBR_GR_SHORT: /* gshrtval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:s, s:h, s:h, s:h, s:h, s:h, s:h}",
				PV_STATUS, pBuf->gshrtval.status,
				PV_SEVERITY, pBuf->gshrtval.severity,
				PV_VALUE, pBuf->gshrtval.value,
				PV_UNITS, pBuf->gshrtval.units,
				PV_UPDISLIM, pBuf->gshrtval.upper_disp_limit,
				PV_LODISLIM, pBuf->gshrtval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gshrtval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gshrtval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gshrtval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gshrtval.lower_warning_limit );
		break;
	    case DBR_GR_FLOAT: /* gfltval */
			d = Py_BuildValue("{s:h, s:h, s:f, s:s, s:h, s:h, s:f, s:f, s:f, s:f, s:f, s:f}",
				PV_STATUS, pBuf->gfltval.status,
				PV_SEVERITY, pBuf->gfltval.severity,
				PV_VALUE, pBuf->gfltval.value,
				PV_UNITS, pBuf->gfltval.units,
				PV_PRECISION, pBuf->gfltval.precision,
				PV_RISCPAD0, pBuf->gfltval.RISC_pad0,
				PV_UPDISLIM, pBuf->gfltval.upper_disp_limit,
				PV_LODISLIM, pBuf->gfltval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gfltval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gfltval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gfltval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gfltval.lower_warning_limit );
		break;
	    case DBR_GR_ENUM: /* genmval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:h, s:s}",
				PV_STATUS, pBuf->genmval.status,
				PV_SEVERITY, pBuf->genmval.severity,
				PV_VALUE, pBuf->genmval.value,
				PV_NOSTRINGS, pBuf->genmval.no_str,
				PV_STATESTRINGS, pBuf->genmval.strs );
		break;
	    case DBR_GR_LONG: /* glngval */
			d = Py_BuildValue("{s:h, s:h, s:l, s:s, s:l, s:l, s:l, s:l, s:l, s:l}",
				PV_STATUS, pBuf->glngval.status,
				PV_SEVERITY, pBuf->glngval.severity,
				PV_VALUE, pBuf->glngval.value,
				PV_UNITS, pBuf->glngval.units,
				PV_UPDISLIM, pBuf->glngval.upper_disp_limit,
				PV_LODISLIM, pBuf->glngval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->glngval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->glngval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->glngval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->glngval.lower_warning_limit );
		break;
	    case DBR_GR_DOUBLE: /* gdblval */
			d = Py_BuildValue("{s:h, s:h, s:d, s:s, s:h, s:h, s:d, s:d, s:d, s:d, s:d, s:d}",
				PV_STATUS, pBuf->gdblval.status,
				PV_SEVERITY, pBuf->gdblval.severity,
				PV_VALUE, pBuf->gdblval.value,
				PV_UNITS, pBuf->gdblval.units,
				PV_PRECISION, pBuf->gdblval.precision,
				PV_RISCPAD0, pBuf->gdblval.RISC_pad0,
				PV_UPDISLIM, pBuf->gdblval.upper_disp_limit,
				PV_LODISLIM, pBuf->gdblval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gdblval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gdblval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gdblval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gdblval.lower_warning_limit );
		break;
	    default:  /* conversion not possible, failure */
		printf("unpackGraphicGet: Unknown DBR type\n");

	} /* end switch(requestType) */
    } /* end if */
    else {
		switch(dbrType) {
		case DBR_GR_STRING: /* gstrval */
			d = Py_BuildValue("{s:h, s:h}",
				PV_STATUS, pBuf->gstrval.status,
				PV_SEVERITY, pBuf->gstrval.severity);
	    break;
	    case DBR_GR_CHAR: /* gchrval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:b, s:b, s:b, s:b, s:b, s:b, s:b}",
				PV_STATUS, pBuf->gchrval.status,
				PV_SEVERITY, pBuf->gchrval.severity,
				PV_UNITS, pBuf->gchrval.units,
				PV_UPDISLIM, pBuf->gchrval.upper_disp_limit,
				PV_LODISLIM, pBuf->gchrval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gchrval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gchrval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gchrval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gchrval.lower_warning_limit,
				PV_RISCPAD, pBuf->gchrval.RISC_pad );
		break;
	    case DBR_GR_SHORT: /* gshrtval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:h, s:h, s:h, s:h}",
				PV_STATUS, pBuf->gshrtval.status,
				PV_SEVERITY, pBuf->gshrtval.severity,
				PV_UNITS, pBuf->gshrtval.units,
				PV_UPDISLIM, pBuf->gshrtval.upper_disp_limit,
				PV_LODISLIM, pBuf->gshrtval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gshrtval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gshrtval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gshrtval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gshrtval.lower_warning_limit );
		break;
	    case DBR_GR_FLOAT: /* gfltval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:f, s:f, s:f, s:f, s:f, s:f}",
				PV_STATUS, pBuf->gfltval.status,
				PV_SEVERITY, pBuf->gfltval.severity,
				PV_UNITS, pBuf->gfltval.units,
				PV_PRECISION, pBuf->gfltval.precision,
				PV_RISCPAD0, pBuf->gfltval.RISC_pad0,
				PV_UPDISLIM, pBuf->gfltval.upper_disp_limit,
				PV_LODISLIM, pBuf->gfltval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gfltval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gfltval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gfltval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gfltval.lower_warning_limit );
		break;
	    case DBR_GR_ENUM: /* genmval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:s}",
				PV_STATUS, pBuf->genmval.status,
				PV_SEVERITY, pBuf->genmval.severity,
				PV_NOSTRINGS, pBuf->genmval.no_str,
				PV_STATESTRINGS, pBuf->genmval.strs );
		break;
	    case DBR_GR_LONG: /* glngval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:l, s:l, s:l, s:l, s:l, s:l}",
				PV_STATUS, pBuf->glngval.status,
				PV_SEVERITY, pBuf->glngval.severity,
				PV_UNITS, pBuf->glngval.units,
				PV_UPDISLIM, pBuf->glngval.upper_disp_limit,
				PV_LODISLIM, pBuf->glngval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->glngval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->glngval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->glngval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->glngval.lower_warning_limit );
		break;
	    case DBR_GR_DOUBLE: /* gdblval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:d, s:d, s:d, s:d, s:d, s:d}",
				PV_STATUS, pBuf->gdblval.status,
				PV_SEVERITY, pBuf->gdblval.severity,
				PV_UNITS, pBuf->gdblval.units,
				PV_PRECISION, pBuf->gdblval.precision,
				PV_RISCPAD0, pBuf->gdblval.RISC_pad0,
				PV_UPDISLIM, pBuf->gdblval.upper_disp_limit,
				PV_LODISLIM, pBuf->gdblval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->gdblval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->gdblval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->gdblval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->gdblval.lower_warning_limit );
		break;
		default:  /* conversion not possible, failure */
		printf("unpackGraphicGet: Unknown DBR type\n");
		} /* end switch(requestType) */
	t = PyTuple_New(count);
        for(i = 0; i < count; ++i) {
	    switch (dbrType) {
		/* case DBR_STRING: No arrays of strings in EPICS*/
		case DBR_GR_CHAR:
		    pyVal = Py_BuildValue("b", (char)*(&(pBuf->gchrval.value) + i));
		    break;
		case DBR_GR_SHORT:
		    pyVal = Py_BuildValue("h", (short)*(&(pBuf->gshrtval.value) + i));
		    break;
		case DBR_GR_ENUM:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->genmval.value) +i));
	    	    break;
		case DBR_GR_LONG:
		    pyVal = Py_BuildValue("i", (long)*(&(pBuf->glngval.value) + i));
		    break;
		case DBR_GR_FLOAT:
		    pyVal = Py_BuildValue("f", (float)*(&(pBuf->gfltval.value) + i));
		    break;
		case DBR_GR_DOUBLE:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->gdblval.value) + i));
		break;
	    } /* end switch */
	    PyTuple_SetItem(t, i, pyVal);
	    Py_XDECREF(pyVal);  /* tuple now references the value */
	} /* end for */
	PyDict_SetItemString(d, PV_VALUE, t);
    } /* end else */

    return d;

}  /* end unpackGraphicGet() */

/* Take the data received from a status & graphic & control callback and unpack it.  */
/* This is also messy because we must handle all the channel access types. */
PyObject *unpackControlGet(union db_access_val *pBuf, chtype dbrType, int count)
{
    PyObject *d, *t, *pyVal;
    int i;
    if(1 == count) {
	switch(dbrType) {
		case DBR_CTRL_STRING: /* cstrval */
			d = Py_BuildValue("{s:h, s:h, s:s}",
				PV_STATUS, pBuf->cstrval.status,
				PV_SEVERITY, pBuf->cstrval.severity,
				PV_VALUE, pBuf->cstrval.value);
	    break;
	    case DBR_CTRL_CHAR: /* cchrval */
			d = Py_BuildValue("{s:h, s:h, s:b, s:s, s:b, s:b, s:b, s:b, s:b, s:b, s:b, s:b, s:b}",
				PV_STATUS, pBuf->cchrval.status,
				PV_SEVERITY, pBuf->cchrval.severity,
				PV_VALUE, pBuf->cchrval.value,
				PV_UNITS, pBuf->cchrval.units,
				PV_UPDISLIM, pBuf->cchrval.upper_disp_limit,
				PV_LODISLIM, pBuf->cchrval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cchrval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cchrval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cchrval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cchrval.lower_warning_limit,
				PV_RISCPAD, pBuf->cchrval.RISC_pad,
				PV_UPCTRLLIM, pBuf->cchrval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cchrval.lower_ctrl_limit);
			break;
	    case DBR_CTRL_SHORT: /* cshrtval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:s, s:h, s:h, s:h, s:h, s:h, s:h, s:h, s:h}",
				PV_STATUS, pBuf->cshrtval.status,
				PV_SEVERITY, pBuf->cshrtval.severity,
				PV_VALUE, pBuf->cshrtval.value,
				PV_UNITS, pBuf->cshrtval.units,
				PV_UPDISLIM, pBuf->cshrtval.upper_disp_limit,
				PV_LODISLIM, pBuf->cshrtval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cshrtval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cshrtval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cshrtval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cshrtval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cshrtval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cshrtval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_FLOAT: /* cfltval */
			d = Py_BuildValue("{s:h, s:h, s:f, s:s, s:h, s:h, s:f, s:f, s:f, s:f, s:f, s:f, s:f, s:f}",
				PV_STATUS, pBuf->cfltval.status,
				PV_SEVERITY, pBuf->cfltval.severity,
				PV_VALUE, pBuf->cfltval.value,
				PV_UNITS, pBuf->cfltval.units,
				PV_PRECISION, pBuf->cfltval.precision,
				PV_RISCPAD, pBuf->cfltval.RISC_pad,
				PV_UPDISLIM, pBuf->cfltval.upper_disp_limit,
				PV_LODISLIM, pBuf->cfltval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cfltval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cfltval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cfltval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cfltval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cfltval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cfltval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_ENUM: /* cenmval */
			d = Py_BuildValue("{s:h, s:h, s:i, s:h, s:s}",
				PV_STATUS, pBuf->cenmval.status,
				PV_SEVERITY, pBuf->cenmval.severity,
				PV_VALUE, (int)pBuf->cenmval.value,
				PV_NOSTRINGS, pBuf->cenmval.no_str,
				PV_STATESTRINGS, pBuf->cenmval.strs );
		break;
	    case DBR_CTRL_LONG: /* clngval */
			d = Py_BuildValue("{s:h, s:h, s:l, s:s, s:l, s:l, s:l, s:l, s:l, s:l, s:l, s:l}",
				PV_STATUS, pBuf->clngval.status,
				PV_SEVERITY, pBuf->clngval.severity,
				PV_VALUE, pBuf->clngval.value,
				PV_UNITS, pBuf->clngval.units,
				PV_UPDISLIM, pBuf->clngval.upper_disp_limit,
				PV_LODISLIM, pBuf->clngval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->clngval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->clngval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->clngval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->clngval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->clngval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->clngval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_DOUBLE: /* cdblval */
			d = Py_BuildValue("{s:h, s:h, s:d, s:s, s:h, s:h, s:d, s:d, s:d, s:d, s:d, s:d, s:d, s:d}",
				PV_STATUS, pBuf->cdblval.status,
				PV_SEVERITY, pBuf->cdblval.severity,
				PV_VALUE, pBuf->cdblval.value,
				PV_UNITS, pBuf->cdblval.units,
				PV_PRECISION, pBuf->cdblval.precision,
				PV_RISCPAD0, pBuf->cdblval.RISC_pad0,
				PV_UPDISLIM, pBuf->cdblval.upper_disp_limit,
				PV_LODISLIM, pBuf->cdblval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cdblval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cdblval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cdblval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cdblval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cdblval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cdblval.lower_ctrl_limit);
		break;
	    default:  /* conversion not possible, failure */
		printf("unpackControlGet: Unknown DBR type\n");
	} /* end switch(requestType) */
    } /* end if */
    else {
		switch(dbrType) {
		case DBR_CTRL_STRING: /* cstrval */
			d = Py_BuildValue("{s:h, s:h}",
				PV_STATUS, pBuf->cstrval.status,
				PV_SEVERITY, pBuf->cstrval.severity);
	    break;
	    case DBR_CTRL_CHAR: /* cchrval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:h, s:h, s:h, s:h, s:h, s:h, s:h}",
				PV_STATUS, pBuf->cchrval.status,
				PV_SEVERITY, pBuf->cchrval.severity,
				PV_UNITS, pBuf->cchrval.units,
				PV_UPDISLIM, pBuf->cchrval.upper_disp_limit,
				PV_LODISLIM, pBuf->cchrval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cchrval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cchrval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cchrval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cchrval.lower_warning_limit,
				PV_RISCPAD, pBuf->cchrval.RISC_pad,
				PV_UPCTRLLIM, pBuf->cchrval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cchrval.lower_ctrl_limit);
			break;
	    case DBR_CTRL_SHORT: /* cshrtval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:h, s:h, s:h, s:h, s:h, s:h}",
				PV_STATUS, pBuf->cshrtval.status,
				PV_SEVERITY, pBuf->cshrtval.severity,
				PV_UNITS, pBuf->cshrtval.units,
				PV_UPDISLIM, pBuf->cshrtval.upper_disp_limit,
				PV_LODISLIM, pBuf->cshrtval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cshrtval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cshrtval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cshrtval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cshrtval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cshrtval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cshrtval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_FLOAT: /* cfltval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:f, s:f, s:f, s:f, s:f, s:f, s:f, s:f}",
				PV_STATUS, pBuf->cfltval.status,
				PV_SEVERITY, pBuf->cfltval.severity,
				PV_UNITS, pBuf->cfltval.units,
				PV_PRECISION, pBuf->cfltval.precision,
				PV_RISCPAD, pBuf->cfltval.RISC_pad,
				PV_UPDISLIM, pBuf->cfltval.upper_disp_limit,
				PV_LODISLIM, pBuf->cfltval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cfltval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cfltval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cfltval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cfltval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cfltval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cfltval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_ENUM: /* cenmval */
			d = Py_BuildValue("{s:h, s:h, s:h, s:s}",
				PV_STATUS, pBuf->cenmval.status,
				PV_SEVERITY, pBuf->cenmval.severity,
				PV_NOSTRINGS, pBuf->cenmval.no_str,
				PV_STATESTRINGS, pBuf->cenmval.strs );
		break;
	    case DBR_CTRL_LONG: /* clngval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:l, s:l, s:l, s:l, s:l, s:l, s:l, s:l}",
				PV_STATUS, pBuf->clngval.status,
				PV_SEVERITY, pBuf->clngval.severity,
				PV_UNITS, pBuf->clngval.units,
				PV_UPDISLIM, pBuf->clngval.upper_disp_limit,
				PV_LODISLIM, pBuf->clngval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->clngval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->clngval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->clngval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->clngval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->clngval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->clngval.lower_ctrl_limit);
		break;
	    case DBR_CTRL_DOUBLE: /* cdblval */
			d = Py_BuildValue("{s:h, s:h, s:s, s:h, s:h, s:d, s:d, s:d, s:d, s:d, s:d, s:d, s:d}",
				PV_STATUS, pBuf->cdblval.status,
				PV_SEVERITY, pBuf->cdblval.severity,
				PV_UNITS, pBuf->cdblval.units,
				PV_PRECISION, pBuf->cdblval.precision,
				PV_RISCPAD0, pBuf->cdblval.RISC_pad0,
				PV_UPDISLIM, pBuf->cdblval.upper_disp_limit,
				PV_LODISLIM, pBuf->cdblval.lower_disp_limit,
				PV_UPALARMLIM, pBuf->cdblval.upper_alarm_limit,
				PV_LOALARMLIN, pBuf->cdblval.lower_alarm_limit,
				PV_UPWARNLIM, pBuf->cdblval.upper_warning_limit,
				PV_LOWARNLIM, pBuf->cdblval.lower_warning_limit,
				PV_UPCTRLLIM, pBuf->cdblval.upper_ctrl_limit,
				PV_LOCTRLLIM, pBuf->cdblval.lower_ctrl_limit);
		break;
		default:  /* conversion not possible, failure */
		printf("unpackControlGet: Unknown DBR type\n");
		} /* end switch(requestType) */						
	t = PyTuple_New(count);
        for(i = 0; i < count; ++i) {
	    switch (dbrType) {
		/* case DBR_STRING: No arrays of strings in EPICS*/
		case DBR_CTRL_CHAR:
		    pyVal = Py_BuildValue("b", (char)*(&(pBuf->cchrval.value) + i));
		    break;
		case DBR_CTRL_SHORT:
		    pyVal = Py_BuildValue("h", (short)*(&(pBuf->cshrtval.value) + i));
		    break;
		case DBR_CTRL_ENUM:
		    pyVal = Py_BuildValue("h", (int)*(&(pBuf->cenmval.value) +i));
	    	    break;
		case DBR_CTRL_LONG:
		    pyVal = Py_BuildValue("i", (long)*(&(pBuf->clngval.value) + i));
		    break;
		case DBR_CTRL_FLOAT:
		    pyVal = Py_BuildValue("d", (float)*(&(pBuf->cfltval.value) + i));
		    break;
		case DBR_CTRL_DOUBLE:
		    pyVal = Py_BuildValue("d", (double)*(&(pBuf->cdblval.value) + i));
		break;
	    } /* end switch */
	    PyTuple_SetItem(t, i, pyVal);
	    Py_XDECREF(pyVal);  /* tuple now references the value */
	} /* end for */
	PyDict_SetItemString(d, PV_VALUE, t);
    } /* end else */

    return d;

}  /* end unpackControlGet() */


/*
typedef struct	event_handler_args{
	void		*usr;	User argument supplied when event added
	struct channel_in_use *chid;	Channel id
	long		type;	the type of the value returned 
	long		count;	the element count of the item returned
	READONLY void	*dbr;	Pointer to the value returned
	int		status;	ECA_XXX Status of the requested op from server
};
*/
void getCallback(struct event_handler_args event_args)
{
    PyObject *func, *args, *retVals, *pyTup, *d, *result;
    char _ptemp[STR_LEN];
    union db_access_val *pBuf;

    if(ECA_NORMAL == event_args.status) {
	/* retrive the transferd data */
	pBuf = (union db_access_val *)event_args.dbr;
	
	if(dbr_type_is_plain(event_args.type)) {
	    d = unpackPlainGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_STS(event_args.type)) {
	    d = unpackStatusGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_TIME(event_args.type)) {
	    d = unpackTimeGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_GR(event_args.type)) {
	    d = unpackGraphicGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_CTRL(event_args.type)) {
	    d = unpackControlGet(pBuf, event_args.type, event_args.count);
	} 
	else
	    printf("getCallback: Unknown DBR type for get ! \n");
    }

    /* Create a swigged pointer to the channel identifier */
    SWIG_MakePtr(_ptemp, (char *) &(event_args.chid), "_chid_p");

    PyDict_SetItemString(d, GET_CHID, Py_BuildValue("s", _ptemp));
    PyDict_SetItemString(d, GET_TYPE, Py_BuildValue("i", event_args.type));
    PyDict_SetItemString(d, GET_COUNT, Py_BuildValue("i", event_args.count));
    PyDict_SetItemString(d, GET_STATUS, Py_BuildValue("i", event_args.status));    
    
    /* Build a tuple of CA values to return to the callback routine */
    pyTup = (PyObject *) event_args.usr;
    /* printf("tuple = %d\n", PyTuple_Check(pyTup)); */
    /* printf("size  = %d\n", PyTuple_Size(pyTup)); */
    func = PyTuple_GetItem(pyTup, 0);
    if(2 == PyTuple_Size(pyTup))
	args = Py_BuildValue("(OO)", d, PyTuple_GetItem(pyTup, 1));
    else
	args = Py_BuildValue("(O)", d);
    Py_XDECREF(d); /* args now references d */
    result = PyEval_CallObject(func, args);
    if (NULL == result)
        printf("***** PyEval_CallObject failed *****\n");
    Py_XDECREF(args);
    Py_XDECREF(result);
    Py_XDECREF(pyTup);
    
} /* end getCallback() */


/* Functionality matches getCallback.  The difference is in reference
 * counting of the argument tuple.  For eventCallback a reference to
 * the tuple needs to be maintained by the user.
 */
void eventCallback(struct event_handler_args event_args)
{
    PyObject *func, *args, *retVals, *pyTup, *d, *result;
    char _ptemp[STR_LEN];
    union db_access_val *pBuf;

    if(ECA_NORMAL == event_args.status) {
	/* retrive the transferd data */
	pBuf = (union db_access_val *)event_args.dbr;
	if(dbr_type_is_plain(event_args.type)) {
	    d = unpackPlainGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_STS(event_args.type)) {
	    d = unpackStatusGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_TIME(event_args.type)) {
	    d = unpackTimeGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_GR(event_args.type)) {
	    d = unpackGraphicGet(pBuf, event_args.type, event_args.count);
	}
	else if(dbr_type_is_CTRL(event_args.type)) {
	    d = unpackControlGet(pBuf, event_args.type, event_args.count);
	} 
	else
	    printf("eventCallback: Can't unpack unknow DBR type.\n");
    }

    /* Create a swigged pointer to the channel identifier */
    SWIG_MakePtr(_ptemp, (char *) &(event_args.chid), "_chid_p");

    PyDict_SetItemString(d, GET_CHID, Py_BuildValue("s", _ptemp));
    PyDict_SetItemString(d, GET_TYPE, Py_BuildValue("i", event_args.type));
    PyDict_SetItemString(d, GET_COUNT, Py_BuildValue("i", event_args.count));
    PyDict_SetItemString(d, GET_STATUS, Py_BuildValue("i", event_args.status));    
    
    /* Build a tuple of CA values to return to the callback routine */
    pyTup = (PyObject *) event_args.usr;
    func = PyTuple_GetItem(pyTup, 0);
    if(2 == PyTuple_Size(pyTup))
	args = Py_BuildValue("(OO)", d, PyTuple_GetItem(pyTup, 1));
    else
	args = Py_BuildValue("(O)", d);
    result = PyEval_CallObject(func, args);
    if (NULL == result)
        printf("***** PyEval_CallObject failed *****\n");
    Py_XDECREF(args);
    Py_XDECREF(result);
    /*Py_XDECREF(pyTup);*/
    
} /* end eventCallback() */


void fdregCallback(void *user_args, int fd, int opened)
{
    PyObject *func, *args, *retVals, *val;
    PyObject *pyTup, *result;
    char _ptemp[STR_LEN];
    
#ifdef DEBUG
    if(opened)
	printf("fd %d was opened\n", fd);
    else
	printf("fd %d was closed\n", fd);
#endif

    pyTup = (PyObject *) user_args;
    func = PyTuple_GetItem(pyTup, 0);
    if(2 == PyTuple_Size(pyTup))
	args = Py_BuildValue("(O)", PyTuple_GetItem(pyTup, 1));
    else
	args = Py_BuildValue("()");
    result = PyEval_CallObject(func, args);
    if (NULL == result)
        printf("***** PyEval_CallObject failed *****\n");
    Py_XDECREF(args);
    Py_XDECREF(result);
    Py_XDECREF(pyTup);
    
} /* end fdregCallback() */



void capollfunc(void *pParam) {
    /* printf("capollfunc\n"); */
    ca_poll();
    fdmgr_add_timeout(pfdctx, &fifteen_seconds, capollfunc, (void *)NULL);
    /*fdmgr_pend_event(pfdctx, &twenty_seconds);*/
}


void caFDCallback(void *pParam) {
    /* printf("caFDCallback\n"); */
    /*ca_poll();*/
    ca_pend_event(0.1);
}

void fd_register(void *pfd, int fd, int opened) {
    if(opened)
	fdmgr_add_callback(pfdctx, fd, fdi_read, caFDCallback, NULL);
    else
	fdmgr_clear_callback(pfdctx, fd, fdi_read);
}







