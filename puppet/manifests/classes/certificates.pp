# Generate a self-signed certificate to match production.
class certificates ($server_name) {

  $certs_path = "/etc/ssl/local"

  package { "openssl":
    ensure => installed;
  }

  file { $certs_path:
    ensure => "directory",
    owner  => "root",
    group  => "root",
    mode => 600,
    require => Package[openssl];
  }

  exec { "openssl-generate-cert":
    command => "openssl req -new -x509 -days 365 -nodes -out $certs_path/$server_name.pem -keyout $certs_path/$server_name.key -subj '/C=US/ST=CA/L=Mountain View/O=Mozilla Foundation/OU=Webdev/CN=$server_name'",
    creates => ["/etc/ssl/local/$server_name.key", "/etc/ssl/local/$server_name.pem"],
    require => File[$certs_path];
  }
}
