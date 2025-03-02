<script lang="ts">
  import type { EvaluatedFile } from "$lib/types/mednote";
  import { getAllWERScore } from "$lib/api/mednote";

  import { fly } from "svelte/transition";
  import { Circle } from "svelte-loading-spinners";
  import { createQuery } from "@tanstack/svelte-query";

  import EDReport from "$lib/components/EDReport.svelte";
  import EdView from "./EDView.svelte";

  $: evaluatedFiles = createQuery<EvaluatedFile[], Error>({
    queryKey: ["refetch-WERscore"],
    queryFn: async () => {
      return await getAllWERScore();
    },
    // refetchOnMount: "always",
    refetchOnWindowFocus: true,
    staleTime: Infinity,
  });
</script>

<div
  in:fly={{ x: 50, duration: 500 }}
  out:fly={{ x: 50, duration: 500 }}
  class="sidebar overflow-y-auto shadow-2xl absolute xl:w-1/2 w-3/4 md:right-14 right-12 top-0 z-30 h-screen pt-28 -mx-1 border-y border-l border-darkgrey border-opacity-50 rounded-tl-lg bg-white"
>
  <div class="bg-lightgrey sticky top-0 p-3 shadow-sm">
    <h2 class="font-semibold md:text-lg text-md mx-1 mt-3">Evaluations</h2>
  </div>
  <div class="px-4 py-3">
    <div class="w-full overflow-y-auto shadow-md sm:rounded-lg">
      {#if $evaluatedFiles.isLoading}
        <div class="h-screen flex items-center justify-center">
          <Circle size="100" color="#3089F0" />
        </div>
      {:else if $evaluatedFiles.isSuccess}
        <EDReport evaluated_files={$evaluatedFiles.data} />
      {/if}
      <!-- <EdView></EdView> -->
    </div>
  </div>
</div>
