# Internet Measurements Environment using RIPE ATLAS

## Installation

* Download this project
* Download and install Docker and Docker-compose.
* In the same folder as docker-compose.yml run:
```sh
docker-compose build
docker-compose run
```
The first time it will download all packages so it might take a while.


## Big Campaign Results

[Cuca results ready for Mongo restore](https://www.dropbox.com/s/sy1fgcvkl5bni28/cuca.gz?dl=0)


### Configurations
To use RIPE ATLAS platform is required to have a user with credits and enable an API KEY. The API KEY must have access to create new measurements, delete measurements, and get information about running measurements.
Run (as to create the file python/code/my_key.py):
```sh
echo "ATLAS_API_KEY=your_api_key_here" >> my_key.py
```

Note: If not planning to run any measurement, run instead:
```sh
echo "ATLAS_API_KEY=''" >> my_key.py
```



## Usage

### Notebook
* Open the browser
* Go to http://localhost:8889
* When requested with a token, use: 1234.
* Navigate to notebooks for examples on how:
    1. To create a new Ripe Campaing (Sample Campaign Creation)
    2. The hitlist for cuca was ensambled (Final Hitlist Creation)
    3. To read results from database, process them and create a new graph.


### Console
* To access the python app:
```sh
docker exec -it myapp /bin/bash
```
* To access mongo:
```sh
docker exec -it mongodb /bin/bash
```

### Importing a database

Copy the content of the database in the dbIO folder in the host machine and run:
```sh
docker exec -it mongodb /bin/bash
cd dbIO
mongorestore --gzip --archive=`filename.gz` --db `dbname`
```
### Exporting a database

Generate a `.gz` of the database to restore later :
```sh
docker exec -it mongodb /bin/bash
cd dbIO
mongodump --gzip --archive=`filename` --db `dbname`
```
