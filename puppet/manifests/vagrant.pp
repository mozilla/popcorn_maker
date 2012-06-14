#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

$PROJ_DIR = $project_path

# You can make these less generic if you like, but these are box-specific
# so it's not required.
$DB_NAME = $project_name
$DB_PASS = $password

Exec {
  path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

class dev {
  class {
    init: ;
    memcached: ;
    versioning: ;
  }
  class { "mysql":
    require => Class[init],
    password => $password;
  }
  class { "python":
    require => Class[mysql],
    project_path => $project_path;
  }
  class { "certificates":
    require => Class[python],
    server_name => $server_name;
  }
  class { "nodejs":
    require => Class[python];
  }
  class { "apache":
    require => Class[certificates],
    server_name => $server_name,
    project_path => $project_path;
  }
  class { "nginx":
    require => Class[apache],
    server_name => $server_name,
    project_path => $project_path;
  }
  class { "playdoh":
    project_path => $project_path,
    project_name => $project_name,
    password => $password,
    require => Class[nginx];
  }
  class { "custom":
    project_path => $project_path,
    project_name => $project_name;
  }
}

include dev
