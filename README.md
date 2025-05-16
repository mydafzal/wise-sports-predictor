# 🧠 WiseSports AI - Score Prediction Pipeline for NBA & MLB

WiseSports is a modular AI-based pipeline for predicting NBA and MLB game outcomes. This system includes ingestion, preprocessing, model inference, and a RESTful FastAPI interface to serve predictions.

---

## 🗂 Project Structure

```

WISESPORTS/
│
├── Artifacts/                 # Stores model artifacts and outputs
├── config/                   # Configuration files
├── logs/                     # Logging directory
├── models/                   # Saved model files
├── myenv/                    # Virtual environment (excluded in production)
├── Research/                 # Notebooks, experiments, R\&D
│
├── routes/                   # FastAPI route files
│   ├── mlb\_adjustedpredictions.py
│   ├── mlb\_finalscores.py
│   ├── mlb\_modelpredictions.py
│   ├── nba\_injuries.py
│   └── nba\_predictions.py
│
├── src/                      # Core logic of the pipelines
│   ├── WiseSportsAI\_MLB/     # Full MLB pipeline
│   ├── WiseSportsAI\_NBA/     # Full NBA pipeline
│   └── WiseSportsAI.egg-info/
│
├── utils/                    # Utility scripts
│
├── app.py                    # FastAPI app entrypoint
├── main.py                   # Main launcher
├── pipeline.py               # Pipeline runner (supports --sport argument)
├── start.sh                  # Script to trigger the pipeline
│
├── docker-compose.yml        # Docker Compose for service orchestration
├── Dockerfile                # Dockerfile for building image
├── setup.py                  # Packaging and installation script
├── params.yaml               # Parameter configuration
├── schema.yaml               # Data schemas
├── requirements.txt          # Project dependencies
└── README.md                 # You're here!

````

---

## ⚙️ Setup Instructions

### 🔧 1. Clone the Repository
```bash
git clone https://github.com/hamzaatccript/WiseSportsAI.git
cd WiseSportsAI
````

### 🐍 2. Create and Activate a Virtual Environment

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Pipeline

You can run the score prediction pipeline for **NBA** or **MLB** using:

```bash
# For NBA
python pipeline.py --sport NBA

# For MLB
python pipeline.py --sport MLB
```

Or simply use the provided shell script:

```bash
sh start.sh
```

---

## 🌐 Starting the FastAPI Server

To serve the predictions via API:

```bash
python3 app.py
```

Navigate to `http://localhost:8080/docs` to view the interactive Swagger UI.

---

## 🐳 Docker Deployment (Optional)

Build and run using Docker Compose:

```bash
docker-compose up --build
```

---

## ☁️ EC2 Deployment Guide

### 🛠 Prerequisites

* AWS EC2 Instance (Ubuntu recommended)
* `git`, `python3`, and `pip` installed
* Security group open on port `8080`

### 🔌 Step-by-step Instructions

1. **SSH into your EC2 instance**

```bash
ssh -i your-key.pem ubuntu@<your-ec2-ip>
```

2. **Clone the repository**

```bash
git clone https://github.com/yourusername/WiseSports.git
cd WiseSports
```

3. **Install Python and Pip (if not installed)**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

4. **Set up virtual environment**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

5. **Install requirements**

```bash
pip install -r requirements.txt
```

6. **Run the pipeline (NBA or MLB)**

```bash
sh start.sh
```

7. **Start FastAPI server**

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

8. **Access the API**
   Open your browser and go to:

```
http://<your-ec2-public-ip>:8000/docs
```

---


## 🧠 Authors & Maintainers

Developed and maintained by **WiseSports AI Team**


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.