<script lang="ts">
    import type { AudioRecord } from "$lib/types/mednote";
    import { Search, Download, TrashCan } from "@steeze-ui/carbon-icons";
    import { Icon } from "@steeze-ui/svelte-icon";
    import { createEventDispatcher } from "svelte";
    import {
        OverflowMenuHorizontal,
        MicrophoneFilled,
    } from "@steeze-ui/carbon-icons";

    import { downloadAudioFile } from "$lib/api/mednote";

    export let record: AudioRecord;
    export let selected: boolean;
    const dispatch = createEventDispatcher();

    let isMenuOpen = false;

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
    }
    function closeMenu() {
        isMenuOpen = false;
    }
    function downloadAudio() {
        downloadAudioFile(record.url);
    }
</script>

<tr
    class="bg-white border-b border-b-darkgrey hover:text-primary hover:cursor-pointer {selected
        ? 'text-primary '
        : ''}"
    on:mouseleave={closeMenu}
    on:click={() => dispatch("selected", { record_url: record.url })}
>
    <td class="ps-6 pe-12 py-4 font-medium">
        <div class="flex">
            <div class="w-5">
                <Icon src={MicrophoneFilled} />
            </div>
            <span class="w-full mx-2">
                {record.file_name}
            </span>
        </div>
    </td>
    <td class="px-6 py-4"> {record.duration} </td>
    <td class="px-6 py-4 text-sm"> {record.formatted_date} </td>
    <td class="px-6 py-4">
        <button class="w-5" on:click={toggleMenu}>
            <Icon src={OverflowMenuHorizontal} />
        </button>

        {#if isMenuOpen}
            <div class="relative">
                <div
                    class="absolute -left-20 -mt-2 -mr-50 bg-white border border-darkgrey divide-y divide-gray-100 rounded-md shadow-lg outline-none z-100"
                >
                    <div class="py-1">
                        <div class="flex mx-2 text-darkgrey hover:text-primary">
                            <div class="w-5">
                                <Icon src={Download} />
                            </div>
                            <button
                                class="block px-2 py-2 text-sm w-full text-left"
                                on:click={downloadAudio}
                            >
                                Download
                            </button>
                        </div>
                        <div
                            class="flex mx-2 w-full text-darkgrey hover:text-primary"
                        >
                            <div class="w-5">
                                <Icon src={TrashCan} />
                            </div>
                            <button
                                class="block px-2 py-2 text-sm w-full text-left"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </td>
</tr>
