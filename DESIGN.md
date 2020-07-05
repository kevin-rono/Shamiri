# Under the hood tour

Generally, most of the website's design was adopted from CS50 finance, homepage and survey.

1. Sign Up and Log in

There are 2 sign up options. One for users and one for administrators. The idea is the administrator accesses the user's data so as to evaluate
the depression levels and their progress throughout the intervention. When users sign up and log in, they are redirected to the homepage, while
when administrators sign up and log in, they are redirected to the users forms and answers. I implemented this by adding an admin field in the database
and checking whether one is an admin or user before signing up and logging in.

2. Eligibility and Intervention

The eligibility form is pretty standard, except where I implemented code to find the total score of the user's input in the PHQ-9 form. The user's data
from the form is recorded in a form table and displayed for the administrators through the record page.The user's answers to the intervention
questions are also recorded in the answers table and are accessed by the administrators through them answers page.

The rest of the website is pretty standard html, with links, images, and a bit of styling.