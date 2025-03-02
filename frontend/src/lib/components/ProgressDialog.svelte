<script>
    import { Icon } from "@steeze-ui/svelte-icon";
    import { ChevronDown } from "@steeze-ui/carbon-icons";
    import { Close } from "@steeze-ui/carbon-icons";
    import { Circle } from "svelte-loading-spinners";
    import { slide,fly } from 'svelte/transition';
    let isSideBarVisible = false;
    function toggleSideBar(){
        isSideBarVisible = !isSideBarVisible;
    }
    let isOpenProgress = false;
    function toggleOpenProgress(){
        isOpenProgress = !isOpenProgress;
    }
    let isDeleteProgress = false;
    function toggleDeleteProgress(){
        isDeleteProgress = !isDeleteProgress;
    }

</script>

<div in:fly={{ x: 50, duration: 500 }} out:fly={{ x: 50, duration: 500 }} class="sidebar overflow-auto shadow-2xl absolute xl:w-1/4 md:w-1/2 w-3/4 md:right-14 right-12 top-0  z-30 h-screen md:pt-32 pt-28 -mx-1 border-y border-l border-darkgrey border-opacity-50 rounded-tl-lg bg-white ">
  <div class="bg-lightgrey sticky top-0 p-3 shadow-sm">
    <h2 class="font-semibold text-lg mx-1">Progress Dialog</h2>
  </div>
  <div class="px-4">
    <!-- progress card -->
    <div class="w-full my-3 bg-primary bg-opacity-10 rounded-md p-3 border border-darkgrey border-opacity-20 
    {isOpenProgress ? ' -mb-1' : ' -mb-1'}">
      <div class="flex justify-between mb-1">
      <div class="w-4/5">
        <h3 class="font-semibold text-sm">File name : JFK.wav</h3>
      </div>
      
        <div class="flex">
          <button class="h-5 md:h-6 mx-2 " on:click={toggleOpenProgress}>
            <Icon src={ChevronDown} />
          </button>
          <button class="h-5 md:h-6" on:click={toggleDeleteProgress}>
            <Icon src={Close} />
          </button>
        </div>
      </div>
      {#if isDeleteProgress}
      <div class="flex  items-center text-xs text-primary w-full">
        <span class="me-2">The progress should be gone at this point</span>
        <button class="w-12 py-1 bg-white rounded-sm me-2"> Cancel</button>
        <button class="bg-primary text-white w-12 py-1 rounded-sm"> OK</button>
    </div>
      {:else}
      <div class="flex items-center text-xs text-primary">
          <span class="me-2">Updates in progress...</span>
          <Circle size="15" color="#3089F0" unit="px" duration="1s" />
      </div>
      {/if}
    </div>
    {#if isOpenProgress}
      <div transition:slide class="bg-white border border-darkgrey border-opacity-20 px-4 py-1 shadow-top ">
          <div class="grid grid-cols-4 items-center rounded sm:p-2 p-1 my-1 bg-primary bg-opacity-10 text-primary">
            <span class="font-semibold text-xs m-1">Upload</span>
            <div class="w-full bg-white m-1 col-span-2 rounded-full ">
              <div class="bg-primary text-xs font-medium text-white text-center  leading-none rounded-full" style="width: 80%;font-size: 10px"> 80%</div>
            </div>
            <span style="font-size: 10px;" class=" text-darkgrey ml-auto m-1">182/256 GB</span>
          </div>
          <div class="grid grid-cols-4 items-center rounded sm:p-2 p-1 my-1 bg-primary bg-opacity-10 text-primary">
            <span class="font-semibold text-xs m-1">Transcript</span>
            <div class="w-full bg-white m-1 col-span-2 rounded-full ">
              <div class="bg-primary font-medium text-white text-center  leading-none rounded-full" style="width: 50%;font-size: 10px"> 50%</div>
            </div>
            <span style="font-size: 10px;" class=" text-darkgrey ml-auto m-1">182/256 GB</span>
          </div>
          <div class="grid grid-cols-4 items-center rounded sm:p-2 p-1 my-1 bg-primary bg-opacity-10 text-primary">
            <span class="font-semibold text-xs m-1">Diarizing</span>
            <div class="w-full bg-white m-1 col-span-2 rounded-full ">
              <div class="bg-primary text-xs font-medium text-white text-center  leading-none rounded-full" style="width: 50%;font-size: 10px"> 50%</div>
            </div>
            <span style="font-size: 10px;" class=" text-darkgrey ml-auto m-1">182/256 GB</span>
          </div>
      </div>
    {/if}
    <!-- progress card end -->
      <!-- progress card -->
    <div class="w-full my-3 bg-primary bg-opacity-10 rounded-md p-3 border border-darkgrey border-opacity-20">
      <div class="flex justify-between mb-1">
        <div class="w-4/5">
        <h3 class="font-semibold text-sm">File name: my-sound-reocrding.ogg my-soundr-reocrding.ogg</h3>
        </div>
        <div class="flex">
          <div class="h-5 md:h-6 mx-2 ">
            <Icon src={ChevronDown} />
          </div>
          <div class="h-5 md:h-6">
            <Icon src={Close} />
          </div>
        </div>
      </div>
      <div class="flex justify-center items-center text-xs text-primary">
        <a href="" class="underline">Show in folder</a> 
        <div class="w-1 h-1 flex justify-center items-center bg-primary rounded-full mx-2"></div>
        <span>256 GB</span>
        <span class="ml-auto">22 hours ago</span>
      </div>
    </div>
    <!-- progress card end -->
  </div>
</div>
