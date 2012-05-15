# From: https://gist.github.com/2246574

define chrislea() {
  exec { "chrislea-repo-added-${name}" :
    command => "/usr/bin/add-apt-repository ppa:chris-lea/${name}",
    creates => "/etc/apt/sources.list.d/chris-lea-${name}-${lsbdistcodename}.list",
    require => Package["python-software-properties"],
  }


  exec { "chrislea-repo-ready-${name}" :
    command => "/usr/bin/apt-get update",
    require => Exec["chrislea-repo-added-${name}"],
    creates => "/var/lib/apt/lists/ppa.launchpad.net_chris-lea_${name}_ubuntu_dists_${lsbdistcodename}_Release",
    timeout => 3600,
  }
}

class nodejs {
  chrislea { 'node.js': }
  package { ["nodejs", "nodejs-dev", "npm"]:
    ensure => installed,
    require => Chrislea["node.js"],
  }

  # other packages we need, e.g. g++ to compile node-expat
  package { ["g++", "libexpat1-dev"]:
    ensure => installed,
  }
}
