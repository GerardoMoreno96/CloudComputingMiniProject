# Gym Progress Web App

The purpose of this webapp is to help people that go to the gym to record their progress in an easy and conventional way. This app makes calls to an external API hosted in https://wger.de/es/software/api in order get information about different routines depending on what part of the body you want to excercise.

Whithin this app, the user is able to update its age, weight and height whenever they find it convenient.


### How it works?

<u>Register a new user in the database: </u>

/new_client - 
 Markup : The user must provide:
              * Name
              * Surname
              * Age (integer)
              * Sex (Male or Female)
              * Weight (float)
              * Height (float)

In the following json format:

```
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"#NAME#","surname":"#SURNAME#","age":"#Integer Number#","sex":"#Male/Female#","weight":"#Float Number#","height":"#Float Number"}' 0.0.0.0:5000/new_client

```
