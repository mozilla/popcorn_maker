# Install python and compiled modules for project
class python ($project_path){
  case $operatingsystem {
    ubuntu: {
      $packages = ["python2.6-dev",
                   "python2.6",
                   "python-imaging",
                   "python-wsgi-intercept",
                   "python-pip",
                   "python-lxml"]
      package { $packages:
          ensure => installed,
      }
      exec { "virtualenvwrapper":
        command => "pip install virtualenv virtualenvwrapper",
        require => Package[$packages],
      }

      exec { "pip-install-compiled":
        cwd => "$project_path/requirements",
        command => "pip install -r $project_path/requirements/compiled.txt",
        require => Package[$packages],
      }

      exec { "pip-install-development":
        cwd => "$project_path/requirements",
        command => "pip install -r $project_path/requirements/dev.txt",
        require => Package[$packages],
      }

      exec { "install-project":
        cwd => "$project_path",
        command => "python $project_path/setup.py develop",
        require => Package[$packages],
      }
    }
  }
}
