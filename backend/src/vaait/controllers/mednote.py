import io
import json
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import av
import boto3
import msgspec
import s3fs
from backend.src.vaait.services.extract_icd10_codes import retrieve_icd10_code
from backend.src.vaait.services.extractions import extract_entities_with_gliner, extract_entities_with_gliner_by_chunk
from backend.src.vaait.services.insights import ner_to_soap, transcript_to_soap
from backend.src.vaait.services.transcription import (
    calculate_error_rate,
    diarize_with_whisperx,
    transcribe_with_whisperx,
)
from backend.src.vaait.settings import aws
from mypy_boto3_s3 import S3Client

from litestar import MediaType, Request, Response, get, post
from litestar.controller import Controller
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body

boto3.setup_default_session()
s3: S3Client = boto3.client("s3")
s3_fs = s3fs.S3FileSystem()
s3_fs_submission = s3fs.S3FileSystem(key=aws.SUBMISSION_ID, secret=aws.SUBMISSION_KEY)


@dataclass
class Download:
    file_name: str


@dataclass
class S3Url:
    file_name: str


@dataclass
class DownloadUrl:
    url: str
    file_name: str


@dataclass
class Record:
    file_name: str
    url: str
    uploaded_date: datetime
    duration: str | None


@dataclass
class TranscribedData:
    file_name: str
    transcription: list[dict[str, Any]]
    reference: str


@dataclass
class Transcriptions:
    transcriptions: list[dict[str, Any]]


@dataclass
class SoapReport:
    soap_report: str


@dataclass
class Entities:
    entities: list[dict[str, Any]]


def get_audio_duration(file_temp: io.BytesIO, file_format: str) -> float:
    with av.open(file_temp, options={"format": file_format}) as container:
        duration = container.duration or 0
        duration_sec = duration / av.time_base
        minutes, seconds = divmod(duration_sec, 60)
        if minutes == 0 and seconds == 0:
            msg = "Audio file is empty - duration is zero sec."
            raise ValueError(msg)
        return duration_sec


class Storage(Controller):
    path = "/api/storage"
    tags = [__qualname__]

    @post(path="/upload")
    async def handle_file_upload(
        self,
        data: Annotated[dict[str, UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
        request: Request,
    ) -> dict[str, Any]:
        console = request.logger
        for file_obj in data.values():
            content = await file_obj.read()
            temp_file = io.BytesIO(content)
            key = f"{aws.S3_FOLDER}/uploads/{file_obj.filename}"

            try:
                temp_file.seek(0)
                s3.upload_fileobj(temp_file, aws.S3_BUCKET, key)
            except ValueError as e:
                console.info(f"An error occurred while processing file {file_obj.filename}, error: {e}")

        return {"url": key}

    @post(path="/submission")
    async def transcript_submission(
        self,
        data: Transcriptions,
        request: Request,
    ) -> dict[str, Any]:
        counter = 1
        base_submission_path = f"{aws.SUBMISSION_FOLDER}T1_Gate2_Encounter"
        while s3_fs_submission.exists(f"{base_submission_path}[{counter}].json"):
            counter += 1
        submission_path = f"{base_submission_path}[{counter}].json"
        request.logger.info(submission_path)
        request.logger.info(aws.SUBMISSION_ID)
        with s3_fs_submission.open(submission_path, "wb") as f2:
            f2.write(msgspec.json.encode(data))
        return {"url": submission_path}

    @post(path="/report/submission")
    async def report_submission(
        self,
        data: dict,
        request: Request,
    ) -> dict[str, Any]:
        counter = 1
        base_submission_path = f"{aws.SUBMISSION_FOLDER}T1_Gate2_Encounter"
        while s3_fs_submission.exists(f"{base_submission_path}[{counter}].SOAP.json"):
            counter += 1
        submission_path = f"{base_submission_path}[{counter}].SOAP.json"
        request.logger.info(submission_path)
        request.logger.info(aws.SUBMISSION_ID)
        with s3_fs_submission.open(submission_path, "wb") as f2:
            f2.write(msgspec.json.encode(data))
        return {"url": submission_path}

    @post(path="/download")
    async def get_download_url(self, data: Download) -> DownloadUrl:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": aws.S3_BUCKET, "Key": data.file_name},
            ExpiresIn=3600,
        )  # generate a pre-signed URL for uploading to S3, valid for 10 minute
        return {"url": response, "file_name": data.file_name}

    @get(path="/list_uploads")
    async def list_uploaded_files(self) -> list[str]:
        """List all files under 's3bucket/upload' in S3 and return them."""
        bucket_name = aws.S3_BUCKET
        prefix = f"{aws.S3_FOLDER}/uploads/"

        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"] != prefix]

    @get(path="/records/get_all")
    def get_records(self, request: Request) -> list[Record]:
        """List all files under 's3bucket/upload' in S3 and return them in Record format."""
        records = []
        prefix = f"{aws.S3_FOLDER}/uploads/"
        bucket_name = aws.S3_BUCKET
        console = request.logger
        try:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            for obj in response["Contents"]:
                file_name = obj["Key"].replace(prefix, "")
                url = obj["Key"]
                uploaded_date = obj["LastModified"]
                console.info(f"Working on the file: {file_name}")
                record = Record(file_name=file_name, url=url, uploaded_date=uploaded_date, duration=0)
                records.append(record)

        except Exception as e:  # noqa: BLE001
            console.info(f"An error occurred at file {file_name}, error: {e}")

        return {
            "records": records,
        }


class Transcribe(Controller):
    path = "/api/transcribe"
    tags = [__qualname__]

    async def _transcribe_and_diarize_audio(self, audio_stream: str) -> dict[str, Any]:
        try:
            segments, audio = transcribe_with_whisperx(audio_stream)
            diarized_transcriptions = diarize_with_whisperx(segments, audio)
        except Exception as e:  # noqa: BLE001
            msg = f"Error processing audio: {e}"
            raise ValueError(msg) from e
        return diarized_transcriptions

    async def _process_and_upload_transcripts_to_s3(
        self,
        audio_data: bytes,
        file_name_base: str,
        request: Request,
    ) -> dict[str, Any]:
        bucket_name = aws.S3_BUCKET
        console = request.logger

        with tempfile.NamedTemporaryFile(delete=False) as temp_file, io.BytesIO() as temp_buffer:
            temp_file.write(audio_data)
            diarized_transcripts = await self._transcribe_and_diarize_audio(temp_file.name)
            json_data = json.dumps(diarized_transcripts).encode("utf-8")
            temp_buffer.write(json_data)
            temp_buffer.seek(0)
            try:
                key = f"{aws.S3_FOLDER}/transcripts/{file_name_base}.json"
                s3.upload_fileobj(temp_buffer, bucket_name, key)
            except ValueError as e:
                console.info(f"An error occurred while processing file {file_name_base}.json, error :{e}")
        return diarized_transcripts

    @post(path="/start_processing_s3")
    async def process_audio_s3(
        self,
        data: S3Url,
        request: Request,
    ) -> dict[str, Any]:
        file_name_base = Path(data.file_name).stem
        transcript_key = f"{aws.S3_FOLDER}/transcripts/{file_name_base}.json"
        request.logger.info(transcript_key)
        # transcripe already exist
        if s3_fs.exists(f"{aws.S3_BUCKET}/{transcript_key}"):
            with s3_fs.open(f"{aws.S3_BUCKET}/{transcript_key}", "rb") as f:
                return f.read().decode("utf-8")
        else:
            with s3_fs.open(f"{aws.S3_BUCKET}/{data.file_name}", "rb") as f:
                return await self._process_and_upload_transcripts_to_s3(f.read(), file_name_base, request)

    @get(path="/download/{file_name:str}")
    async def download_transcript_file(
        self,
        file_name: str,
        request: Request,
    ) -> Response:
        file_name_base = Path(file_name).stem
        transcript_key = f"{aws.S3_FOLDER}/transcripts/{file_name_base}.json"

        # Check if the transcript already exists
        request.logger.info(transcript_key)
        if not s3_fs.exists(f"{aws.S3_BUCKET}/{transcript_key}"):
            return Response("Transcript file not found", status_code=404)
        try:
            with s3_fs.open(f"{aws.S3_BUCKET}/{transcript_key}", "r") as f:
                transcript_json = f.read()
                transcript_data = json.loads(transcript_json)
        except json.JSONDecodeError:
            return Response("Error parsing transcript JSON", status_code=500)

        if "transcription" in transcript_data:
            transcription_list = transcript_data["transcription"]
            # Format each transcription entry in the following format:
            # start-end -> text: "transcription text"
            # For example:  0.009-0.869 -> text: "What brought you in today?"
            transcript_text = "\n".join(
                f"{entry['start']}-{entry['end']} -> text: \"{entry['text']}\"" for entry in transcription_list
            )
        else:
            return Response("Transcription key not found in JSON", status_code=500)

        headers = {
            "Content-Disposition": f'attachment; filename="{file_name_base}.txt"',
            "Content-Type": "text/plain",
        }
        return Response(transcript_text, headers=headers)

    @post(path="/start_processing", sync_to_thread=True)
    async def process_audio(
        self,
        data: Annotated[dict[str, UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
        request: Request,
    ) -> dict[str, Any]:
        for file_obj in data.values():
            file_name_base = Path(file_obj.filename).stem
            content = await file_obj.read()
            diarized_transcripts = await self._process_and_upload_transcripts_to_s3(content, file_name_base, request)
        return diarized_transcripts

    @post(path="/calculate_error_rate")
    async def calculate_error_rate(
        self,
        data: Annotated[TranscribedData, Body(media_type=MediaType.JSON)],
    ) -> dict[str, Any]:
        try:
            transcriptions = data.transcription
            input_hypothesis = " ".join([transcription["text"] for transcription in transcriptions])

            input_reference = data.reference
            error_rate = "10"
            error_rate = calculate_error_rate(input_hypothesis, input_reference)

            json_file_key = f"{aws.S3_FOLDER}/error_rates.json"

            if s3_fs.exists(f"{aws.S3_BUCKET}/{json_file_key}"):
                with s3_fs.open(f"{aws.S3_BUCKET}/{json_file_key}", "r") as s3_file:
                    error_rates = json.load(s3_file)
            else:
                # Setting an empty dictionary if the file does not exist
                error_rates = {}

            error_rates[data.file_name] = error_rate

            # Writing the updated dictionary back to the JSON file in S3
            with s3_fs.open(f"{aws.S3_BUCKET}/{json_file_key}", "w") as s3_file:
                json.dump(error_rates, s3_file)
        except Exception as e:  # noqa: BLE001
            msg = f"Error calculating word error rate: {e}"
            raise ValueError(msg) from e

        return {"error_rate": error_rate}

    @get(path="/wer_scores/get_all")
    async def get_wer_scores(self, request: Request) -> dict[str, Any]:
        try:
            json_file_key = f"{aws.S3_FOLDER}/error_rates.json"

            if not s3_fs.exists(f"{aws.S3_BUCKET}/{json_file_key}"):
                return Response("error rate files file not found", status_code=404)

            # Reading the JSON file from S3
            with s3_fs.open(f"{aws.S3_BUCKET}/{json_file_key}", "r") as s3_file:
                return json.load(s3_file)

        except Exception as e:  # noqa: BLE001
            return Response(f"Error retrieving WER scores: {e}", status_code=500)


class Report(Controller):
    path = "/api/report"
    tags = [__qualname__]

    @post(path="/soap")
    async def soap_report(
        self,
        data: Transcriptions,
        request: Request,
    ) -> dict[str, Any]:
        transcriptions = data.transcriptions
        input_transcripts = "\n".join([transcription["text"] for transcription in transcriptions])
        request.logger.info(input_transcripts)
        return transcript_to_soap(input_transcripts)

    @post(path="/soap_from_entities")
    async def entities_soap_report(
        self,
        data: Entities,
        request: Request,
    ) -> dict[str, Any]:
        transcript_entities = data.entities
        input_transcript_entities = json.dumps(transcript_entities)
        request.logger.info(input_transcript_entities)
        return ner_to_soap(input_transcript_entities)


class Reference(Controller):
    path = "/api/reference"
    tags = [__qualname__]

    @post(path="/upload_file")
    async def upload_file(
        self,
        data: Annotated[dict[str, UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
        request: Request,
    ) -> dict[str, Any]:
        for file_obj in data.values():
            content = await file_obj.read()
            key = f"{aws.S3_FOLDER}/references/{file_obj.filename}"
            request.logger.info(key)
            with s3_fs.open(f"{aws.S3_BUCKET}/{key}", "wb") as s3_file:
                s3_file.write(content)
        return {"reference_data": content.decode("utf-8")}

    @get(path="/download_file/{file_name:str}")
    async def download_file_url(
        self,
        file_name: str,
        request: Request,
    ) -> DownloadUrl:
        file_name_base = Path(file_name).stem + ".txt"

        key = f"{aws.S3_FOLDER}/references/{file_name_base}"

        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": aws.S3_BUCKET, "Key": key},
            ExpiresIn=3600,
        )
        return {"url": response, "file_name": file_name_base}


class Extract(Controller):
    path = "/api/extract"
    tags = [__qualname__]

    @post(path="/extract_entity")
    async def extract_entity(self, data: SoapReport, request: Request) -> dict[str, Any]:
        soap_report_dict = json.loads(data.soap_report)
        formatted_results = {}
        request.logger.info(soap_report_dict)

        def process_section(section_name: str, section_content: Any, parent_dict: dict[str, Any] | None = None) -> None:
            if parent_dict is None:
                parent_dict = formatted_results
            if isinstance(section_content, str) and len(section_content) > 0:
                recognized_entities = extract_entities_with_gliner(section_content)
                parent_dict[section_name] = {
                    "text": section_content,
                    "entities": recognized_entities,
                }
            elif isinstance(section_content, dict):
                parent_dict[section_name] = {}
                for sub_section_name, sub_section_content in section_content.items():
                    process_section(sub_section_name, sub_section_content, parent_dict[section_name])
            elif isinstance(section_content, list):
                parent_dict[section_name] = []
                for index, item in enumerate(section_content):
                    # Using a temporary dictionary for each item in the list
                    temp_dict = {}
                    process_section(f"{section_name}_{index}", item, temp_dict)
                    parent_dict[section_name].append(temp_dict)

        for section_name, section_content in soap_report_dict.items():
            process_section(section_name, section_content)

        json_format = json.dumps(formatted_results)
        request.logger.info(json_format)
        return json_format


    @post(path="/extract_transcript_entity")
    async def extract_transcript_entity(
        self,
        data: Transcriptions,
        request: Request,
    ) -> dict[str, list[dict[str, Any]]]:
        transcriptions = data.transcriptions
        input_transcripts = "\n".join([transcription["text"] for transcription in transcriptions])
        request.logger.info(input_transcripts)
        result = extract_entities_with_gliner_by_chunk(input_transcripts)
        return {"entities": result}


    @post(path="/extract_icd10_codes")
    async def extract_icd10_codes(
        self,
        data: SoapReport,
        request: Request,
    ) -> dict[str, Any]:
        soap_report_dict = json.loads(data.soap_report)
        formatted_results = {}
        labels_for_icd10 = ["SIGN_SYMPTOM", "DISEASE_DISORDER"]

        def process_section(section_name: str, section_content: Any, parent_dict: dict[str, Any] | None = None) -> None:
            entities_with_icd10 = []
            if parent_dict is None:
                parent_dict = formatted_results
            if isinstance(section_content, str) and len(section_content) > 0:
                recognized_entities = extract_entities_with_gliner(section_content)
                for i in range(len(recognized_entities)):
                    if recognized_entities[i]["entity_group"] in labels_for_icd10:
                        icd10 = retrieve_icd10_code(recognized_entities[i]["word"])
                        recognized_entities[i]["icd10"] = icd10
                        entities_with_icd10.append(recognized_entities[i])
                parent_dict[section_name] = {
                    "text": section_content,
                    "entities": entities_with_icd10,
                }
            elif isinstance(section_content, dict):
                parent_dict[section_name] = {}
                for sub_section_name, sub_section_content in section_content.items():
                    process_section(sub_section_name, sub_section_content, parent_dict[section_name])
            elif isinstance(section_content, list):
                parent_dict[section_name] = []
                for index, item in enumerate(section_content):
                    # Using a temporary dictionary for each item in the list
                    temp_dict = {}
                    process_section(f"{section_name}_{index}", item, temp_dict)
                    parent_dict[section_name].append(temp_dict)

        for section_name, section_content in soap_report_dict.items():
            process_section(section_name, section_content)

        json_format = json.dumps(formatted_results)
        request.logger.info(json_format)
        return json_format
