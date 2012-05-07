class mysql ($password){

  $packages = ["mysql-server", "libmysqld-dev", "libmysqlclient-dev"]
  package { $packages: ensure => installed}

  file {"/etc/mysql/my.cnf":
    path => "/etc/mysql/my.cnf",
    mode => 0644,
    owner => root,
    group => root,
    ensure => file,
    require => Package["mysql-server"],
    notify => Service["mysql"],
    content => template("mysql/my.cnf"),
  }

  service { "mysql":
    ensure => running,
    enable => true,
    hasrestart => true,
    subscribe => [Package["mysql-server"],
                  File["/etc/mysql/my.cnf"]],
  }

  # First run? Set up the root user.
  exec { "set-mysql-root-password":
    unless => "mysqladmin -uroot -p$password status",
    path => ["/bin", "/usr/bin"],
    command => "mysqladmin -uroot password $password",
    require => Package["mysql-server"],
  }

}
