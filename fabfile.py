import os.path
from fabric.api import run, local, put, cd, sudo, env


def lgru():
    env.hosts = ['constant@oscillator.worm.org:222']
    env.path = '/var/www/vhosts/aa.lgru.net/'
    env.git_path = '/home/constant/www/aa.lgru.net/db/repositories'
    env.media_path = '/home/constant/www/aa.lgru.net/static/media/'

def sarma():
    env.hosts = ['sarma@sarma.be']
    env.path = '/home/sarma/www/be.sarma/'
    env.git_path = '/home/sarma/www/be.sarma/db/repositories/'
    env.media_path = '/home/sarma/www/be.sarma/static/media/'

def aa():
    env.hosts = ['activearchives@activearchives.org']
    env.path = '/var/www/vhosts/activearchives.org/wsgi/vj13/'
    #env.git_path = '/home/sarma/www/be.sarma/db/repositories'
    #env.media_path = '/home/sarma/www/be.sarma/static/media/'

def fix_permissions():
    # fixes permission issues
    sudo('chown -R %s:www-data %s' % (env.user, env.path))
    sudo('chown -R www-data:www-data %s' % env.git_path)
    sudo('chmod -R g+w %saa.core' % env.path)
    sudo('apache2ctl graceful')

def deploy(treeish='HEAD'):
    # makes a tarball of the django project and transfers it
    local('git archive %s . | gzip > project.tar.gz' % treeish)
    put('project.tar.gz', env.path)
    local('rm project.tar.gz')

    # backups old versions
    with cd(env.path):
        import time
        timestamp = time.strftime('%Y%m%d%H%M%S')
        try:
            run('mv aa.core aa.core.%s.bak' % timestamp)
        except:
            pass
        run('mkdir aa.core')

    # gunzips the new django project
    with cd(env.path + 'aa.core/'):
        run('tar zxvf ../project.tar.gz')
        run('rm ../project.tar.gz')

    fix_permissions()
