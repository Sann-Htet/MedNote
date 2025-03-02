# Project Documentation for Mednote

## Requirment Specification

- Store
  - Upload and List
    - Upload audio files to S3
      - Or
    - Load list of Audio files from S3
- Prepare
  - Convert to WAV File
  - Run speech enhancements
  - Run Dirazation
- Transribe
  - Transcribe Wave to Text
- Report
  - Produce Reports
- Tag
  - Name Entity Recognition of Medical Terms
  - Custom User Tagging

### Store

- POST /storage/upload/presign
  - file_name
  - Geenrate Presign URL based on `file_name`
  - Returns full path to s3
- POST /storage/download/presign
  - Generate
- GET /storage/list

### Transcribe

- POST /transcribe/start
  - filePath = s3_path

## Pipeline

![First MVP](image-3png)
