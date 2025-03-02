<script lang="ts">
    import { Modal, getModalStore } from "@skeletonlabs/skeleton";

    const modalStore = getModalStore();
    let data: { url: string; message: string } = $modalStore[0].meta;

    function closeModal() {
        modalStore.close();
    }
</script>

<div
    class="w-110 h-72 flex flex-col justify-center items-center modal-transition bg-white shadow-md card rounded-lg space-y-4"
>
    <h2 class="justify-center text-lg font-semibold items-center text-justify">{data.message}</h2>
    <p class="text-justify p-6">
        File has been successfully uploaded to the Amazon S3 storage service.
    </p>
    <span class=" text-center mb-2">{data.url}</span>

    <button
        class="bg-gray-400 rounded-md hover:cursor-pointer bg-primary p-1 text-white w-24"
        on:click={closeModal}
    >
        Okay</button
    >
</div>
