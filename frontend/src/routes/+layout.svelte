<script lang="ts">
    import "../app.pcss";
    import type { ModalComponent } from "@skeletonlabs/skeleton";
    import { Modal, initializeStores } from "@skeletonlabs/skeleton";
    import { browser } from "$app/environment";
    import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";
    import ExistAudioForm from "$lib/components/ExistAudioForm.svelte";
    import InformPrompt from "$lib/components/InformPrompt.svelte";
    import InformPromptSubmit from "$lib/components/InformPromptSubmit.svelte";

    initializeStores();

    const modalRegistry: Record<string, ModalComponent> = {
        ExistAudioFormComponent: { ref: ExistAudioForm },
        InformPrompt: { ref: InformPrompt },
        InformPromptSubmit: { ref: InformPromptSubmit },
    };
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                enabled: browser,
                retry: false,
            },
        },
    });
</script>

<QueryClientProvider client={queryClient}>
    <div class="h-screen">
        <Modal
            class="modal-backdrop fixed top-0 left-0 right-0 bottom-0 bg-surface-backdrop-token p-4 z-[999] h-screen backdrop-filter backdrop-blur-sm overflow-y-hidden"
            components={modalRegistry}
        ></Modal>
        <slot />
    </div>
</QueryClientProvider>
