class apache($server_name, $project_path) {

  case $operatingsystem {
    ubuntu: {

      package {
        ["apache2-dev", "libapache2-mod-wsgi", "libapache2-mod-rpaf"]:
          ensure => installed
      }

      service { "apache2":
        ensure => running,
        enable => true,
        hasrestart => true,
        require => [
                    Package["apache2-dev"],
                    Package["libapache2-mod-wsgi"],
                    Package["libapache2-mod-rpaf"],
                    ],
      }

      file { "/etc/apache2/sites-enabled/playdoh.conf":
        path => "/etc/apache2/sites-enabled/playdoh.conf",
        mode => 0644,
        owner => root,
        group => root,
        ensure => file,
        require => Package["apache2-dev"],
        notify => Service["apache2"],
        content => template("apache/apache.conf"),
      }

      exec { "restart-apache2":
        command => "/etc/init.d/apache2 restart",
        refreshonly => true,
        before => Service["apache2"],
      }

      # make sure the default site isnt present.
      exec {"/usr/sbin/a2dissite default":
        onlyif => "/usr/bin/test -L /etc/apache2/sites-enabled/000-default",
        notify => Exec["restart-apache2"],
      }

      exec {"/usr/sbin/a2enmod proxy_http":
        notify => Exec["restart-apache2"],
      }

      exec {"/usr/sbin/a2enmod headers":
        notify => Exec["restart-apache2"],
      }

      exec {"/usr/sbin/a2enmod expires":
        notify => Exec["restart-apache2"],
      }

      exec {"/usr/sbin/a2enmod rewrite":
        notify => Exec["restart-apache2"],
      }

      exec {"/usr/sbin/a2enmod proxy":
        notify => Exec["restart-apache2"],
      }

    }
  }
}
