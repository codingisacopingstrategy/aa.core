import os.path
from fabric.api import run, local, put, cd, sudo, env


def lgru():
    env.hosts = ['constant@oscillator.worm.org:222']
    env.path = '/var/www/vhosts/aa.lgru.net/'

def sarma():
    env.hosts = ['sarma@oralsite2.stdin.fr']
    env.path = '/home/sarma/www/fr.stdin.oralsite2/'

def aa():
    env.hosts = ['activearchives@activearchives.org']
    env.path = '/var/www/vhosts/activearchives.org/wsgi/vj13/'

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
        # put back the database and the git repository
        run('cp ../aa.core.%s.bak/run/aa.db run/' % timestamp)
        run('cp -r ../aa.core.%s.bak/run/repositories run/' % timestamp)
        # make alias media
        #run('ln -s /root/src/Django-1.2.1/django/contrib/admin/media/')

    # fixes permission issues
    sudo('chown -R %s:www-data %s' % (env.user, env.path))
    sudo('chmod -R g+w %saa.core' % env.path)
    sudo('apachectl graceful')
