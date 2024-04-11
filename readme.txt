PREREQUISITE SOFTWARES
- Node.js
- Python version 3.4 or later
- PostgreSQL with PgAdmin4
- Chocolatey

Extract the project
1.	Extract the .zip file to wherever you want.

Install Prerequisite software and packages on Windows

Install Chocolatey:
1.	Follow the directions at https://chocolatey.org/install#individual to install
	chocolatey for individuals
	
Install Node.js:
1.	Get the installer from https://nodejs.org/en/download/

2.	Verify installation by opening a command terminal and running:
		npm --version
	or
		node --version

Install PostgreSQL and PGadmin4
1.	Open command prompt -> Run as admin

2.	Run the command:		
		choco install postgresql
	*this will install the latest version of postgresql, which should be version 16.x.x
	*this should also include pgadmin4
	
3.	When prompted, enter 'Y'
	*Wait until the installation process finishes. It may take a couple minutes.
	
4.	Save your postgres password. During a successful installation, your cmd should give you a warning
	that looks like:
		WARNING: You did not specify a password for the postgres user so an insecure one has been generated for you. Please change it immediately.
		WARNING: Generated password: <your password>
	IMPORTANT!!!: Copy and save your generated password into the setup_local_db.py script.
	
	Open your the UEP_backend folder in windows explorer. <your extracted folder location>->UEP->UEP_backend
	
	Edit setup_local_db.py with your preferred text editor.
	Change line 6:
		mypassword = ""
	by pasting your generated password from installing postgres in the cmd terminal into the quotations.
	It should look something like: mypassword = "ad123423fda12341231a", but with your actual password.
	
	Save and close the script.

5.	After successful installation, go back to the cmd terminal and run the command:
		net start postgresql-x64-16
	*this service may already be started during the installation process, if so you will receive
	a prompt saying "The requested service has already been started." which is fine.

6.	Refresh your environment variabls to reflect PATH updates from installing postgresql.
	Run the command:
		refreshenv

Setup the backend server
1.	Open command prompt -> Run as admin (if you don't still have your cmd terminal open)

2.	Change directories to where you placed UEP. Open the UEP_backend folder.
	*your command line should look something like: "C:\Users\...\UEP\UEP_backend>"

3.	Make sure you have Python installed.
	Run the command:
		python --version
	If you receive a version number above 3, you are all good. Proceed to step 4.
	
	If you receive an error message then run the command:
		choco install python
	After successfully installing python, you will need to restart your environment variables.
	Run the command:
		refreshenv
	After which, running "python --version" should return your python version
	
4.	Install dependencies.
	Run the command:
		pip install -r requirements.txt
		*python 3.4 and later come with pip installed

5.	Run the command:
		python app.py
		
6.	Leave this terminal running
		
Start the frontend app

1.	Open a new command prompt

2.	Change directories to where you placed UEP. Open the frontend folder.
	*your command would look something like:
		cd C:\Users\...\UEP\UniversityEventPlanner\frontend
		
3.	Run the command:
		npm start
		
Create the first user and university

1.	Signup as a super admin role user



VIEWING THE DATABASE WITH PgAdmin4
1.	Open PgAdmin4
2.	Add a server group if there aren't any
3.	Register a new server by right clicking on the server group
	a.	Use "uep" for server name
	b.	Open the "Connection" tab
	c.	Set hostname to "localhost"
	d.	Set password to "password"
	e.	Toggle ON "save password"
	f.	In the bottom right, click "Save"

4.	Open the database SQL Query tool
	a.	Expand the uep server on the left-hand side by clicking on ">"
	b.	Expand "Databases"
	c.	Right click on "uep_db"
	d.	Select "Query Tool"

5.	Enter any queries you want. For example, if you enter "SELECT * FROM users;" The bottom
	of the screen will dislpay a GUI representing the users table
	