# playdoh-specific commands that get playdoh all going so you don't
# have to.

# TODO: Make this rely on things that are not straight-up exec.
class playdoh {

    file { "$PROJ_DIR/popcorn_gallery/settings/local.py":
        ensure => file,
        source => "$PROJ_DIR/popcorn_gallery/settings/local.py-dist",
        replace => false;
    }

    exec { "create_mysql_database":
        command => "mysql -uroot -p$DB_PASS -B -e'CREATE DATABASE $DB_NAME CHARACTER SET utf8;'",
        unless  => "mysql -uroot -p$DB_PASS  -B --skip-column-names -e 'show databases' | /bin/grep '$DB_NAME'",
        require => File["$PROJ_DIR/popcorn_gallery/settings/local.py"]
    }

    exec { "grant_mysql_database":
        command => "mysql -uroot -p$DB_PASS  -B -e'GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@localhost # IDENTIFIED BY \"$DB_PASS\"'",
        unless  => "mysql -uroot -p$DB_PASS -B --skip-column-names mysql -e 'select user from user' | grep '$DB_USER'",
        require => Exec["create_mysql_database"];
    }

    exec { "syncdb":
        cwd => "$PROJ_DIR",
        command => "python manage.py syncdb --noinput",
        require => Exec["grant_mysql_database"];
    }

}
