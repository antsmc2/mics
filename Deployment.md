### Deployment
**Setting Up VPS for Python Environment**:

Deployment involves packaging Web Application and putting it in a production environment that can run the application. A production environment is the canonical version of our current application and its associated data into live.

**Common Prerequisites**:

Python web application deployments are comprised of many pieces that need to be individually configured. Below is the list of components need to be set up to run a Python web application. Below diagram shows how each deployment component relates to each other.

1.	Servers
2.	Operating Systems supports any Linux OS (Ubuntu)
3.	Web Servers (Nginx)
4.	Source control (Git)
5.	Database (PostgreSQL)
6.	Application Dependencies
7.	WSGI Servers (Gunicorn)
8.	Task Queues (Redis Queue)
9.	Continuous Integration (Travis-CI)

A high-level overview of web application deployment architecture is presented in Figure 1.1
