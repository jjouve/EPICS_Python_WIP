/*
 * filename: ca.i
 * created : 12/22/98
 * author  : Geoff Savage
 *
 *   SWIG input file for EPICS channel access.
 * Goal:
 *	Make EPICS channel access calls from Python.
 * Strategy:
 *	Use swig to wrap the channel access calls.
 *
 */
%module ca

#define AUTODOC
/* %include typemaps.i */

/* Include directly in .c file */
%{
#include "alarmString.h"
#include "cadef.h"
 
#include "fdmgr.h"
fdctx *pfdctx;
static struct timeval twenty_seconds	= {20, 0};
static struct timeval fifteen_seconds	= {15, 0};
static struct timeval one_second	= { 0, 1000000};

#include "ca_internal_functions.c"

%}  /* end of direct includes */

/* so that SWIG interprets chtype correctly */
typedef long chtype;
typedef float dbr_float_t;


%name(version) %inline %{
void caVersion()
{
    printf("caPython: version v00-02-01\n");
    printf("Supports EPICS R3.12 CA Client API\n");

} /* end caVersion() */
%}

/* Functions added to help implement the channel access functionality */
%include "../ca_helper_functions.i"

%name(task_initialize) int ca_task_initialize();

%name(task_exit)       int ca_task_exit();

%typemap(python,in) void *CONNECTFUNC {
    $target = connectCallback;
}

%typemap(python,in) void *CONNECTARG {
    $target = $source;
    Py_INCREF($source);
}

%name(search_and_connect)
int ca_search_and_connect(
	char *CHANNEL_NAME,
	chid *PCHID,
	void *CONNECTFUNC,
	void *CONNECTARG);

%name(search) int ca_search(char *chName, chid *pchId);

%name(clear_channel) int ca_clear_channel(chid chId);

%name(array_put)
int ca_array_put(
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *PVALUE);
%name(put) int ca_put(chtype TYPE, chid CHID, void *PVALUE);
%name(bput) int ca_bput(chid CHID, char *PVALUE);
%name(rput) int ca_rput(chid CHID, dbr_float_t *PVALUE);


%typemap(python,in) void *PUTFUNC {
    $target = putCallback;
}

%typemap(python,in) void *PUTARG {
    $target = $source;
    Py_XINCREF($source);
}

%name(array_put_callback)
int ca_array_put_callback(
	chtype chType,
	unsigned long count,
	chid chId,
	void *pvalue,
	void *PUTFUNC,
	void *PUTARG);

%name(put_callback)
int ca_put_callback(
	chtype chType,
	chid chId,
	void *pvalue,
	void *PUTFUNC,
	void *PUTARG);


%name(array_get)
int ca_array_get(
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *PVALUE);
%name(get) int ca_get(chtype TYPE, chid CHID, void *PVALUE);
%name(bget) int ca_bget(chid CHID, void *PVALUE);
/*%name(bget) int ca_bget(chid CHID, char *PVALUE); */
%name(rget) int ca_rget(chid CHID, dbr_float_t *PVALUE);

%typemap(python,in) void *GETFUNC {
    $target = getCallback;
}

%typemap(python,in) void *GETARG {
    $target = $source;
    Py_INCREF($source);
}

%name(get_callback)
int ca_get_callback(
	chtype TYPE,
	chid CHID,
	void *GETFUNC,
	void *GETARG);

%name(array_get_callback)
int ca_array_get_callback(
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *GETFUNC,
	void *GETARG);


%typemap(python,in) void *EVENTFUNC {
    $target = eventCallback;
}

%typemap(python,in) void *EVENTARG {
    $target = $source;
}

%typemap(python,in) double float_zero {
    $target = 0.0;
}

%name(add_masked_array_event)
int ca_add_masked_array_event(
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *EVENTFUNC,
	void *EVENTARG,
	double float_zero,
	double float_zero,
	double float_zero,
	evid *PEVID,
	unsigned long MASK);

%name(add_array_event)
int ca_add_array_event(
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *EVENTFUNC,
	void *EVENTARG,
	double float_zero,
	double float_zero,
	double float_zero,
	evid *PEVID);

%name(add_event)
int ca_add_event(
	chtype TYPE,
	chid CHID,
	void *EVENTFUNC,
	void *EVENTARG,
	evid *PEVID);


%name(clear_event) int ca_clear_event(evid EVID);

%name(pend_io) int ca_pend_io(double TIMEOUT);

%name(test_io) int ca_test_io();

%name(pend_event) int ca_pend_event(double TIMEOUT);

%name(poll) int ca_poll();

%name(flush_io) int ca_flush_io();

%name(signal) void ca_signal(long CA_STATUS, char *CONTEXT_STRING);

%name(SEVCHK) void SEVCHK(long CA_STATUS, char *CONTEXT_STRING);

/*
 * These functions don't support passing an argument to the
 * callback function.  This is needed to implement callbacks
 * in Python.
 
%name(change_connection_event)
int ca_change_connection_event (
	chid	chan,
	void	(*pfunc)(struct connection_handler_args)
);

%name(replace_printf_handler)
int ca_replace_printf_handler (
	int (*ca_printf_func)(READONLY char *pformat, va_list args)
);

%name(replace_access_rights_event)
int ca_replace_access_rights_event(
	chid	chan,
	void 	(*pfunc)(struct access_rights_handler_args)
);
*/

/*
 * This routine appears to be too complicated to implement.
 * From the Channel Access Reference Manual:
 *	"More information needs to be provided about which
 *	arguments are valid with each exception.  More
 *	information needs to be provided correlating exceptions
 *	with the routines which cause them."
	
%name(add_exception_event)
int ca_add_exception_event (
	void           (*pfunc) (struct exception_handler_args),
	READONLY void	*pArg
);
*/

%name(test_event)
void ca_test_event(struct event_handler_args HANDLERARGS);

%typemap(python,in) void *FDREGFUNC {
    $target = getCallback;
}

%typemap(python,in) void *FDREGARG {
    $target = $source;
    Py_INCREF($source);
}

%name(add_fd_registration)
int ca_add_fd_registration(
	void *FDREGFUNC,
	void *FDREGARG);

%name(modify_user_name)
int ca_modify_user_name(char *PUSERNAME);

%name(modify_host_name)
int ca_modify_host_name(char *PHOSTNAME);

%name(sg_create)
int ca_sg_create(CA_SYNC_GID *PGID);

%name(sg_delete)
int ca_sg_delete(CA_SYNC_GID GID);

%name(sg_block)
int ca_sg_block(CA_SYNC_GID GID, double timeout);

%name(sg_test)
int ca_sg_test(CA_SYNC_GID GID);

%name(sg_reset)
int ca_sg_reset(CA_SYNC_GID GID);

%name(sg_put)
int ca_sg_array_put(
	CA_SYNC_GID GID,
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *PVALUE);

%name(sg_get)
int ca_sg_array_get(
	CA_SYNC_GID GID,
	chtype TYPE,
	unsigned long COUNT,
	chid CHID,
	void *PVALUE);


%include pointer.i
%include "../captr.i"	/* my pointer library */

/* Included in the initialization function, initcaswig().
   The init function is called when the module is imported.
 */
%init %{
    /* Field types */
    /* Native types, DBF_XXXX */
    PyDict_SetItemString(d, "DBF_STRING", PyInt_FromLong((long) DBF_STRING));
    PyDict_SetItemString(d, "DBF_SHORT", PyInt_FromLong((long) DBF_SHORT));
    PyDict_SetItemString(d, "DBF_INT", PyInt_FromLong((long) DBF_INT));
    PyDict_SetItemString(d, "DBF_FLOAT", PyInt_FromLong((long) DBF_FLOAT));
    PyDict_SetItemString(d, "DBF_ENUM", PyInt_FromLong((long) DBF_ENUM));
    PyDict_SetItemString(d, "DBF_CHAR", PyInt_FromLong((long) DBF_CHAR));
    PyDict_SetItemString(d, "DBF_LONG", PyInt_FromLong((long) DBF_LONG));
    PyDict_SetItemString(d, "DBF_DOUBLE", PyInt_FromLong((long) DBF_DOUBLE));

    /* Request types, DBR_XXXX */
    PyDict_SetItemString(d, "DBR_STRING", PyInt_FromLong((long) DBR_STRING));
    PyDict_SetItemString(d, "DBR_SHORT", PyInt_FromLong((long) DBR_SHORT));
    PyDict_SetItemString(d, "DBR_INT", PyInt_FromLong((long) DBR_INT));
    PyDict_SetItemString(d, "DBR_FLOAT", PyInt_FromLong((long) DBR_FLOAT));
    PyDict_SetItemString(d, "DBR_ENUM", PyInt_FromLong((long) DBR_ENUM));
    PyDict_SetItemString(d, "DBR_CHAR", PyInt_FromLong((long) DBR_CHAR));
    PyDict_SetItemString(d, "DBR_LONG", PyInt_FromLong((long) DBR_LONG));
    PyDict_SetItemString(d, "DBR_DOUBLE", PyInt_FromLong((long) DBR_DOUBLE));

    /* Status request types, DBR_STS_XXXX */
    PyDict_SetItemString(d, "DBR_STS_STRING", PyInt_FromLong((long) DBR_STS_STRING));
    PyDict_SetItemString(d, "DBR_STS_SHORT", PyInt_FromLong((long) DBR_STS_SHORT));
    PyDict_SetItemString(d, "DBR_STS_INT", PyInt_FromLong((long) DBR_STS_INT));
    PyDict_SetItemString(d, "DBR_STS_FLOAT", PyInt_FromLong((long) DBR_STS_FLOAT));
    PyDict_SetItemString(d, "DBR_STS_ENUM", PyInt_FromLong((long) DBR_STS_ENUM));
    PyDict_SetItemString(d, "DBR_STS_CHAR", PyInt_FromLong((long) DBR_STS_CHAR));
    PyDict_SetItemString(d, "DBR_STS_LONG", PyInt_FromLong((long) DBR_STS_LONG));
    PyDict_SetItemString(d, "DBR_STS_DOUBLE", PyInt_FromLong((long) DBR_STS_DOUBLE));

    /* Time request types, DBR_TIME_XXXX */
    PyDict_SetItemString(d, "DBR_TIME_STRING", PyInt_FromLong((long) DBR_TIME_STRING));
    PyDict_SetItemString(d, "DBR_TIME_SHORT", PyInt_FromLong((long) DBR_TIME_SHORT));
    PyDict_SetItemString(d, "DBR_TIME_INT", PyInt_FromLong((long) DBR_TIME_INT));
    PyDict_SetItemString(d, "DBR_TIME_FLOAT", PyInt_FromLong((long) DBR_TIME_FLOAT));
    PyDict_SetItemString(d, "DBR_TIME_ENUM", PyInt_FromLong((long) DBR_TIME_ENUM));
    PyDict_SetItemString(d, "DBR_TIME_CHAR", PyInt_FromLong((long) DBR_TIME_CHAR));
    PyDict_SetItemString(d, "DBR_TIME_LONG", PyInt_FromLong((long) DBR_TIME_LONG));
    PyDict_SetItemString(d, "DBR_TIME_DOUBLE", PyInt_FromLong((long) DBR_TIME_DOUBLE));

    /* Graphics request types, DBR_GR_XXXX */
    PyDict_SetItemString(d, "DBR_GR_STRING", PyInt_FromLong((long) DBR_GR_STRING));
    PyDict_SetItemString(d, "DBR_GR_SHORT", PyInt_FromLong((long) DBR_GR_SHORT));
    PyDict_SetItemString(d, "DBR_GR_INT", PyInt_FromLong((long) DBR_GR_INT));
    PyDict_SetItemString(d, "DBR_GR_FLOAT", PyInt_FromLong((long) DBR_GR_FLOAT));
    PyDict_SetItemString(d, "DBR_GR_ENUM", PyInt_FromLong((long) DBR_GR_ENUM));
    PyDict_SetItemString(d, "DBR_GR_CHAR", PyInt_FromLong((long) DBR_GR_CHAR));
    PyDict_SetItemString(d, "DBR_GR_LONG", PyInt_FromLong((long) DBR_GR_LONG));
    PyDict_SetItemString(d, "DBR_GR_DOUBLE", PyInt_FromLong((long) DBR_GR_DOUBLE));

    /* Control request types, DBR_CTRL_XXXX */
    PyDict_SetItemString(d, "DBR_CTRL_STRING", PyInt_FromLong((long) DBR_CTRL_STRING));
    PyDict_SetItemString(d, "DBR_CTRL_SHORT", PyInt_FromLong((long) DBR_CTRL_SHORT));
    PyDict_SetItemString(d, "DBR_CTRL_INT", PyInt_FromLong((long) DBR_CTRL_INT));
    PyDict_SetItemString(d, "DBR_CTRL_FLOAT", PyInt_FromLong((long) DBR_CTRL_FLOAT));
    PyDict_SetItemString(d, "DBR_CTRL_ENUM", PyInt_FromLong((long) DBR_CTRL_ENUM));
    PyDict_SetItemString(d, "DBR_CTRL_CHAR", PyInt_FromLong((long) DBR_CTRL_CHAR));
    PyDict_SetItemString(d, "DBR_CTRL_LONG", PyInt_FromLong((long) DBR_CTRL_LONG));
    PyDict_SetItemString(d, "DBR_CTRL_DOUBLE", PyInt_FromLong((long) DBR_CTRL_DOUBLE));

    /* Miscellaneous request types */
    PyDict_SetItemString(d, "DBR_PUT_ACKT", PyInt_FromLong((long) DBR_PUT_ACKT));
    PyDict_SetItemString(d, "DBR_PUT_ACKS", PyInt_FromLong((long) DBR_PUT_ACKS));
    PyDict_SetItemString(d, "DBR_STSACK_STRING", PyInt_FromLong((long) DBR_STSACK_STRING));
    PyDict_SetItemString(d, "DBR_STSACK_STRING", PyInt_FromLong((long) DBR_STSACK_STRING));
    PyDict_SetItemString(d, "LAST_BUFFER_TYPE", PyInt_FromLong((long) LAST_BUFFER_TYPE));
    PyDict_SetItemString(d, "DBR_CTRL_CHAR", PyInt_FromLong((long) DBR_CTRL_CHAR));
    PyDict_SetItemString(d, "DBR_CTRL_LONG", PyInt_FromLong((long) DBR_CTRL_LONG));
    PyDict_SetItemString(d, "DBR_CTRL_DOUBLE", PyInt_FromLong((long) DBR_CTRL_DOUBLE));

    /* Return Codes, from caerr.h */
    PyDict_SetItemString(d, "ECA_NORMAL", PyInt_FromLong((long) ECA_NORMAL));
    PyDict_SetItemString(d, "ECA_MAXIOC", PyInt_FromLong((long) ECA_MAXIOC));
    PyDict_SetItemString(d, "ECA_UKNHOST", PyInt_FromLong((long) ECA_UKNHOST));
    PyDict_SetItemString(d, "ECA_UKNSERV", PyInt_FromLong((long) ECA_UKNSERV));
    PyDict_SetItemString(d, "ECA_SOCK", PyInt_FromLong((long) ECA_SOCK));
    PyDict_SetItemString(d, "ECA_CONN", PyInt_FromLong((long) ECA_CONN));
    PyDict_SetItemString(d, "ECA_ALLOCMEM", PyInt_FromLong((long) ECA_ALLOCMEM));
    PyDict_SetItemString(d, "ECA_UKNCHAN", PyInt_FromLong((long) ECA_UKNCHAN));
    PyDict_SetItemString(d, "ECA_UKNFIELD", PyInt_FromLong((long) ECA_UKNFIELD));
    PyDict_SetItemString(d, "ECA_TIMEOUT", PyInt_FromLong((long) ECA_TIMEOUT));
    PyDict_SetItemString(d, "ECA_TOLARGE", PyInt_FromLong((long) ECA_TOLARGE));
    PyDict_SetItemString(d, "ECA_NOSUPPORT", PyInt_FromLong((long) ECA_NOSUPPORT));
    PyDict_SetItemString(d, "ECA_STRTOBIG", PyInt_FromLong((long) ECA_STRTOBIG));
    PyDict_SetItemString(d, "ECA_DISCONNCHID", PyInt_FromLong((long) ECA_DISCONNCHID));
    PyDict_SetItemString(d, "ECA_BADTYPE", PyInt_FromLong((long) ECA_BADTYPE));
    PyDict_SetItemString(d, "ECA_CHIDNOTFND", PyInt_FromLong((long) ECA_CHIDNOTFND));
    PyDict_SetItemString(d, "ECA_CHIDRETRY", PyInt_FromLong((long) ECA_CHIDRETRY));
    PyDict_SetItemString(d, "ECA_INTERNAL", PyInt_FromLong((long) ECA_INTERNAL));
    PyDict_SetItemString(d, "ECA_DBLCLFAIL", PyInt_FromLong((long) ECA_DBLCLFAIL));
    PyDict_SetItemString(d, "ECA_GETFAIL", PyInt_FromLong((long) ECA_GETFAIL));
    PyDict_SetItemString(d, "ECA_PUTFAIL", PyInt_FromLong((long) ECA_PUTFAIL));
    PyDict_SetItemString(d, "ECA_ADDFAIL", PyInt_FromLong((long) ECA_ADDFAIL));
    PyDict_SetItemString(d, "ECA_BADCOUNT", PyInt_FromLong((long) ECA_BADCOUNT));
    PyDict_SetItemString(d, "ECA_BADSTR", PyInt_FromLong((long) ECA_BADSTR));
    PyDict_SetItemString(d, "ECA_DISCONN", PyInt_FromLong((long) ECA_DISCONN));
    PyDict_SetItemString(d, "ECA_DBLCHNL", PyInt_FromLong((long) ECA_DBLCHNL));
    PyDict_SetItemString(d, "ECA_EVDISALLOW", PyInt_FromLong((long) ECA_EVDISALLOW));
    PyDict_SetItemString(d, "ECA_BUILDGET", PyInt_FromLong((long) ECA_BUILDGET));
    PyDict_SetItemString(d, "ECA_NEEDSFP", PyInt_FromLong((long) ECA_NEEDSFP));
    PyDict_SetItemString(d, "ECA_OVEVFAIL", PyInt_FromLong((long) ECA_OVEVFAIL));
    PyDict_SetItemString(d, "ECA_BADMONID", PyInt_FromLong((long) ECA_BADMONID));
    PyDict_SetItemString(d, "ECA_NEWADDR", PyInt_FromLong((long) ECA_NEWADDR));
    PyDict_SetItemString(d, "ECA_NEWCONN", PyInt_FromLong((long) ECA_NEWCONN));
    PyDict_SetItemString(d, "ECA_NOCACTX", PyInt_FromLong((long) ECA_NOCACTX));
    PyDict_SetItemString(d, "ECA_DEFUNCT", PyInt_FromLong((long) ECA_DEFUNCT));
    PyDict_SetItemString(d, "ECA_EMPTYSTR", PyInt_FromLong((long) ECA_EMPTYSTR));
    PyDict_SetItemString(d, "ECA_NOREPEATER", PyInt_FromLong((long) ECA_NOREPEATER));
    /*PyDict_SetItemString(d, "ECA_NOCHANMSG", PyInt_FromLong((long) ECA_NOCHANMSG)); */
    PyDict_SetItemString(d, "ECA_DLCKREST", PyInt_FromLong((long) ECA_DLCKREST));
    PyDict_SetItemString(d, "ECA_SERVBEHIND", PyInt_FromLong((long) ECA_SERVBEHIND));
    PyDict_SetItemString(d, "ECA_NOCAST", PyInt_FromLong((long) ECA_NOCAST));
    PyDict_SetItemString(d, "ECA_BADMASK", PyInt_FromLong((long) ECA_BADMASK));
    PyDict_SetItemString(d, "ECA_IODONE", PyInt_FromLong((long) ECA_IODONE));
    PyDict_SetItemString(d, "ECA_IOINPROGRESS", PyInt_FromLong((long) ECA_IOINPROGRESS));
    PyDict_SetItemString(d, "ECA_BADSYNCGRP", PyInt_FromLong((long) ECA_BADSYNCGRP));
    PyDict_SetItemString(d, "ECA_PUTCBINPROG", PyInt_FromLong((long) ECA_PUTCBINPROG));
    PyDict_SetItemString(d, "ECA_NORDACCESS", PyInt_FromLong((long) ECA_NORDACCESS));
    PyDict_SetItemString(d, "ECA_NOWTACCESS", PyInt_FromLong((long) ECA_NOWTACCESS));
    PyDict_SetItemString(d, "ECA_ANACHRONISM", PyInt_FromLong((long) ECA_ANACHRONISM));
    PyDict_SetItemString(d, "ECA_NOSEARCHADDR", PyInt_FromLong((long) ECA_NOSEARCHADDR));
    PyDict_SetItemString(d, "ECA_NOCONVERT", PyInt_FromLong((long) ECA_NOCONVERT));
    PyDict_SetItemString(d, "ECA_BADCHID", PyInt_FromLong((long) ECA_BADCHID));
    PyDict_SetItemString(d, "ECA_BADFUNCPTR", PyInt_FromLong((long) ECA_BADFUNCPTR));

    /* Connection Codes */
    PyDict_SetItemString(d, "CA_OP_CONN_UP", PyInt_FromLong((long) CA_OP_CONN_UP));
    PyDict_SetItemString(d, "CA_OP_CONN_DOWN", PyInt_FromLong((long) CA_OP_CONN_DOWN));
    PyDict_SetItemString(d, "cs_never_conn", PyInt_FromLong((long) cs_never_conn));
    PyDict_SetItemString(d, "cs_prev_conn", PyInt_FromLong((long) cs_prev_conn));
    PyDict_SetItemString(d, "cs_conn", PyInt_FromLong((long) cs_conn));
    PyDict_SetItemString(d, "cs_closed", PyInt_FromLong((long) cs_closed));
    
    /* Event Trigger Mask */
    PyDict_SetItemString(d, "DBE_VALUE", PyInt_FromLong((long) DBE_VALUE));
    PyDict_SetItemString(d, "DBE_LOG", PyInt_FromLong((long) DBE_LOG));
    PyDict_SetItemString(d, "DBE_ALARM", PyInt_FromLong((long) DBE_ALARM));


    if (PyErr_Occurred())
        Py_FatalError("initca: Error adding items to dictionary");
      
	/* ca_task_initialize() called when ca module is imported*/
	{
	int status;
	status = ca_task_initialize();

	if(ECA_NORMAL == status)
		/*printf("CA task initialized.\n")*/;
	else if (ECA_ALLOCMEM == status)
		Py_FatalError("initca: ca_task_initialize: ECA_ALLOCMEM\n");
	else
		Py_FatalError("initca: ca_task_initialize: unknown error code\n");
	}
      
%}
