REPORT_NAME     = 'system.domain.name'  # Name of the monitored HBlink system
CONFIG_INC      = True                  # Include HBlink stats
BRIDGES_INC     = True                  # Include Bridge stats (confbrige.py)
HBLINK_IP      = '127.0.0.1'           # HBlink's IP Address
HBLINK_PORT    = 4321                  # HBlink's TCP reporting socket
FREQUENCY       = 10                    # Frequency to push updates to web clients
WEB_SERVER_PORT = 8080                  # Has to be above 1024 if you're not running as root

# Files and stuff for loading alias files for mapping numbers to names
PATH            = './'                          # MUST END IN '/'
PEER_FILE       = 'peer_ids.csv'                # Will auto-download from DMR-MARC
SUBSCRIBER_FILE = 'subscriber_ids.csv'          # Will auto-download from DMR-MARC
TGID_FILE       = 'talkgroup_ids.csv'           # User provided, should be in "integer TGID, TGID name" format
LOCAL_SUB_FILE  = 'local_subscriber_ids.csv'    # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_PEER_FILE = 'local_peer_ids.csv'          # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
FILE_RELOAD     = 7                             # Number of days before we reload DMR-MARC database files
PEER_URL        = 'http://radioid.net/static/rptrs.csv'
SUBSCRIBER_URL  = 'http://radioid.net/static/users.csv'
