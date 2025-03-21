# RQG Translation API

A fast and efficient translation API based on Meta's NLLB-200 (No Language Left Behind) model. This API provides translation services between multiple languages with automatic language detection.

## Features

- Translate text between 200+ languages
- Automatic source language detection
- RESTful API with FastAPI
- GPU acceleration support
- Containerized deployment with Docker
- Configurable debug logging

## Technologies Used

- **NLLB-200**: Meta's neural machine translation model
- **FastAPI**: Modern, high-performance web framework for building APIs
- **Hugging Face Transformers**: Library for working with pre-trained language models
- **PyTorch**: Deep learning framework
- **Docker**: Containerization platform

## Getting Started

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for better performance)
- Docker and Docker Compose (for containerized deployment)

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rqg-translation-api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r Code3/requirements.txt
```

4. Download the NLLB-200 model:
```bash
cd Code3
python models/save_models.py
```

5. Run the API:
```bash
cd Code3
python main.py
```

### Docker Deployment

1. Build and start the container using Docker Compose:
```bash
cd Code3
docker-compose up -d
```

2. To stop the container:
```bash
docker-compose down
```

### Running on RunPod.io

This API is designed to be deployed as a serverless container on RunPod.io:

1. Build the Docker image:
```bash
cd Code3
docker build -t rqg-translation-api:1.0 -f docker/Dockerfile .
```

2. Push the image to a container registry accessible by RunPod.

3. Create a new serverless endpoint on RunPod, specifying your image.

## API Usage

### Translating Text

**Endpoint**: `POST /api/translate`

**Request Body**:
```json
{
  "text": "Hello, how are you?",
  "target_language": "fr",
  "source_language": null
}
```

- `text`: The text to translate
- `target_language`: The target language code (ISO 639-1)
- `source_language`: Optional source language code (ISO 639-1). If not provided, auto-detection is used

**Response**:
```json
{
  "translated_text": "Bonjour, comment allez-vous?",
  "source_language": "en",
  "target_language": "fr"
}
```

### Health Check

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "ok"
}
```

## Environment Variables

- `DEBUG`: Set to "true" to enable debug-level logging (default: "false")
- `PORT`: The port to run the API on (default: 8000)

## Language Support

The API supports 200+ languages from the NLLB-200 model. Common language codes include:

- `en`: English
- `fr`: French
- `es`: Spanish
- `de`: German
- `zh`: Chinese
- `ru`: Russian
- `ja`: Japanese
- `ar`: Arabic

For a complete list of supported languages, refer to the NLLB-200 documentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Meta AI for the NLLB-200 model
- Hugging Face for providing access to the model through their transformers library 