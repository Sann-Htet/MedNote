<script>
  import { Icon } from "@steeze-ui/svelte-icon";
  import {
    ArrowRight,
    ChevronRight,
    Download,
    FolderOpen,
    MicrophoneFilled,
  } from "@steeze-ui/carbon-icons";
  import { Report, Reset, InProgress } from "@steeze-ui/carbon-icons";
  import { FileStorage } from "@steeze-ui/carbon-icons";
  import { Modal, getModalStore } from "@skeletonlabs/skeleton";
  import ProgressDialog from "./ProgressDialog.svelte";
  import EntityDetection from "./EntityDetection.svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  const modalStore = getModalStore();

  function openExistRecordForm() {
    modalStore.trigger({
      type: "component",
      component: "ExistAudioFormComponent",
    });
  }
  // start progress dialog
  let isProgressSidebarVisible = false;
  function toggleProgressSidebar() {
    isProgressSidebarVisible = !isProgressSidebarVisible;
    if (isProgressSidebarVisible) {
      isEntityDetectionVisible = false;
    }
  }
  let isOpenProgress = false;
  function toggleOpenProgress() {
    isOpenProgress = !isOpenProgress;
  }
  let isDeleteProgress = false;
  function toggleDeleteProgress() {
    isDeleteProgress = !isDeleteProgress;
  }
  // end progress dialog

  // start entity detection
  let isEntityDetectionVisible = false;
  function toggleEntityDetection() {
    isEntityDetectionVisible = !isEntityDetectionVisible;
    if (isEntityDetectionVisible) {
      isProgressSidebarVisible = false;
    }
  }
  // end entity detection
</script>

<aside
  id="separator-sidebar"
  class="fixed border border-darkgrey w-14 border-opacity-20 top-0 sm:right-0 -right-14 z-40 h-screen md:pt-32 pt-28 transition-transform -translate-x-full bg-lightgrey text-darkgrey border-r border-gray-200 sm:translate-x-0 dark:bg-gray-800 dark:border-gray-700"
  aria-label="Sidebar"
>
  <div class="h-full text-primary flex flex-col justify-between items-center">
    <div class="">
      <button
        class="flex relative flex-col items-center border-b-darkgrey py-4 px-4 text-xs font-bold"
        on:click={toggleProgressSidebar}
      >
        <div
          class="w-10 h-10 rounded-lg flex justify-center items-center hover:bg-primary hover:bg-opacity-10 {isProgressSidebarVisible
            ? 'bg-primary bg-opacity-10'
            : ' text-primary'}"
        >
          <Icon src={InProgress} size="24px" />
        </div>
      </button>
      <button
        class="flex flex-col items-center border-b-darkgrey py-4 px-4 text-xs font-bold"
        on:click={toggleEntityDetection}
      >
        <div
          class="w-10 h-10 rounded-lg flex justify-center items-center hover:bg-primary hover:bg-opacity-10 {isEntityDetectionVisible
            ? 'bg-primary bg-opacity-10'
            : ' text-primary'}"
        >
          <Icon src={Report} size="24px" />
        </div>
      </button>
      <button
        class="flex flex-col items-center border-b-darkgrey py-4 px-4 text-xs font-bold"
        on:click={openExistRecordForm}
      >
        <div
          class="w-10 h-10 rounded-lg flex justify-center items-center hover:bg-primary hover:bg-opacity-10"
        >
          <Icon src={FolderOpen} size="24px" />
        </div>
      </button>
    </div>
    <div class="mb-4">
     <slot/>
    </div>
  </div>
</aside>
{#if isProgressSidebarVisible}
  <ProgressDialog></ProgressDialog>
{/if}
{#if isEntityDetectionVisible}
  <EntityDetection></EntityDetection>
{/if}
