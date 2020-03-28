# Gym Progress Web App

The purpose of this webapp is to help people that go to the gym to record their progress in an easy and conventional way. This app makes calls to an external API hosted in https://wger.de/es/software/api in order get information about different routines depending on what part of the body you want to excercise.

Whithin this app, the user is able to update its age, weight and height whenever they find it convenient.


### How it works?

<b>Register a new user in the database:</b>

/new_user - 
 The user must provide:
 * Name
 * Surname
 * Age (integer)
 * Sex (Male or Female)
 * Weight (float)
 * Height (float)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"NAME","surname":"SURNAME","age":"IntegerNumber","sex":"Male/Female","weight":"FloatNumber","height":"FloatNumber"}' 0.0.0.0:5000/new_user
```

<b>Get routines:</b>

/external_routines

<b>Delete user from the database:</b>

/delete_user - 
 The user must provide:
 * Name
 * Surname

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X DELETE -d '{"name":"NAME","surname":"SURNAME"}' 0.0.0.0:5000/delete_user
```

<b>Update user weight:</b>

/update_user_weight - 
 The user must provide:
 * Name
 * Surname
 * Weight (float)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","weight":"FloatNum"}' 0.0.0.0:5000/update_user_weight
```

<b>Update user height:</b>

/update_user_height - 
 The user must provide:
 * Name
 * Surname
 * Height (float)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","height":"FloatNumber"}' 0.0.0.0:5000/update_client_height
```

<b>Update user age:</b>

/update_user_height - 
 The user must provide:
 * Name
 * Surname
 * Age (integer)

In the following format and execute the command:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"NAME","surname":"SURNAME","age":"IntegerNumber"}' 0.0.0.0:5000/update_client_age
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
4.- 
CREATE TABLE gym.accounts (Name text, Surname text, Password text, PRIMARY KEY (Name, Surname));

5.- Build our own Docker image:
```
sudo docker build . --tag=gymprogress:v1
```

6.- Run the container for our image:
```
sudo docker run -p 5000:5000 gymprogress:v1
```

After that, the webapp will be accessible at port 5000