# Wise Sports Predictor

Wise Sports Predictor is a machine-learning pipeline and FastAPI service for NBA and MLB game predictions. It includes ingestion, preprocessing, model training, model inference, injury/weather adjustments, and REST endpoints for serving predictions.

## Highlights

- Separate NBA and MLB pipeline modules
- Data ingestion, preparation, preprocessing, model training, and prediction stages
- XGBoost and scikit-learn model workflow
- FastAPI routes for NBA predictions, injury impact, MLB final scores, model predictions, and adjusted predictions
- Docker and docker-compose support
- Config-driven pipeline with YAML schemas and parameters
- Reusable helpers, model schemas, and route-level APIs

## Tech Stack

- Python
- FastAPI
- Pandas
- NumPy
- scikit-learn
- XGBoost
- Pydantic
- Selenium
- Docker
- AWS SDK / boto3

## Project Structure

```text
src/
  WiseSportsAI_NBA/       NBA pipeline components and stages
  WiseSportsAI_MLB/       MLB pipeline components and stages

routes/                   FastAPI route modules
models/                   API schemas
config/                   YAML configuration loader
utils/                    shared helpers
Artifacts/                trained model artifacts and encoders

app.py                    FastAPI app entrypoint
pipeline.py               command-line pipeline runner
params.yaml               model and pipeline parameters
schema.yaml               expected data schema
Dockerfile                container image
docker-compose.yml        local service orchestration
```

## Local Development

```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

Run the pipeline:

```bash
python pipeline.py --sport NBA
python pipeline.py --sport MLB
```

Start the API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

Open Swagger docs at `http://localhost:8080/docs`.

## Docker

```bash
docker-compose up --build
```

## Security

Do not commit virtual environments, logs, local datasets, private model artifacts, cloud credentials, or production API keys.

