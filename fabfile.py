import os.path
from fabric.api import run, local, put, cd, sudo, env


def set_env(hostname):
    if hostname == 'sarma':
        env.user = 'sarma'
        env.path = '/home/sarma/www/fr.stdin.oralsite2/'
    elif hostname == 'oscillator':
        env.user = 'constant'
        env.path = '/var/www/vhosts/aa.lgru.net/'


def deploy(treeish='HEAD'):
    set_env(run('hostname'))

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
        # put back the database
        run('cp ../aa.core.%s.bak/run/aa.db run/' % timestamp)
        # make alias media
        #run('ln -s /root/src/Django-1.2.1/django/contrib/admin/media/')

    # fixes permission issues
    sudo('chown -R %s:www-data %s' % (env.user, env.path))
    sudo('chmod -R g+w %saa.core' % env.path)
    sudo('apachectl graceful')