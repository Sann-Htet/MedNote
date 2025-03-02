import { writable } from "svelte/store";

interface AudioUrls {
  aws_url: string;
  s3_url: string;
}

export const audioUrlStore = writable<AudioUrls>({ aws_url: "", s3_url: "" });
