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
        memcached: ;
        custom: ;
    }
    class { "python":
      before => Class[apache],
      project_path => $project_path;
    }
    class { "mysql":
      before => Class[python],
      password => $password;
    }
    class { "apache":
      before => Class[playdoh],
      server_name => $server_name,
      project_path => $project_path;
    }
    class { "playdoh":
      project_path => $project_path,
      project_name => $project_name,
      username => $username,
      password => $password;
    }
}

include dev
