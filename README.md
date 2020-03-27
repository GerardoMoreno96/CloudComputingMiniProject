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
