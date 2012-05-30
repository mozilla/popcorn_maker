class nginx($server_name, $project_path){
  case $operatingsystem {
    ubuntu: {
      package { "nginx":
        ensure => installed,
      }

      service { "nginx":
        ensure => running,
        enable => true,
        hasrestart => true,
        require => Package["nginx"]
      }

      file { "/etc/nginx/sites-available/default":
        path => "/etc/nginx/sites-available/default",
        mode => 0644,
        owner => root,
        group => root,
        ensure => file,
        require => Package["nginx"],
        notify => Service["nginx"],
        content => template("nginx/nginx.conf"),
      }

      file { "/etc/nginx/mime.types":
        path => "/etc/nginx/mime.types",
        mode => 0644,
        owner => root,
        group => root,
        ensure => file,
        require => Package["nginx"],
        notify => Service["nginx"],
        content => template("nginx/mime.types"),
      }

      exec {"restart-nginx":
        command => "/etc/init.d/nginx restart",
        refreshonly => true,
        before => Service["nginx"],
      }

    }
  }
}
