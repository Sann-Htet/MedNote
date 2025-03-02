<script lang="ts">
    import { Icon } from "@steeze-ui/svelte-icon";
    import { Calendar } from "@steeze-ui/carbon-icons";
    let currentDate = new Date().toDateString();

</script>

<div class="absolute inset-x-0 z-0  text-primary justify-center items-center hidden lg:flex " >
    <div class="w-5 text-primary me-2">
        <Icon src={Calendar} />
    </div>
    <span>    {currentDate}
    </span>
</div>
