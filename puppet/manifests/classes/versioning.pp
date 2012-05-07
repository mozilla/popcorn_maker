class versioning {
  case $operatingsystem {
    ubuntu: {
      $packages = ["git-core", "subversion", "mercurial"]
      package { $packages:
        ensure => installed;
      }
    }
  }
}
