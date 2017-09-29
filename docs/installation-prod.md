# MegaQC Installation: Production


1. Install the MegaQC package

    MegaQC is available on both the Python Package Index (PyPI) and conda (bioconda channel). 
    To install using PyPI,  run the following command:

    ```pip install megaqc```
    
    To install with conda:

    ```conda install -c bioconda megaqc```
    
2. Set up the database

    MegaQC uses the Flask SQLAlchemy plugin, meaning that it can be used with any SQL database (PostgreSQL, MySQL, SQLite and others).

    If you have a preference for any of the above, feel free to use that. The instructions below describe how to set up a PostgreSQL database.

    First, install PostgreSQL : 

    https://wiki.postgresql.org/wiki/Detailed_installation_guides:

    Then, install the Python package that handles requests :

    ```pip install psycopg2```

    MegaQC can assess wether the database to use is postgresql. If it is, it will try to connect as ```megaqc_user``` to the database ```megaqc``` on localhost:5432. On failure, megaqc will attempt to create the user and the database, and will then export the schema. 

    In order to get this done, run :
    ```megaqc initdb```

    
3. Install and start the web server

    *Note : This step can be ignored if you wish to use gunicorn as your primary web server.*

    1. Install gunicorn

       ```pip install gunicorn```

    2. Start megaqc as a gunicorn wsgi app:

        ```gunicorn --log-file megaqc.log --timeout 300 megaqc.wsgi:app``` 

        *Note : We recommend using a long timeout as the data upload from MultiQC can take several minutes for large reports*
        
    At this point, MegaQC should be running on the default gunicorn port (8000)
    
    3. Create an apache proxy

        *Note : this is an example configuration that will map all http requests to the current server to MegaQC. It will also not filter anything.* 

        Update your apache configuration (```/usr/local/apache2/conf/httpd.conf```, ```/etc/apache2/apache2.conf```, ```/etc/httpd/conf/httpd.conf```...)
        to include, for instance (Apache 2.2):
        
```
<VirtualHost *:80>
  SetEnv proxy-sendcl 1
  ProxyPass / http://127.0.0.1:8000/
  ProxyPassReverse / http://127.0.0.1:8000/
  <Proxy *>
    Order Allow,Deny
    Allow from all
  </Proxy>
</VirtualHost>
```

    4. Restart apache
	```service restart httpd``` or equivalent.

You should now have a fully functionnal MegaQC server running.
