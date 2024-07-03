# Insightful-Eyes

Introducing a groundbreaking LLM-powered guide designed to illuminate the world around you. Whether you're exploring historical landmarks, admiring vintage cars, examining intriguing objects, or observing beautiful houses, our innovative platform provides insightful explanations for everything you see. Unlock the stories behind the sights with our intelligent and intuitive guide, making every observation a rich and educational experience. It can become a very useful tool for blind persons.
<br>
<br>
<img src="images/1.png">
<img src="images/2.png">


# Steps to run it on local machine
### Clone the repository to your designated path
```bash
git clone https://github.com/MANMEET75/Insightful-Eyes.git
```
### Navigate to that specific directory
```bash
cd Insightful-Eyes/
```
### Create an environment using Anaconda
```bash
conda create -p venv python==3.11 -y
```
### Activate the Anaconda environment
```bash
conda activate venv/
```
### Open your IDE
```bash
code .
```
### Install all the requirements
```bash
pip install -r requirements.txt
```
### Run the FastAPI Python backend
```bash
uvicorn main:app --reload --port 3000
```
### Navigate to the following URL for the user interface
```bash
http://localhost:3000/
```
### Navigate to the following URL to open the Swagger API interface.
```bash
http://localhost:3000/docs
```
### Navigate to the following URL to open the customized ReDoc HTML
```bash
http://localhost:3000/redoc
```



#### Enjoy Coding!

