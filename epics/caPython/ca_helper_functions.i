/*
 * filename: ca_helper_functions.i
 * created : 07/26/99
 * author  : Geoff Savage
 *
 * Functions added to channel access to make the interface complete.
 */

%name(new_chid) %inline %{
chid *new_chid()
{
    void *pspace;
    pspace = malloc(sizeof(chid *));
    if (NULL == pspace)
	PyErr_NoMemory();
    return pspace;
} %}
/* Pointer to channel data. */

%name(free_chid) %inline %{
void free_chid(chid *pchid)
{
    free(pchid);
} %}
/* Free pointer to channel data. */

%name(new_evid) %inline %{
evid *new_evid()
{
    void *pspace;
    pspace = malloc(sizeof(evid *));
    if (NULL == pspace)
	PyErr_NoMemory();
    return pspace;
} %}
/* Pointer to event data. */

%name(free_evid) %inline %{
void free_evid(evid *pevid)
{
    free(pevid);
} %}
/* Free pointer to event data. */

/* Macros wrapped in functions */

%name(field_type) %inline %{
int ca_field_type_macro(chid chId) {
    return ca_field_type(chId);
} %}
/* Native field type (DBF_XXXX). */

%name(element_count) %inline %{
unsigned ca_element_count_macro(chid chId) {
    return ca_element_count(chId);
} %}
/* Native array element count. */

%name(name) %inline %{
const char *ca_name_macro(chid chId) {
    return ca_name(chId);
} %}
/* Name provided when channel was connected. */

%name(puser) %inline %{
void *ca_puser_macro(chid chId) {
    return ca_puser(chId);
} %}
/* A pointer sized region accesible by users. */

%name(state) %inline %{
enum channel_state ca_state_macro(chid chId) {
    return ca_state(chId);
} %}
/* Channels current state. */

%name(message) %inline %{
char *ca_message_macro(int status) {
    return ca_message(status);
} %}
/* Message string associated with status code. */

%name(host_name) %inline %{
char *ca_host_name_macro(chid chId) {
    return ca_host_name(chId);
} %}
/* Host name to which channel is connected. */

%name(read_access) %inline %{
int ca_read_access_macro(chid chId) {
    return ca_read_access(chId);
} %}
/* TRUE if client can read; FALSE otherwise. */

%name(write_access) %inline %{
int ca_write_access_macro(chid chId) {
    return ca_write_access(chId);
} %}
/* TRUE if client can write; FALSE otherwise.*/

%name(dbr_size_n) %inline %{
unsigned dbr_size_n_macro(chtype type, int count) {
    return dbr_size_n(type, count);
} %}
/* Size in bytes for a DBR_XXXX with n elements. */

%name(dbr_size) %inline %{
unsigned dbr_size_macro(chtype type) {
    return dbr_size[type];
} %}
/* Size in bytes for a DBR_XXXX. */

%name(dbr_value_size) %inline %{
unsigned dbr_value_size_macro(chtype type) {
    return dbr_value_size[type];
} %}
/* Size in bytes for the value of a DBR_XXXX */

%name(valid_db_req)
%inline %{
int valid_db_req_macro(int x) {
    return VALID_DB_REQ(x);
} %}

%name(invalid_db_req) 
%inline %{
int invalid_db_req_macro(int x) {
    return INVALID_DB_REQ(x);
} %}

%name(dbr_text) %inline %{
char *dbr_text_macro(int x) {
    return dbr_text[x];
} %}

%name(dbf_text) %inline %{
char *dbf_text_macro(int x) {
    return dbf_text[x];
} %}

%name(dbf_type_to_DBR) %inline %{
int dbf_type_to_DBR_macro(int x) {
    return dbf_type_to_DBR(x);
} %}

%name(dbf_type_to_DBR_STS) %inline %{
int dbf_type_to_DBR_STS_macro(int x) {
    return dbf_type_to_DBR_STS(x);
} %}

%name(dbf_type_to_DBR_TIME) %inline %{
int dbf_type_to_DBR_TIME_macro(int x) {
    return dbf_type_to_DBR_TIME(x);
} %}

%name(dbf_type_to_DBR_GR) %inline %{
int dbf_type_to_DBR_GR_macro(int x) {
    return dbf_type_to_DBR_GR(x);
} %}

%name(dbf_type_to_DBR_CTRL) %inline %{
int dbf_type_to_DBR_CTRL_macro(int x) {
    return dbf_type_to_DBR_CTRL(x);
} %}

%name(dbr_type_is_valid) %inline %{
int dbr_type_is_valid_macro(int x) {
    return dbr_type_is_valid(x);
} %}

%name(dbr_type_is_plain) %inline %{
int dbr_type_is_plain_macro(int x) {
    return dbr_type_is_plain(x);
} %}

%name(dbr_type_is_STS) %inline %{
int dbr_type_is_STS_macro(int x) {
    return dbr_type_is_STS(x);
} %}

%name(dbr_type_is_TIME) %inline %{
int dbr_type_is_TIME_macro(int x) {
    return dbr_type_is_TIME(x);
} %}

%name(dbr_type_is_GR) %inline %{
int dbr_type_is_GR_macro(int x) {
    return dbr_type_is_GR(x);
} %}

%name(dbr_type_is_CTRL) %inline %{
int dbr_type_is_CTRL_macro(int x) {
    return dbr_type_is_CTRL(x);
} %}

%name(alarmSeverityString) %inline %{
char *alarmSeverityString_macro(int x) {
    return alarmSeverityString[x];
} %}

%name(alarmStatusString) %inline %{
char *alarmStatusString_macro(int x) {
    return alarmStatusString[x];
} %}

%name(fdmgr_start) %inline %{
void fdmgr_start() {
    /* printf("fdmgr_start: fdmgr_init()\n"); */
    pfdctx = fdmgr_init();
    
    if(!pfdctx)
	printf("fdmgr_start: fdmgr_init() failed\n");

    SEVCHK(ca_add_fd_registration(fd_register, pfdctx), 
		"fdmgr_start: ca_add_fd_registration failed");

    /* printf("fdmgr_start: fdmgr_add_timeout()\n"); */
    fdmgr_add_timeout(pfdctx, &one_second, capollfunc, (void *)NULL);

} %}

%name(fdmgr_pend) %inline %{
void fdmgr_pend() {
    fdmgr_pend_event(pfdctx, &twenty_seconds);
} %}









