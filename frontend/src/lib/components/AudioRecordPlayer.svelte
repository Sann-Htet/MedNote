<script lang="ts">
  import type { AudioPlayerProps } from "$lib/types/mednote";
  import { Icon } from "@steeze-ui/svelte-icon";
  //   import '@steeze-ui/components/base.css'
  import { MicrophoneFilled, RecordingFilled } from "@steeze-ui/carbon-icons";
  import { uploadAudioFile } from "$lib/api/mednote";
  import { getModalStore } from "@skeletonlabs/skeleton";
  import { createEventDispatcher, onMount } from "svelte";
  import { PlayFilled, StopFilled } from "@steeze-ui/carbon-icons";
  import { Stretch } from "svelte-loading-spinners";
  import WaveSurfer from "wavesurfer.js";
  import RecordPlugin from "wavesurfer.js/plugins/record";
  import { audioWaveLoadingStore } from "$lib/stores/AudioWaveLoadingStore";

  export let audioPlayerProps: AudioPlayerProps;
  export let uploadedAudioS3Url: string = "";

  const dispatch = createEventDispatcher();
  const modalStore = getModalStore();

  let shownRecordWave = false;
  let isAudioPlaying = false;
  let isRecording = false;

  let media: BlobPart[] = [];
  let mediaRecorder: MediaRecorder;
  let record: any;

  let wavesurfer: WaveSurfer;
  let audioWavesurfer: WaveSurfer;

  let container: HTMLDivElement;
  let recordContainer: HTMLDivElement;

  async function handleMediaRecorderStop() {
    audioWaveLoadingStore.set(true);
    const blob: Blob = new Blob(media, { type: "audio/ogg; codecs=opus" });
    media = [];
    uploadedAudioS3Url = "";

    const fileName = `recorded_${Date.now()}.ogg`;
    const file = new File([blob], fileName, { type: "audio/ogg; codecs=opus" });
    console.log("uploadedAudioS3Url", uploadedAudioS3Url);
    audioPlayerProps.audioSrc = window.URL.createObjectURL(blob);
    loadAudioWave();
    try {
      uploadedAudioS3Url = await uploadAudioFile(file);
    } catch (error: any) {
      modalStore.trigger({
        type: "component",
        component: "InformPrompt",
        meta: "Failed to upload the recorded audio file. Please check your connection",
      });
    }
    console.log("S3 url", uploadedAudioS3Url);
    dispatch("uploaded", uploadedAudioS3Url);
  }

  function createWaveSurfer() {
    audioWaveLoadingStore.set(true);
    try {
      if (wavesurfer) {
        wavesurfer.destroy();
      }

      wavesurfer = WaveSurfer.create({
        container: container,
        waveColor: "#fff",
        progressColor: "#3089F0",
        height: audioPlayerProps.waveHeight,
        cursorColor: "#000",
        url: audioPlayerProps.audioSrc,
      });

      audioPlayerProps.isActive = true;

      wavesurfer.once("ready", function () {
        audioWaveLoadingStore.set(false);
      });

      wavesurfer.on("click", () => {
        wavesurfer.play();
        isAudioPlaying = true;
      });
      wavesurfer.on("finish", () => {
        isAudioPlaying = false;
      });
    } catch (error) {
      console.error("waveSurfer error", error);
    }
    return wavesurfer;
  }

  async function getMicrophonePerm() {
    const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e: BlobEvent) => media.push(e.data);
    mediaRecorder.onstop = await handleMediaRecorderStop;
    return mediaRecorder;
  }

  async function recordAudio() {
    dispatch("uploaded", "");
    if (mediaRecorder == null) {
      await getMicrophonePerm();
    }
    if (isRecording == false) {
      mediaRecorder.start();
      record.startRecording();
      shownRecordWave = true;

      audioPlayerProps.isActive = true;
    } else {
      record.stopRecording();
      mediaRecorder.stop();
      shownRecordWave = false;
    }

    isRecording = !isRecording;
  }

  function loadAudioWave() {
    createWaveSurfer();
  }

  $: {
    if (audioPlayerProps.isResetWaveForm) {
      if (wavesurfer) {
        wavesurfer.destroy();
      }
    }
    if (audioPlayerProps.audioSrc !== "") {
      let ws = createWaveSurfer();
      ws.seekTo(0);
    }
  }

  async function playAudio() {
    if (!audioPlayerProps.isActive || wavesurfer == null || isRecording) return;
    if (isAudioPlaying) {
      wavesurfer.pause();
      isAudioPlaying = false;
    } else {
      await wavesurfer.play();
      isAudioPlaying = true;
    }
  }

  const setupRecord = () => {
    dispatch("audioloaded", false);

    audioWavesurfer = WaveSurfer.create({
      container: recordContainer,
      waveColor: "#fff",
      height: audioPlayerProps.waveHeight,
    });
    record = audioWavesurfer.registerPlugin(
      RecordPlugin.create({
        scrollingWaveform: true,
        renderRecordedAudio: false,
      }),
    );
  };
  onMount(() => {
    /*
         RecordPlugin needs to be associated with the same WaveSurfer instance
         throughout the entire lifecycle of the recording.
    */
    setupRecord();
  });
</script>

<div class="flex justify-center items-center ms-3">
  <button
    type="button"
    class="md:w-9 w-8 {isRecording ? 'text-red' : 'text-darkgrey'} "
    on:click={recordAudio}
  >
    {#if isRecording}
      <Icon src={RecordingFilled} class="animate-pulse" />
    {:else}
      <Icon src={MicrophoneFilled} />
    {/if}
    <!-- <Icon src={MicrophoneFilled} /> -->
  </button>
</div>

<div class="flex items-center w-full">
  <div
    bind:this={recordContainer}
    class="h-11 w-full mx-2 bg-primary {audioPlayerProps.isActive
      ? 'bg-opacity-60'
      : 'bg-opacity-10'} text-primary rounded-lg {shownRecordWave
      ? ''
      : 'hidden'}"
  ></div>

  <div
    bind:this={container}
    class="h-11 w-full mx-2 bg-primary {audioPlayerProps.isActive
      ? 'bg-opacity-60'
      : 'bg-opacity-10'} text-primary rounded-lg {$audioWaveLoadingStore ||
    isRecording
      ? 'hidden'
      : ''}"
  ></div>
  {#if $audioWaveLoadingStore}
    <div
      class="flex justify-center bg-primary bg-opacity-60 items-center h-11 w-full mx-2"
    >
      <Stretch size="40" color="#fff" />
      <Stretch size="40" color="#fff" />
      <Stretch size="40" color="#fff" />
      <Stretch size="40" color="#fff" />
      <Stretch size="40" color="#fff" />
      <Stretch size="40" color="#fff" />
    </div>
  {/if}
  <button
    on:click={playAudio}
    type="button"
    class="h-11 text-primary"
    aria-disabled={audioPlayerProps.isActive}
  >
    <Icon src={isAudioPlaying ? StopFilled : PlayFilled} />
  </button>
</div>
