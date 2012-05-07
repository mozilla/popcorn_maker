# Project specific setup
# TODO: Make this rely on things that are not straight-up exec.
class playdoh ($project_path, $project_name, $username, $password){

  file { "$project_path/popcorn_gallery/settings/local.py":
    ensure => file,
    source => "$project_path/popcorn_gallery/settings/local.py-dist",
    replace => false;
  }

  exec { "create_mysql_database":
    command => "mysql -uroot -p$password -B -e'CREATE DATABASE `$project_name` CHARACTER SET utf8;'",
    unless  => "mysql -uroot -p$password  -B --skip-column-names -e 'show databases' | /bin/grep '$project_name'",
    require => File["$project_path/popcorn_gallery/settings/local.py"]
  }

  exec { "grant_mysql_database":
    command => "mysql -uroot -p$password  -B -e \"GRANT ALL PRIVILEGES ON $project_name.* TO '$project_name'@'localhost' IDENTIFIED BY '$project_name'\"",
    unless  => "mysql -uroot -p$password -B --skip-column-names mysql -e 'select user from user' | grep '$project_name'",
    require => Exec["create_mysql_database"];
  }

  exec { "syncdb":
    cwd => "$project_path",
    command => "python manage.py syncdb --noinput",
    require => Exec["grant_mysql_database"];
  }

}
