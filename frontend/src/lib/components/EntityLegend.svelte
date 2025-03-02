<script lang="ts">
  import { fly } from "svelte/transition";
  import { colors } from "../../entityLegend";
  import { showEntityLabelStore} from "$lib/stores/EntityDetectionStore";

  const colorKeys: string[] = Object.keys(colors) as string[];
  let isShowButtonActive = false;
//  function toggleLegendLabel(event: Event, toggle: boolean): void {

//     const targetElement = event.target as HTMLElement;
//     if (toggle) {
//         targetElement.classList.add("text-black", "text-xs");
//     } else {
//         targetElement.classList.remove("text-black", "text-xs");
//     }
//     showEntityLabelStore.set(toggle);
//  }
function toggleLegendLabel(event: Event, toggle: boolean) : void{
    isShowButtonActive = toggle;
    showEntityLabelStore.set(toggle);
  }
</script>

<div
  in:fly={{ y: 30, duration: 500 }}
  out:fly={{ y: 30, duration: 500 }}
  class="w-full overflow-y-auto z-30 h-2/3 mt-2 bg-white border border-darkgrey border-opacity-10 rounded-t-lg shadow"
>
  <div class="sticky flex justify-between top-0 bg-white p-2">
    <h3 class="font-semibold mx-2">NER Legend</h3>
    <div
      class="bg-darkgrey bg-opacity-10 border border-darkgrey border-opacity-15 relative rounded-full select-none cursor-pointer flex"
    >
      <button
        class="transition relative rounded-full text-sm w-11 h-full flex items-center justify-center font-bold"
        class:bg-primary={!isShowButtonActive} class:text-white={!isShowButtonActive}
        on:click={(event)=>toggleLegendLabel(event, false)}>Hide</button
      >
      <button
        class="transition relative rounded-full text-sm w-11 h-full flex items-center justify-center font-bold "
        class:bg-primary={isShowButtonActive} class:text-white={isShowButtonActive}
        on:click={(event)=>toggleLegendLabel(event,true)}>Show</button
      >
  </div>
  </div>
  <div class="flex flex-wrap px-2 pb-2">
    {#each colorKeys as colorKey}
      <span
        class="mx-2 my-1 p-1 rounded text-xs font-medium"
        style="background-color: {colors[colorKey]};"
      >
        {colorKey.replace("_", " ")}
      </span>
    {/each}
  </div>
  <div class="mx-3">
    <mark
      class="inline-block text-sm px-3 py-1 m-1 rounded relative"
      style="background-color: {colors.WEIGHT};"
    >
      105lb
      <span
        class="entity font-bold uppercase align-middle ml-2 bg-white p-1 rounded border border-darkgrey border-opacity-10"
        style="font-size: 9px;">WEIGHT</span
      >
    </mark>
  </div>
</div>
