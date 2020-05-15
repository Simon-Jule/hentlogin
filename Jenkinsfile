node {
    stage 'Checkout'
        checkout scm
    stage 'Build and UnitTest'
        docker.image('mysql:5').withRun('-e "MYSQL_ROOT_PASSWORD=root"') { c ->
            docker.image('mysql:5').inside("--link ${c.id}:db") {
                /* Wait until mysql service is up */
                sh 'while ! mysqladmin ping -hdb --silent; do sleep 1; done'
            }
            docker.image('python:3.7.2').inside("--link ${c.id}:db") {
                /*
                * Run some tests which require MySQL, and assume that it is
                * available on the host name `db`
                */
                sh 'pip install -r requirements.txt'
                sh 'python test.py'
                /*sh 'make check'*/
            }
        }
    stage 'Deploy'
        sh 'docker build -t hentlogin .'
        sh 'docker run -it -d hentlogin'
}