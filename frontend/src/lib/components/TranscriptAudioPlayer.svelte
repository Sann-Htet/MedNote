<script lang="ts">
    import type { Transcription } from "$lib/types/mednote";

    import { audioUrlStore } from "$lib/stores/AudioUrlStore";
    import WaveSurfer from "wavesurfer.js";
    import { onMount } from "svelte";
    import { Icon } from "@steeze-ui/svelte-icon";
    import { PlayFilled, StopFilled } from "@steeze-ui/carbon-icons";
    import RegionsPlugin from "wavesurfer.js/plugins/regions";

    export let transcription: Transcription;

    let containerId = `waveform-${transcription.start.toString().replace(".", "_")}`;

    let isAudioPlaying = false;
    let wavesurfer: WaveSurfer | null = null;
    console.log("TranscriptAudioPlayer now");

    onMount(async () => {
        wavesurfer = WaveSurfer.create({
            container: "#" + containerId,
            waveColor: "#fff",
            progressColor: "#3089F0",
            height: 44,
            width: 400,
            cursorColor: "#000",
            minPxPerSec: 360,
        });
        async function displaySegment() {
            wavesurfer?.load(
                $audioUrlStore.aws_url +
                    "#t=" +
                    transcription.start +
                    "," +
                    transcription.end,
            );
               wavesurfer?.seekTo(transcription.start)
            // const duration = transcription.end - transcription.start;
            // wavesurfer?.zoom(duration);
            // console.log(duration)
            const wsRegions = wavesurfer?.registerPlugin(
                RegionsPlugin.create(),
            );
            wavesurfer?.on("decode", function () {
                wsRegions?.addRegion({
                    start: transcription.start,
                    end: transcription.end,
                    content:"Transcript",
                    color: 'hsla(100, 100%, 30%, 0.1)',
                    drag: false,
                    resize: false,
                });
            });
            // wavesurfer?.on("ready", function () {
                // wsRegions?.addRegion({
                //     start: transcription.start,
                //     end: transcription.end,
                //     color: "hsla(100, 100%, 30%, 0.1)",
                //     drag: false,
                //     resize: false,
                // });

                // Adjust the waveform container size to match the region
                // let zoomValue = wavesurfer?.options.minPxPerSec;
                // if (zoomValue == undefined) zoomValue = 1;
                // let regionWidth =
                //     (transcription.end - transcription.start) * zoomValue;

                // let containerElement = document.getElementById(containerId);

                // if (containerElement != null) {
                //     containerElement.style.width = regionWidth + "px";
                // }
            // });

            wavesurfer?.on("finish", function () {
                wavesurfer?.stop();
            });
        }
        await displaySegment();
    });

    async function playAudio() {
        if (isAudioPlaying) {
            wavesurfer?.pause();
            isAudioPlaying = false;
        } else {
            await wavesurfer?.play();
            isAudioPlaying = true;
        }
    }
</script>

<div class="flex justify-self-end w-56 pb-1">
    <div
        id={containerId}
        class="animate-wave h-11 w-full mx-2 bg-primary bg-opacity-10 text-primary rounded-lg overflow-hidden"
    ></div>

    <button type="button" class="h-11 text-primary" on:click={playAudio}>
        <Icon src={isAudioPlaying ? StopFilled : PlayFilled} />
    </button>
</div>
