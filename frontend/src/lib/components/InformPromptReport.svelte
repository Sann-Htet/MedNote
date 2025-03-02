<script lang="ts">
    import { Modal, getModalStore } from "@skeletonlabs/skeleton";

    const modalStore = getModalStore();
    function closeModal() {
        modalStore.close();
    }
</script>

<div
    class="w-80 h-72 flex flex-col justify-center items-center modal-transition bg-white shadow-md card rounded-lg space-y-4"
>
    <h2 class="justify-center items-center text-justify">Report successfully submitted to S3!</h2>
    <p class="text-justify p-8">
        File has been successfully reported to the Amazon S3 storage service.
    </p>

    <button
        class="bg-gray-400 rounded-md hover:cursor-pointer"
        on:click={closeModal}
    >
        Okay</button
    >
</div>
