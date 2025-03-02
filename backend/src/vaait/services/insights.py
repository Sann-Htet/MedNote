from ollama import AsyncClient


async def transcript_to_soap(prompt: str) -> dict:
    message = {"role": "user", "content": prompt}
    assistant = {"role": "assistant", "content": " "}
    return await AsyncClient("medllm:11434").chat(
        model="soapdoc:latest",
        format="json",
        messages=[message, assistant],
        options={"temperature": 0, "num_ctx": 16000, "repeat_penalty": 1.0},
        keep_alive=0,
    )


async def ner_to_soap(prompt: str) -> dict:
    message = {"role": "user", "content": prompt}
    assistant = {"role": "assistant", "content": " "}
    return await AsyncClient("medllm:11434").chat(
        model="nersoap:latest",
        format="json",
        messages=[message, assistant],
        options={"temperature": 0, "num_ctx": 16000, "repeat_penalty": 1.0},
        keep_alive=0,
    )
