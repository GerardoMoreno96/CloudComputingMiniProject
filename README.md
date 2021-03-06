# Gym Progress Web App

The purpose of this webapp is to help people that go to the gym to record their progress in an easy and conventional way. This app makes calls to an external API hosted in https://wger.de/es/software/api in order get information about different routines depending on what part of the body you want to excercise.

Within this app, the user is able to update its age, weight and height whenever they find it convenient. Also, they can keep a record of their weight and personal records in an easy and conventional way.

The website's URL is:
https://www.gerrysgymapp.co.uk/

## How it works?
You can add, get,update or delete values in this app through the terminal or with the user interface that can be accesed at https://www.gerrysgymapp.co.uk/


### Terminal commands
<b>Register a new user in the database:</b>

/new_user_cli

The user must provide:
 * Name
 * Surname
 * Age (integer)
 * Gender (Male or Female)
 * Weight (float)
 * Height (float)
 * Password 

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"NAME","surname":"SURNAME","age":"IntegerNumber","gender":"Male/Female","weight":"FloatNumber","height":"FloatNumber","password":"PASSWORD"}' https://www.gerrysgymapp.co.uk/new_user_cli
```
<b>Get routines:</b>

You can get different workouts depending on what you want to excercise. This particular request is the one that makes a call to an external api in https://wger.de/es/software/api.
 The valid categories are:
 * Abs
 * Arms
 * Back
 * Calves
 * Chest
 * Legs
 * Shoulders 

Example:
```
https://www.gerrysgymapp.co.uk/external_routines/arms
```

<b>Delete user from the database:</b>

/delete_user

This command will delete all the information of the user from the different database tables, including weights and personal records.

The user must provide:
 * Name
 * Surname

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X DELETE -d '{"name":"NAME","surname":"SURNAME"}' https://www.gerrysgymapp.co.uk/delete_user
```

<b>Update user weight:</b>

/update_user_weight_cli

The user must provide:
 * Name
 * Surname
 * Weight (float)
 * Date (YYYY-mm-DD)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","weight":"FloatNum","date":"YYYY-mm-DD"}' https://www.gerrysgymapp.co.uk/update_user_weight_cli
```

<b>Update user height:</b>

/update_user_height

The user must provide:
 * Name
 * Surname
 * Height (float)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","height":"FloatNUmber"}' https://www.gerrysgymapp.co.uk/update_user_height
```

<b>Update user age:</b>

/update_user_height

The user must provide:
 * Name
 * Surname
 * Age (integer)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","age":"IntegerNUmber"}' https://www.gerrysgymapp.co.uk/update_user_age
```

<b> Add PR (personal record) for new excercise</b>

/set_user_pr_cli

Here you can set a pr for an excercise that you haven't recorded before
The user must provide:
 * Name
 * Surname
 * Excercise name (Text)
 * New record (Text)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"NAME","surname":"SURNAME","excercise_name":"EXCERCISE_NAME","new_record":"NEW_RECORD"}' https://www.gerrysgymapp.co.uk/set_user_pr_cli
```

<b> Update the value of an existing PR</b>

/update_user_pr_cli

Here you can update an existing pr to a new value.
The user must provide:
 * Name
 * Surname
 * Excercise name (Text)
 * New record (Text)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","excercise_name":"EXCERCISE_NAME","new_record":"NEW_RECORD"}' https://www.gerrysgymapp.co.uk/update_user_pr_cli
```
- - - -

### Deployment
#### Cassandra Container 
1.- Run cassandra in a Docker container and expose port 9042:
```
sudo docker run --name cassandra-cont -p 9042:9042 -d cassandra
```

2.- Access the cassandra container in iterative mode:
```
sudo docker exec -it cassandra-cont cqlsh
```

3.- Create a dedicated keyspace inside cassandra for the gym database:

```
CREATE KEYSPACE gym WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

4.- Create the database table for the users:
```
CREATE TABLE gym.users (
    Name text, 
    Surname text, 
    Age int, 
    Gender text, 
    Weight float, 
    Height float, 
    PRIMARY KEY (Name, Surname));
```
5- Create the database table for the accounts: 
```
CREATE TABLE gym.accounts (
    Name text, 
    Surname text, 
    Password text, 
    PRIMARY KEY (Name, Surname));
```
6- Create the database table for the weights: 
```
CREATE TABLE gym.weights (
    name text,
    new_date date,
    surname text,
    weight float,
    PRIMARY KEY (name, new_date,surname)
)WITH CLUSTERING ORDER BY(new_date desc);
```

7 - Create the database table for the PRs
```
CREATE TABLE gym.personal_records (
    name text,
    surname text,
    excercise_name text,
    new_record text,
    PRIMARY KEY (name,surname,excercise_name)
);
```
#### Nginx & Gunicorn setup
For this project, I used nginx as the web server. This is neccesary as I implemented https in this app, so a web server was a requirement.

1.- 
Install nginx
```
sudo apt install nginx
```

2.-
Install gunicorn using pip, nginx is the one that handles the static files and gunicorn is the responsible to execute python code
```
pip3 install gunicorn
```

3.-
Remove the default file for nginx and create your own 
```
sudo rm /etc/nginx/sites-enabled/default
sudo vim /etc/nginx/sites-enabled/gerapp 
```
The name for this app is going to be "gerapp" (My name is gerardo and this is an app, so this is a pun)


4.- Inside nginx, type in the following. In this case, "www.gerrysgymapp.co.uk" is the name of the domain that I bought with GoDaddy. I just had to point this DNS to my aws-ec2 elastic IP.

```
server {
        server_name www.gerrysgymapp.co.uk;

        location /static {
                alias /home/ubuntu/CloudComputingMiniProject/static;
        }
        

        location / {
                proxy_pass http://localhost:8000;
                include /etc/nginx/proxy_params;
                proxy_redirect off;
        }

}
```

5.- 
Restart nginx
```
sudo systemctl restart nginx
```

6.- Once nginx is configured, we use gunicorn to run the app. 
```
gunicorn -w 5 app:app
```
-w is the number of workers that you want in your app. This is calculated by multiplying (2*# of cores)+1.

After executing the above command, the app should be running fine.

#### Achieving https
Once we have nginx as our webserver, we can obtain a free SSL certificate through https://letsencrypt.org/. We can use the Cerbot instructions to get the certificate for our webapp once we have selected the appropiate webserver and AMI running in our instance:

Add Certbot PPA:
```
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
```

Install cerbot:
```
sudo apt-get install certbot python-certbot-nginx
```

Get and install your certificates
```
sudo certbot --nginx
```

After completing the previous steps, we can see that https is now enabled in the webapp.

![](images/https1.png)


![](images/https2.png)


### Hash encryption
Another feature of this webapp is hash encryption. When a new user is registered in the app, its password will not be stored as plain text, instead it will be encrypted by using SHA256 and then it will be stored in the database. 

![](images/hashEncryption.png)
