import { PUBLIC_API_URL } from "$env/static/public";
import { PUBLIC_S3_FOLDER } from "$env/static/public";
import type {
  Transcriptions,
  Transcription,
  AudioRecord,
  statusCode,
  EvaluatedFile,
  Entity,
  ExtractedEntities,
} from "$lib/types/mednote";

export async function authFetch(
  path: string,
  settings?: RequestInit,
): Promise<Response> {
  try {
    settings = settings || {};
    settings.credentials = "include";
    console.log(`Fetch sent: ${PUBLIC_API_URL}/${path}` + "\n");
    return await fetch(`${PUBLIC_API_URL}/${path}`, settings);
  } catch (error) {
    throw new Error("Failed to fetch data. Please try again later.");
  }
}

export async function uploadAudioFile(audioFile: File): Promise<string> {
  try {
    const formData = new FormData();
    formData.append("file", audioFile);
    const response = await authFetch(`storage/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.url;
  } catch (error) {
    throw new Error("Failed to upload audio file. Please check the connection");
  }
}

export async function startProcessing(
  s3AudioURL: string,
): Promise<Transcriptions> {
  try {
    const response = await authFetch(`transcribe/start_processing_s3`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_name: s3AudioURL }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: { transcription: Transcriptions } = await response.json();
    console.log("Transcripts");
    console.log(data.transcription);
    return data.transcription;
  } catch (error) {
    throw new Error(
      `Failed to transcribe the audio file. ${
        error instanceof Error ? error.message : "Please check the connection."
      }`,
    );
  }
}

export async function getRecords(): Promise<AudioRecord[]> {
  try {
    const response = await authFetch(`storage/records/get_all`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: { records: AudioRecord[] } = await response.json();
    let format_data = data.records.map((record: AudioRecord) => {
      if (record.duration) {
        let durationF = parseFloat(record.duration);
        let minutes = Math.floor(durationF / 60);
        let seconds = Math.floor(durationF % 60);
        record.duration =
          minutes >= 1 ? `${minutes}min ${seconds}s` : `${seconds}s`;
      }
      const date = new Date(record.uploaded_date);
      const formattedDate =
        date.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }) +
        ", " +
        date.toLocaleDateString([], {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
        });
      record.formatted_date = formattedDate;
      return record;
    });
    return format_data;
  } catch (error) {
    throw new Error(
      "Failed to retrieve audio file. Please check the connection",
    );
  }
}

export async function downloadAudioFile(s3url: string): Promise<statusCode> {
  try {
    const response = await authFetch(`storage/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_name: s3url }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: { url: string; file_name: string } = await response.json();
    console.log("Download s3 url :", data.url);
    downloadFile(data.url, data.file_name);
    return { status: 200 };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to download audio file. Please try again later");
    }
  }
}

export async function getAudioFileByURL(url: string) {
  try {
    const response = await authFetch(`storage/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_name: url }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error("Failed to retrieve audio file. Please try again later");
  }
}
export async function loadSoapInsights(transcriptions: Transcriptions) {
  try {
    const response = await authFetch(`report/soap`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ transcriptions }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      `Failed to load SOAP insight. ${
        error instanceof Error ? error.message : "Please check the connection."
      }`,
    );
  }
}

export async function loadSoapInsightsFromEntity(
  transcriptions: Transcriptions,
) {
  try {
    const entities: ExtractedEntities =
      await extractEntityFromTranscript(transcriptions);
    console.log("Got extrated entities:", entities.entities);
    const response = await authFetch(`report/soap_from_entities`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ entities: entities.entities }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      `Failed to load SOAP insight From Entity Extraction. ${
        error instanceof Error ? error.message : "Please check the connection."
      }`,
    );
  }
}

export async function groupTranscriptBySpeaker(
  transcriptions: Transcriptions,
): Promise<Record<string, Transcriptions>[]> {
  const groupedTranscripts: Record<string, Transcription[]>[] = [];

  let currentGroup: Record<string, Transcription[]> | null = null;
  let currentSpeaker = "";

  for (const transcript of transcriptions) {
    // If this is the first transcript or the speaker has changed, start a new group
    if (!currentGroup || transcript.speaker !== currentSpeaker) {
      if (currentGroup) {
        groupedTranscripts.push(currentGroup);
      }
      // Creating a new group with the current speaker
      currentGroup = { [transcript.speaker]: [transcript] };
      currentSpeaker = transcript.speaker;
    } else {
      currentGroup[currentSpeaker].push(transcript);
    }
  }

  if (currentGroup) {
    groupedTranscripts.push(currentGroup);
  }
  console.log("Transcripts After grouping");
  console.log(groupedTranscripts);
  return groupedTranscripts;
}

export async function calculateWER(
  s3_file_path: string,
  transcription: Transcriptions,
  reference: string,
): Promise<string> {
  try {
    const prefix = `${PUBLIC_S3_FOLDER}/uploads/`;
    const fileName = s3_file_path.replace(prefix, "");
    const response = await authFetch(`transcribe/calculate_error_rate`, {
      method: "POST",
      body: JSON.stringify({ file_name: fileName, transcription, reference }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.error_rate;
  } catch (error) {
    throw new Error("Failed to calculate WER. Please try again");
  }
}
interface FileUploadEvent extends Event {
  target: HTMLInputElement;
}

export async function getAllWERScore() {
  try {
    const response = await authFetch(`transcribe/wer_scores/get_all`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    const evaluatedFiles: EvaluatedFile[] = Object.entries(data).map(
      ([file_name, wer_score]) => ({
        file_name,
        wer_score: (wer_score as number).toString(),
      }),
    );

    return evaluatedFiles;
  } catch (error) {
    throw new Error(
      "Failed to retrieve WER scrore. Please check your connection",
    );
  }
}

export const uploadReference = async (referenceFile: File) => {
  try {
    const formData = new FormData();
    formData.append("file", referenceFile);
    const response = await authFetch(`reference/upload_file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.reference_data;
  } catch (error) {
    throw new Error(
      "Failed to upload reference file. Please check the connection",
    );
  }
};

// Helper function to download a Blob as a file
async function downloadBlob(blob: Blob, fileName: string) {
  try {
    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.style.display = "none";
    a.href = blobUrl;
    a.download = fileName;

    document.body.appendChild(a);
    a.click();

    URL.revokeObjectURL(blobUrl);
    document.body.removeChild(a);

    return true;
  } catch (error) {
    throw new Error("Failed to download the file. Please try again");
  }
}

export async function downloadJSON(json_data: object, file_name?: string) {
  const blob = new Blob([JSON.stringify(json_data)], {
    type: "application/json",
  });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${file_name}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

async function downloadFile(s3URL: string, filePath: string) {
  try {
    const response = await fetch(s3URL);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    let fileName = filePath.split("/").pop();
    if (fileName) {
      return downloadBlob(blob, fileName);
    }
  } catch (error) {
    throw new Error("Failed to download the audio file. Please try again");
  }
}

export async function downloadTranscriptTxt(s3_file_path: string) {
  try {
    const prefix = `${PUBLIC_S3_FOLDER}/uploads/`;
    const fileName = s3_file_path.replace(prefix, "");

    const response = await authFetch(`transcribe/download/${fileName}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    return downloadBlob(blob, fileName + ".txt");
  } catch (error) {
    throw new Error("Failed to download transcript file. ");
  }
}

export async function downloadTranscriptJSON(s3_file_path: string) {
  const prefix = `${PUBLIC_S3_FOLDER}/uploads/`;
  const fileName = s3_file_path.replace(prefix, "");
  console.log("fileName");
  console.log(fileName);
  const response = await authFetch(`transcribe/start_processing_s3`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_name: fileName }),
  });
  console.log("response");
  console.log(response);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data: { transcription: Transcriptions } = await response.json();
  console.log("Transcripts Before grouping");
  console.log(data.transcription);
  downloadJSON(data.transcription, `${fileName}.transcript.json`);
}

export async function downloadInsightJSON(report: object) {
  try {
    const jsonString = JSON.stringify(report, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    return downloadBlob(blob, "report.json");
  } catch (error) {
    throw new Error("Failed to download JSON file. ");
  }
}

export async function downloadReferenceFile(file_path: string) {
  try {
    const prefix = `${PUBLIC_S3_FOLDER}/uploads/`;
    const fileName = file_path.replace(prefix, "");

    const response = await authFetch(`reference/download_file/${fileName}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: { url: string; file_name: string } = await response.json();

    downloadFile(data.url, data.file_name);
    return { status: 200 };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to download audio file. Please try again later");
    }
  }
}

export async function submitTranscript(
  transcriptions: Transcriptions,
): Promise<string> {
  try {
    const response = await authFetch(`storage/submission`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ transcriptions }),
    });
    const data: { url: string } = await response.json();
    return data.url;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to submit transcript. Please try again later");
    }
  }
}
export async function submitReport(report: object | undefined) {
  try {
    const response = await authFetch(`storage/report/submission`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ report: report }),
    });
    const data: { url: string } = await response.json();
    return data.url;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to submit transcript. Please try again later");
    }
  }
}

export async function extractEntity(
  soapReport: object | undefined,
): Promise<ExtractedEntities> {
  try {
    if (!soapReport || Object.keys(soapReport).length === 0) {
      throw new Error("soapReport is empty or undefined");
    }

    const requestBody = { soap_report: JSON.stringify(soapReport) };

    const response = await authFetch(`extract/extract_entity`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to extract entities. Please try again later");
    }
  }
}

async function extractEntityFromTranscript(
  transcriptions: Transcriptions,
): Promise<ExtractedEntities> {
  try {
    if (transcriptions.length <= 0) {
      throw new Error("soapReport is empty or undefined");
    }
    // const response = await fetch(`http://0.0.0.0:8000/api/extract/extract_transcript_entity`, {
    const response = await authFetch(`extract/extract_transcript_entity`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ transcriptions }),
    });
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`${error.message}`);
    } else {
      throw new Error("Failed to extract entities. Please try again later");
    }
  }
}
