<script lang="ts">
  export let speaker: string;
</script>

{#if speaker}
  <span
    class="bg-blue-100 text-blue-800 text-left text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300"
    >{speaker}</span
  >
{/if}
