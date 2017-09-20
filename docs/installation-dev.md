# MegaQC Installation: Development


1. Install the MegaQC package

    MegaQC is available on both the Python Package Index (PyPI) and conda (bioconda channel). 
    To install using PyPI,  run the following command:

    ```pip install megaqc```
    
    To install with conda:

    ```conda install -c bioconda megaqc```
    
2. Set the variable for the development mode : 

    ```export MEGAQC_DEBUG=1```

2. Set up the database

    ```megaqc initdb```

3. Start megaqc
    ```megaqc run``` 
    
You should now have a fully functionnal MegaQC test server running, accessible on 127.0.0.1:5000.
