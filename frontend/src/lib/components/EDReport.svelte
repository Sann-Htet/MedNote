<script lang="ts">
  import type { EvaluatedFile } from "$lib/types/mednote";
  import EdReportRow from "./EDReportRow.svelte";

  export let evaluated_files: EvaluatedFile[];
</script>

<table class="w-full text-sm text-left rtl:text-right text-darkgrey">
  <thead class="text-xs bg-lightgrey text-darkgrey uppercase">
    <tr>
      <th scope="col" class="px-5 py-3"> File Name </th>
      <th scope="col" class="px-5 py-3"> Hypothesis </th>
      <th scope="col" class="px-5 py-3"> Reference </th>
      <th scope="col" class="px-5 py-3"> WER </th>
      <th scope="col" class="px-5 py-3"> </th>
    </tr>
  </thead>
  <tbody>
    {#each evaluated_files as evaluated_data}
      <EdReportRow {evaluated_data} />
    {/each}
  </tbody>
</table>
