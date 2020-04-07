# Gym Progress Web App

The purpose of this webapp is to help people that go to the gym to record their progress in an easy and conventional way. This app makes calls to an external API hosted in https://wger.de/es/software/api in order get information about different routines depending on what part of the body you want to excercise.

Whithin this app, the user is able to update its age, weight and height whenever they find it convenient. Also, they can keep a record of their weight and personal records in an easy and conventional way.

The website's URL is:
https://www.gerrysgymapp.co.uk/

## How it works?
You can add, get,update or delete values in this app through the terminal or with the user interface that can be accesed at https://www.gerrysgymapp.co.uk/


### Terminal commands
<b>Register a new user in the database:</b>

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
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"NAME","surname":"SURNAME","age":"IntegerNumber","sex":"Male/Female","weight":"FloatNumber","height":"FloatNumber","password":"PASSWORD"}' https://www.gerrysgymapp.co.uk/new_user_cli
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

<b>Delete user from the database:</b> #Update this

/delete_user - 
 The user must provide:
 * Name
 * Surname

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X DELETE -d '{"name":"NAME","surname":"SURNAME"}' https://www.gerrysgymapp.co.uk/delete_user
```

<b>Update user weight:</b>

/update_user_weight_cli - 
 The user must provide:
 * Name
 * Surname
 * Weight (float)
 * Date (YYYY-mm-DD)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","weight":"FloatNum","date","YYYY-mm-DD"}' https://www.gerrysgymapp.co.uk/update_user_weight_cli
```

<b>Update user height:</b>

/update_user_height - 
 The user must provide:
 * Name
 * Surname
 * Height (float)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","height":"FloatNUmber"}' https://www.gerrysgymapp.co.uk/update_user_height
```

<b>Update user age:</b>

/update_user_height - 
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
CREATE TABLE gym.users (Name text, Surname text, Age int, Sex text, Weight float, Height float, PRIMARY KEY (Name, Surname));
```
4.5- 
CREATE TABLE gym.accounts (Name text, Surname text, Password text, PRIMARY KEY (Name, Surname));

4.6- 
CREATE TABLE gym.weights (
    name text,
    new_date date,
    surname text,
    weight float,
    PRIMARY KEY (name, new_date,surname)
)WITH CLUSTERING ORDER BY(new_date desc);

4.7 -
CREATE TABLE gym.personal_records (
    name text,
    surname text,
    excercise_name text,
    new_record text,
    PRIMARY KEY (name,surname,excercise_name)
);

5.- Build our own Docker image:
```
sudo docker build . --tag=gymprogress:v1
```

6.- Run the container for our image:
```
sudo docker run -p 5000:5000 gymprogress:v1
```

After that, the webapp will be accessible at port 5000