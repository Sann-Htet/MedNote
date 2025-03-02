<script>
     import { Icon } from "@steeze-ui/svelte-icon";
     import { Close } from "@steeze-ui/carbon-icons";
     import SearchBox from "$lib/components/Searchbox.svelte";
     import { Modal, getModalStore } from "@skeletonlabs/skeleton";
     const modalStore = getModalStore();
    let menuVisible = false;
function toggleMenu() {
    menuVisible = !menuVisible;
  }
  let isNavBarVisible = false;

function toggleNavBar() {
  isNavBarVisible = !isNavBarVisible;
  menuVisible = false;
}
function openExistRecordForm() {
    modalStore.trigger({
      type: "component",
      component: "ExistAudioFormComponent",
    });
  }
let currentDate = new Date().toDateString();
</script>
<div class="flex relative lg:hidden sm:visible">
    <div class="flex items-center shadow-sm ">
      <SearchBox />
    </div>
    <!-- <button class="w-5 mx-2 text-darkgrey" on:click={toggleMenu}>
      <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button> -->
  </div>
  {#if menuVisible}
  <div class="absolute -top-3 -right-2 bg-white transform transition-transform ease-in-out duration-300 overflow-y-auto h-screen w-1/2 shadow-sm">
    <div class="flex flex-col mt-5 mx-3">
     <div class="flex">
      <div class="text-primary text-sm flex justify-center items-center " >
        <span class=" "> 
          {currentDate}
        </span>
    </div>
      <button class="w-8 text-primary ml-auto"  on:click={toggleNavBar}>
        <Icon src={Close} />
      </button>
     </div>
      <button class="flex my-2 shadow-sm justify-center items-center border border-primary rounded-lg text-primary"  on:click={openExistRecordForm}>
        <span class="text-sm"> Choose File</span>
      </button>
      
    </div>
  </div>
{/if}