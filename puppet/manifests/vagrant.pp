#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

$PROJ_DIR = $project_path

# You can make these less generic if you like, but these are box-specific
# so it's not required.
$DB_NAME = $project_name
$DB_USER = $username
$DB_PASS = $password

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

class dev {
    class {
        init: before => Class[mysql];
        mysql: before  => Class[python];
        python: before => Class[apache];
        apache: before => Class[playdoh];
        memcached: ;
        playdoh: ;
        custom: ;
    }
}

include dev
