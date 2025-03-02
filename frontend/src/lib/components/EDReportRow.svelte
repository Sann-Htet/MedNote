<script lang="ts">
    import type { EvaluatedFile } from "$lib/types/mednote";
    import { Icon } from "@steeze-ui/svelte-icon";
    import { Download, MicrophoneFilled } from "@steeze-ui/carbon-icons";
    import { Report } from "@steeze-ui/carbon-icons";
    import {
        downloadReferenceFile,
        downloadTranscriptJSON,
    } from "$lib/api/mednote";
    export let evaluated_data: EvaluatedFile;
</script>

<tr class="bg-white border-b border-darkgrey border-opacity-20 shadow-sm">
    <th scope="row" class="px-5 py-4 font-medium text-darkgrey">
        <div class="flex">
            <div class="w-5 me-1">
                <Icon src={MicrophoneFilled} />
            </div>
            <span class="w-full">{evaluated_data.file_name}</span>
        </div>
    </th>
    <td class="px-5 py-4">
        <!--  Hypotesis download button  -->
        <button
            type="button"
            class="text-darkgrey flex justify-center items-center bg-white border border-gray-300 hover:bg-lightgrey rounded-lg text-xs p-1"
            on:click={() => downloadTranscriptJSON(evaluated_data.file_name)}
        >
            Download
            <div class="w-4 ms-1">
                <Icon src={Download} />
            </div>
        </button>
    </td>
    <td class="px-5 py-4">
        <!--  reference download button  -->
        <button
            type="button"
            class="text-darkgrey flex justify-center items-center bg-white border border-gray-300 hover:bg-lightgrey rounded-lg text-xs p-1"
            on:click={() => downloadReferenceFile(evaluated_data.file_name)}
        >
            Download
            <div class="w-4 ms-1">
                <Icon src={Download} />
            </div>
        </button>
    </td>
    <td class="px-5 py-4">
        <span class="text-xs">{evaluated_data.wer_score}</span>
    </td>
    <td class="px-5 py-4">
        <button
            class="text-primary w-20 flex justify-center items-center bg-white border border-primary hover:bg-primary hover:text-white rounded-lg text-xs p-1"
        >
            View
            <div class="w-4 ms-1">
                <Icon src={Report} />
            </div>
        </button>
    </td>
</tr>
