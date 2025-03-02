<script lang="ts">
    import { Modal, getModalStore } from "@skeletonlabs/skeleton";

    const modalStore = getModalStore();
    let message: string = $modalStore[0].meta;

    function closeModal() {
        modalStore.close();
    }
</script>

<div
    class="w-80 h-72 flex flex-col justify-center items-center modal-transition bg-white shadow-md card rounded-lg space-y-4"
>
    <h2 class="justify-center text-2xl font-semibold items-center text-justify">Information</h2>
    <p class="text-justify p-8">
        {message}
    </p>

    <button
        class="bg-gray-400 rounded-md hover:cursor-pointer bg-primary p-1 text-white w-24"
        on:click={closeModal}
    >
        Okay</button
    >
</div>
