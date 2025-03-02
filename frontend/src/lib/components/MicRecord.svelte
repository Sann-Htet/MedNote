<script lang="ts">
  import { Icon } from "@steeze-ui/svelte-icon";
  import { RecordingFilled, MicrophoneFilled } from "@steeze-ui/carbon-icons";

  import { onMount } from "svelte";
  import { createEventDispatcher } from "svelte";
  import { uploadAudioFile } from "$lib/api/mednote";
  import { Jumper, Wave } from "svelte-loading-spinners";
  const dispatch = createEventDispatcher();
  export let animateRecording: boolean = false;
  let audioPlayerSrc:string = "";
  export let uploadedAudioS3Url:string = "";
  let isRecording:boolean = false;

  let media: BlobPart[] = [];
  let mediaRecorder: MediaRecorder | null = null;

  onMount(async () => {
    const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e: BlobEvent) => media.push(e.data);
    mediaRecorder.onstop = function () {
      const blob: Blob = new Blob(media, { type: "audio/ogg; codecs=opus" });
      media = [];

      const fileName = `recorded_${Date.now()}.ogg`;

      // Create a File object from the Blob
      const file = new File([blob], fileName, {
        type: "audio/ogg; codecs=opus",
      });

      audioPlayerSrc = window.URL.createObjectURL(blob);
      dispatch("recorded", {"src":audioPlayerSrc,"file":file});
    };
  });

  function recordAudio() {
    uploadedAudioS3Url=""
    if (mediaRecorder) {
      if (!isRecording) {
        mediaRecorder.start();
      } else {
        mediaRecorder.stop();
      }

      animateRecording = !animateRecording;
      isRecording = !isRecording;
    }
  }
</script>

<div class="flex justify-center items-center ms-3">
  <button
    type="button"
    class="w-9 {isRecording ? 'text-primary' : 'text-darkgrey'} "
    on:click={recordAudio}
  >
    <Icon src={MicrophoneFilled} />
  </button>
  {#if isRecording}
    <Wave size="14" />
    <Jumper size="30" />
  {/if}
</div>
