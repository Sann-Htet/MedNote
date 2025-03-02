<script lang="ts">
  import type { AudioRecord } from "$lib/types/mednote";
  import { writable } from "svelte/store";
  import { Stretch } from "svelte-loading-spinners";
  import { createQuery } from "@tanstack/svelte-query";
  import { getRecords, getAudioFileByURL } from "$lib/api/mednote";
  import { audioUrlStore } from "$lib/stores/AudioUrlStore";
  import Record from "./Record.svelte";
  import { getModalStore } from "@skeletonlabs/skeleton";
  import { createEventDispatcher } from 'svelte';

  const modalStore = getModalStore();

  let isLoading: boolean;
  $: records = createQuery<AudioRecord[], Error>({
    queryKey: ["refetch-records"],
    queryFn: async () => {
      isLoading = true;
      return await getRecords();
    },
    // refetchOnMount: "always",
    refetchOnWindowFocus: true,
    staleTime: Infinity,
  });

  let selectedRecordURL: string = "";

  function handleSelectedRecord(event: CustomEvent<any>) {
    selectedRecordURL = event.detail.record_url;
  }

  async function loadAudioFile() {
    if (selectedRecordURL.length <= 0) {
      return;
    }

    try {
      let response = await getAudioFileByURL(selectedRecordURL);
      if (response && response.url) {
        audioUrlStore.set({ aws_url: response.url, s3_url: selectedRecordURL });
        modalStore.close();
      } else {
        console.error("No URL received for the audio file.");
      }
    } catch (error: any) {
      throw new Error(
        "Failed to load uploaded audio files. Please check your connection",
      );
    }
  }
</script>

<div
  class="flex justify-center items-center modal-transition h-screen min-h-full overflow-y-auto md:w-3/4 lg:w-2/5 sm:w-3/4 w-full max-h-[36rem]"
>
  <form
    action=""
    class="bg-white shadow-md card rounded-lg space-y-4 w-full mx-auto"
  >
    <div
      class=" bg-lightgrey rounded-t-lg flex justify-between items-center px-6"
    >
      <h1 class="text-xl font-semibold py-3">Existing Records</h1>
    </div>
    {#if $records.isSuccess}
      <div class=" overflow-y-auto max-h-[24rem] sm:rounded-lg">
        <table class="w-full text-sm text-left rtl:text-right text-darkgrey">
          <thead class="text-xs">
            <tr>
              <th scope="col" class="px-6"> Name </th>
              <th scope="col" class="px-6"> Duration </th>
              <th scope="col" class="px-6"> Date </th>
              <th scope="col" class="px-6">
                <span class="sr-only">Edit</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {#each $records.data as record}
              <Record
                on:selected={handleSelectedRecord}
                {record}
                selected={record.url === selectedRecordURL}
              />
            {/each}
          </tbody>
        </table>
      </div>
      <div class="flex justify-end px-6 py-2">
        <button
          class="border bg-primary rounded py-2 px-5 text-white cursor-pointer"
          on:click={loadAudioFile}
        >
          Load Audio File
        </button>
      </div>
    {:else if isLoading}
      <!-- loading... -->
      <div class="flex justify-center items-center h-12 pt-16 pb-16">
        <Stretch size="42" color="#3089F0" />
      </div>
    {:else if $records.isError}
      <div class="flex flex-col justify-center items-center h-24 pb-10 pt-5">
        <p class="mt-5 mb-4">{$records.error}</p>
        <!-- <button class="p-3  text-white bg-primary rounded-md"  on:click={getRecordAgain}>Retry</button> -->
      </div>
    {/if}
  </form>
</div>
