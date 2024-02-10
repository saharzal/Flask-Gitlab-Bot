# Flask-Gitlab-Bot
A bot powered by flask for automating gitlab tasks.

Requierment:
- **Flask:** web application framework of python
- **python-gitlab:** a Python package providing access to the GitLab server API.

    ```pip install -r requirements.txt```
- **Vercel**: (Optional) used for deploy.

    ```npm i -g vercel```
---

To start we should create a webhook on gitlab through `settings/webhooks` and use the our deployed app vercel endpoint for its address.

Steps to run the project:
    
1. Clone the project and navigate to it's directory.

2. Run: ```python3 -m venv my_env```
3. Run: ```source my_env/bin/activate```
4. Run: ```pip install -r requirements.txt```
5. We can run ```flask --app main run``` to make sure if the app works perfect locally.
6. Now we can deploy app by ```vercel``` and use the `deployed-app-address-vercel.com/webhook` as our webhook endpoint.

---

