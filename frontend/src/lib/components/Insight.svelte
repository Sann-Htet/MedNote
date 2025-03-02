<script lang="ts">
  import { JsonView } from "@zerodevx/svelte-json-view";
  import InsightContent from "./InsightContent.svelte";
  import type { SoapJsonType} from "$lib/types/mednote";
  export let isJsonView = false;
  export let report: SoapJsonType;
</script>

<div class="space-y-4 ps-5">
  {#if isJsonView}
    <div class="">
      <h1 class="text-darkgrey font-semibold pb-2">SOAP REPORT</h1>
      <div class="px-5">
        <JsonView json={report} />
      </div>
    </div>
  {:else}
    <InsightContent soap_json={report} />
  {/if}
</div>
