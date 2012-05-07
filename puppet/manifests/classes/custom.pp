# custom helpers for the app
class custom {
  $packages = ['vim', 'curl', 'ack-grep']
  package { $packages:
    ensure => installed
  }
}
