<script lang="ts">
  import type { AudioPlayerProps, Transcriptions } from "$lib/types/mednote";
  import SpeakerBadge from "./SpeakerBadge.svelte";
  import { Icon } from "@steeze-ui/svelte-icon";
  import { Barcode, Language } from "@steeze-ui/carbon-icons";
  import { PlayFilledAlt } from "@steeze-ui/carbon-icons";
  import { audioWaveLoadingStore } from "$lib/stores/AudioWaveLoadingStore";
  import TranscriptAudioPlayer from "./TranscriptAudioPlayer.svelte";

  export let audioPlayerProps: AudioPlayerProps;
  export let groupedTranscripts: Record<string, Transcriptions>[] = [];

  export let isLoaded: boolean = false;
  export let isUploadingToS3: boolean;
</script>

{#if groupedTranscripts.length <= 0}
  <div class="flex flex-col justify-center items-center h-full text-center">
    {#if !$audioWaveLoadingStore && !isUploadingToS3}
      <p class="lg:text-4xl md:text-3xl">
        {isLoaded ? "Ready to transcribe" : "No transcripts available."}
      </p>
    {/if}
    <div class="flex justify-center items-center w-full">
      <slot />
    </div>
  </div>
{:else}
  {#each groupedTranscripts as group}
    {#each Object.keys(group) as speaker}
      <div class="bg-white shadow-lg rounded-lg p-4 mb-4">
        <div class="flex">
          <div class="text-sm font-semibold text-gray-500 mr-4">
            <SpeakerBadge {speaker} />
          </div>
          <div class="text-gray-700 text-justify grid grid-cols-2 gap-3">
            {#each group[speaker] as transcript}
              <div class="w-96">
                <p> {transcript.text}</p>
              </div>
              <!-- <div class="w-2">

              </div> -->
              <div class="w-100">

              </div>
              <!-- <TranscriptAudioPlayer transcription={transcript} /> -->
            {/each}
          </div>
        </div>
      </div>
    {/each}
  {/each}
{/if}
