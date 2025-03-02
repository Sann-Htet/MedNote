<script lang="ts">
  import type {
    AudioPlayerProps,
    SoapJsonType,
    Transcriptions,
  } from "$lib/types/mednote";
  import { Icon } from "@steeze-ui/svelte-icon";
  import {
    FileStorage,
    RepoArtifact,
    CaretRight,
    Send,
    Reset,
  } from "@steeze-ui/carbon-icons";

  import {
    uploadAudioFile,
    startProcessing,
    loadSoapInsights,
    loadSoapInsightsFromEntity,
    uploadReference,
    calculateWER,
    submitTranscript,
    downloadJSON,
    groupTranscriptBySpeaker,
    submitReport,
  } from "$lib/api/mednote";
  import logo from "$lib/images/mednote.svg";
  import { Circle, Jumper, Wave } from "svelte-loading-spinners";
  import { tweened } from "svelte/motion";
  import { cubicOut } from "svelte/easing";
  import { getModalStore } from "@skeletonlabs/skeleton";
  import { audioUrlStore } from "$lib/stores/AudioUrlStore";
  import { audioWaveLoadingStore } from "$lib/stores/AudioWaveLoadingStore";
  import {
    isEntityDetectionStore,
    isEntittDetectionLoadingStore,
  } from "$lib/stores/EntityDetectionStore";

  import AudioRecordPlayer from "$lib/components/AudioRecordPlayer.svelte";
  import EntityLegend from "$lib/components/EntityLegend.svelte";
  import Transcript from "$lib/components/Transcript.svelte";
  import SearchBox from "$lib/components/Searchbox.svelte";
  import Calendar from "$lib/components/Calendar.svelte";
  import Insight from "$lib/components/Insight.svelte";
  import SideNav from "$lib/components/SideNav.svelte";
  import SideBar from "$lib/components/SideBar.svelte";

  const modalStore = getModalStore();

  let audioFileElement: HTMLInputElement;
  let referenceFileElement: HTMLInputElement;

  let audioFile: File | null = null;
  let referenceFile: File | null = null;

  let uploadedAudioS3Url: string = "";
  let referenceStr: string = "";

  let time = new Date();

  let transcriptions: Transcriptions = [];
  let report: SoapJsonType | undefined;
  let isTranscripting: boolean;
  let isCreatingReport: boolean;
  let hasWERScore: boolean;
  let isUploadingToS3: boolean;

  let WERScore: string;
  let isJsonView: boolean = true;
  let isChecked = false;
  $: seconds = time.getSeconds();

  let groupedTranscripts: Record<string, Transcriptions>[] = [];

  let audioPlayerProps: AudioPlayerProps = {
    isActive: false,
    audioSrc: "",
    waveHeight: 44,
    isResetWaveForm: false,
  };

  function triggerAudioFileInput() {
    audioFileElement?.click();
  }

  async function uploadRefFile() {
    referenceFileElement?.click();
  }

  function s3UploadedHandler(event: CustomEvent<any>) {
    uploadedAudioS3Url = event.detail;
    if (!uploadedAudioS3Url) {
      resetStates();
    }
  }

  function showInformPrompt(message: string) {
    modalStore.trigger({
      type: "component",
      component: "InformPrompt",
      meta: message,
    });
  }

  async function handleAudioFileChange(event: Event) {
    resetStates();
    const target = event.target as HTMLInputElement;
    uploadedAudioS3Url = "";
    if (!target.files || target.files.length <= 0) {
      return;
    }
    audioWaveLoadingStore.set(true);
    isUploadingToS3 = true;
    hasWERScore = false;

    audioFile = target.files[0];
    const objectURL = URL.createObjectURL(audioFile);
    audioPlayerProps.audioSrc = objectURL;
    audioPlayerProps.isActive = true;
    audioPlayerProps = audioPlayerProps;
    try {
      console.log("Uploading audio file to S3", isUploadingToS3);
      uploadedAudioS3Url = await uploadAudioFile(audioFile);
      isUploadingToS3 = false;
      console.log("Uploading audio file to S3", isUploadingToS3);
      console.log("S3 URL ", uploadedAudioS3Url);
    } catch (error: any) {
      showInformPrompt(error.message);
    }
  }

  async function handleRefFile(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files || target.files.length <= 0) {
      return;
    }
    referenceFile = target.files[0];
    try {
      referenceStr = await uploadReference(referenceFile);
      WERScore = await calculateWER(
        uploadedAudioS3Url,
        transcriptions,
        referenceStr,
      );
      uploadedAudioS3Url = "";
      hasWERScore = true;
    } catch (error: any) {
      showInformPrompt(error.message);
    }
  }

  async function loadReport(
    loadFunction: (transcriptions: Transcriptions) => Promise<any>,
  ) {
    if (transcriptions.length <= 0) {
      showInformPrompt("Please generate transcripts first to create a report");
      return;
    }
    isCreatingReport = true;
    console.log("is loading", isCreatingReport);
    try {
      let insights = await loadFunction(transcriptions);
      report = JSON.parse(insights.message.content);
    } catch (error: any) {
      showInformPrompt(error.message);
    } finally {
      isCreatingReport = false;
    }
  }

  $: {
    if ($audioUrlStore?.aws_url) {
      audioWaveLoadingStore.set(true);
      transcriptions = [];
      groupedTranscripts = [];
      hasWERScore = false;
      report = undefined;
      uploadedAudioS3Url = $audioUrlStore.s3_url;
      audioPlayerProps.audioSrc = $audioUrlStore.aws_url;
    }
  }

  const size = tweened(1, {
    duration: 300,
    easing: cubicOut,
  });

  function handleClick() {
    $size += 1;
  }
  async function transcribe() {
    console.log("uploadedAudioS3Url :", uploadedAudioS3Url);
    isTranscripting = true;
    transcriptions = [];
    groupedTranscripts = [];
    try {
      transcriptions = await startProcessing(uploadedAudioS3Url);
      groupTranscriptBySpeaker(transcriptions).then((result) => {
        groupedTranscripts = result;
      });
    } catch (error: any) {
      showInformPrompt(error.message);
    } finally {
      isTranscripting = false;
    }
  }

  function toggleInsightFormat() {
    isJsonView = !isJsonView;
  }

  function resetStates() {
    audioWaveLoadingStore.set(false);
    isTranscripting = false;
    isCreatingReport = false;
    hasWERScore = false;
    transcriptions = [];
    groupedTranscripts = [];
    report = undefined;
    WERScore = "";
    uploadedAudioS3Url = "";

    audioPlayerProps.isActive = false;
    audioPlayerProps.audioSrc = "";
    audioPlayerProps = audioPlayerProps;
    audioPlayerProps.isResetWaveForm = true;
    $audioUrlStore.aws_url = "";
    $audioUrlStore.s3_url = "";
  }
  function downloadTranscriptFile() {
    const fileName = uploadedAudioS3Url.split("/").pop();
    downloadJSON(transcriptions, `${fileName}.transcript.json`);
  }
  function downloadReport() {
    const fileName = uploadedAudioS3Url.split("/").pop();
    if (report) {
      downloadJSON(report, `${fileName}.report.json`);
    }
  }

  async function submitTranscriptToS3() {
    try {
      const url = await submitTranscript(transcriptions);
      let message = "Submission to S3 is complete!";
      modalStore.trigger({
        type: "component",
        component: "InformPromptSubmit",
        meta: { url, message },
      });
    } catch (error: any) {
      showInformPrompt(error.message);
    }
  }
  async function submitReportToS3() {
    try {
      const url = await submitReport(report);
      let message = "Report successfully submitted to S3!";
      modalStore.trigger({
        type: "component",
        component: "InformPromptSubmit",
        meta: { url, message },
      });
    } catch (error: any) {
      showInformPrompt(error.message);
    }
  }
</script>

<header
  class="h-[7rem] xl:h-[8rem] z-50 px-2 lg:px-10 md:px-5 sm:px-3 py-1 rounded-sm sticky top-0 bg-lightgrey border border-darkgrey border-opacity-20"
>
  <nav
    class="relative mx-auto flex items-center justify-between xl:py-2 lg:py-1 py-2"
  >
    <div class="flex items-center justify-center relative">
      <div class="xl:w-12 lg:w-10 w-9">
        <img src={logo} alt="" class="" />
      </div>
      <h1 class="font-bold lg:text-xl mx-2">Mednote</h1>
    </div>
    <Calendar></Calendar>

    <SideNav></SideNav>
    <div class="relative hidden md:hidden lg:flex sm:hidden">
      <div class="">
        <SearchBox />
      </div>
    </div>
  </nav>
  <div class="flex flex-row sm:mx-2 mt-1 mb-3 items-center">
    <div class="">
      <input
        type="file"
        bind:this={audioFileElement}
        on:change={handleAudioFileChange}
        accept="audio/*"
        style="display: none;"
      />
      <button
        on:click={triggerAudioFileInput}
        class="border bg-secondary rounded lg:p-2 md:p-2 p-1 text-lightgrey cursor-pointer"
        >Upload</button
      >
    </div>

    <div class="flex w-full justify-center items-center">
      <AudioRecordPlayer
        {uploadedAudioS3Url}
        {audioPlayerProps}
        on:uploaded={s3UploadedHandler}
      />
    </div>
  </div>
</header>

<section
  class=" lg:px-10 md:px-5 sm:px-3 py-3 h-[calc(100%-7rem)] xl:h-[calc(100%-8rem)]"
>
  <div
    id="appShell"
    class="flex h-full flex-col gap-2 sm:mr-12 mr-14 lg:flex-row lg:gap-0 md:flex-col md:gap-2 sm:flex-col"
    data-testid="app-shell"
  >
    <!-- transcript start -->
    <div
      class="basis-1/2 mx-2 border border-darkgrey rounded-lg flex flex-col shadow-lg"
    >
      <div class="flex items-center justify-between bg-lightgrey rounded-t-lg">
        <div class="flex items-center">
          <h1 class="md:text-xl text-md font-semibold md:mx-5 mx-3 py-3">
            Transcript
          </h1>
        </div>
        <div class="flex items-center me-5">
          {#if hasWERScore}
            <span class="text-xs font-semibold me-7">WER - {WERScore}</span>
          {/if}
          {#if transcriptions.length > 0}
            <button
              class="h-5 w-5 text-darkgrey"
              on:click={downloadTranscriptFile}
            >
              <Icon src={FileStorage} />
            </button>
          {/if}
        </div>
      </div>
      <div class="flex-grow h-full overflow-auto">
        {#if !isTranscripting}
          <Transcript
            {audioPlayerProps}
            {groupedTranscripts}
            {isUploadingToS3}
            isLoaded={uploadedAudioS3Url !== ""}
          >
            {#if uploadedAudioS3Url && !$audioWaveLoadingStore}
              <div
                class="mx-auto text-center flex flex-col justify-center items-center"
              >
                <p class="mb-6 font-light text-gray-500 md:text-lg">
                  {$audioWaveLoadingStore
                    ? "Audio file is being loaded..."
                    : "Audio file is loaded. Begin transcribing?"}
                </p>
                <button
                  on:click={transcribe}
                  disabled={$audioWaveLoadingStore}
                  class="flex justify-center items-center border border-darkgrey bg-primary sm:text-sm text-xs rounded sm:py-2 py-1 px-2 sm:px-3 text-lightgrey cursor-pointer"
                >
                  <div class="h-5 md:h-7 text-white">
                    <Icon src={CaretRight} />
                  </div>
                  <span class="me-2">
                    {$audioWaveLoadingStore
                      ? "Loading..."
                      : "Transcribe Now"}</span
                  >
                </button>
              </div>
            {:else if $audioWaveLoadingStore || isUploadingToS3}
              <div class="h-full flex items-center justify-center">
                <Circle size="100" color="#3089F0" />
              </div>
            {/if}
          </Transcript>
        {:else}
          <div class="h-full flex items-center justify-center">
            <Circle size="100" color="#3089F0" />
          </div>
        {/if}
      </div>
      {#if transcriptions.length > 0}
        <div class="mt-auto flex gap-3 justify-center items-center p-2">
          <input
            type="file"
            bind:this={referenceFileElement}
            on:change={handleRefFile}
            accept=".txt"
            style="display: none;"
          />
          <button
            class="py-2 md:w-1/2 xl:1/4 lg:w-1/3 text-primary border bg-primary-500 border-primary rounded text-xs sm:text-sm flex justify-center items-center"
            on:click={uploadRefFile}
          >
            <div class="h-5 md:h-7 text-primary">
              <Icon src={RepoArtifact} />
            </div>
            <span class="me-2">Evaluate Transcript</span>
          </button>

          <button
            class="py-2 md:w-1/2 xl:1/4 lg:w-1/3 text-white bg-primary border bg-primary-500 border-primary rounded text-xs sm:text-sm flex justify-center items-center"
            on:click={submitTranscriptToS3}
          >
            <!-- disabled={transcriptions.length <= 0} -->
            <div class="h-5 md:h-7 text-white">
              <Icon src={Send} />
            </div>
            <span class="me-2">Submit To S3</span>
          </button>
        </div>
      {/if}
    </div>
    <!-- transcript end -->

    <!-- insight start -->
    <div
      class="basis-1/2 mx-2 border border-darkgrey rounded-lg flex flex-col shadow-lg"
    >
      <div class="flex justify-between items-center bg-lightgrey rounded-t-lg">
        <h1 class="md:text-xl text-md font-semibold md:mx-5 mx-3 py-3">
          Insights
        </h1>
        {#if report}
          <div class="flex items-center me-5">
            <span>Entity</span>
            <div
              class="mx-5 bg-white p-1 rounded-md border border-darkgrey border-opacity-15"
            >
              <button
                class="px-2 py-1 bg-primary w-16 text-xs rounded-md font-bold text-darkgrey
        hover:bg-primary hover:text-white hover:border-primary
        {!$isEntityDetectionStore
                  ? 'bg-primary text-white border-primary  '
                  : 'bg-white '}"
                on:click={() => isEntityDetectionStore.set(false)}
                class:selected={!isJsonView}
              >
                Off
              </button>
              <button
                class="px-2 py-1 bg-primary w-16 text-xs rounded-md font-bold text-darkgrey
        hover:bg-primary hover:text-white hover:border-primary
        {$isEntityDetectionStore
                  ? 'bg-primary text-white border-primary font-bold '
                  : 'bg-white '}"
                on:click={() => isEntityDetectionStore.set(true)}
              >
                On
              </button>
            </div>
            {#if $isEntittDetectionLoadingStore == true}
              <div>
                <Wave size="20" color="#d60000"></Wave>
              </div>
            {/if}

            <div
              class="mx-5 bg-white p-1 rounded-md border border-darkgrey border-opacity-15"
            >
              <button
                class="px-2 py-1 bg-primary w-16 text-xs rounded-md font-bold text-darkgrey
      hover:bg-primary hover:text-white hover:border-primary
      {!isJsonView ? 'bg-primary text-white border-primary  ' : 'bg-white '}"
                on:click={toggleInsightFormat}
                class:selected={!isJsonView}
              >
                Text
              </button>
              <button
                class="px-2 py-1 bg-primary w-16 text-xs rounded-md font-bold text-darkgrey
      hover:bg-primary hover:text-white hover:border-primary
      {isJsonView
                  ? 'bg-primary text-white border-primary font-bold '
                  : 'bg-white '}"
                on:click={toggleInsightFormat}
              >
                Json
              </button>
            </div>
            <label class="inline-flex items-center cursor-pointer me-5">
              <input
                type="checkbox"
                bind:checked={isChecked}
                value=""
                class="sr-only peer"
              />
              <div
                class="relative w-11 h-6 bg-darkgrey bg-opacity-35 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-darkgrey after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"
              ></div>
            </label>
            <button class="h-5 w-5 text-darkgrey" on:click={downloadReport}>
              <Icon src={FileStorage} />
            </button>
          </div>
        {/if}
      </div>
      {#if isCreatingReport}
        <div class="h-full flex items-center justify-center">
          <Circle size="100" color="#3089F0" />
        </div>
      {:else if report}
        <div class="flex-grow h-full py-3 overflow-y-auto">
          <Insight {isJsonView} {report}></Insight>
        </div>
        {#if isChecked}
          <EntityLegend></EntityLegend>
        {/if}
        <div class="mt-auto z-45 flex gap-3 justify-center items-center p-2">
          <button
            class="py-2 md:w-1/2 xl:1/4 lg:w-1/3 text-white bg-primary border bg-primary-500 border-primary rounded text-xs sm:text-sm flex justify-center items-center"
            on:click={submitReportToS3}
          >
            <div class="h-5 md:h-7 text-white">
              <Icon src={Send} />
            </div>
            <span class="me-2">Report To S3</span>
          </button>
        </div>
      {:else}
        <div
          class="flex-grow flex-col h-full py-3 overflow-y-auto flex justify-center items-center"
        >
          {#if transcriptions.length === 0}
            <p class="lg:text-4xl md:text-3xl">No reports available.</p>
          {/if}
          {#if transcriptions.length > 0}
            <div
              class="mx-auto text-center flex flex-col justify-center items-center"
            >
              <h2
                class="mb-4 text-3xl tracking-tight font-extrabold leading-tight text-gray-900"
              >
                No Reports Available.
              </h2>
              <p class="mb-6 font-light text-gray-500 md:text-lg">
                You can start generation of SOAP Reports based on Transcripts.
              </p>
              <div class="flex">
                <button
                  class="border flex justify-center items-center border-darkgrey border-primary text-primary sm:text-sm text-xs rounded sm:py-2 py-1 px-2 sm:px-3 text-lightgrey cursor-pointer"
                  on:click={() => loadReport(loadSoapInsights)}
                >
                  <div class="h-5 md:h-7 text-primary">
                    <Icon src={CaretRight} />
                  </div>
                  <span class="me-2">Generate Now</span>
                </button>
                <button
                  class="border flex mx-3 justify-center items-center border-darkgrey bg-primary sm:text-sm text-xs rounded sm:py-2 py-1 px-2 sm:px-3 text-lightgrey cursor-pointer"
                  on:click={() => loadReport(loadSoapInsightsFromEntity)}
                >
                  <div class="h-5 text-white me-1">
                    <Icon src={Send} />
                  </div>
                  <span class="me-2">Generate Report - EE</span>
                </button>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
    <!-- insight end -->
  </div>
  <SideBar>
    <button
      class="flex flex-col items-center border-b-darkgrey py-4 px-4 text-xs font-bold"
      on:click={() => resetStates()}
    >
      <div
        class="w-8 h-8 bg-primary text-white rounded-full flex justify-center items-center"
      >
        <Icon src={Reset} size="24px" />
      </div>
    </button>
  </SideBar>
</section>
