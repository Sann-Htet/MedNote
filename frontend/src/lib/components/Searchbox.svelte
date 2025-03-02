<script>
    import { Icon } from '@steeze-ui/svelte-icon';
      import { Search } from '@steeze-ui/carbon-icons';
</script>
<form action="" class=" w-full">
    <div class="relative ">
      <input type="text" class="input block h-6 lg:h-9 shadow-sm xl:w-80 md:w-full w-full ps-8 border border-darkgrey rounded-md text-sm" placeholder="Search in transcript " required />
      <div class="absolute inset-y-0 start-0 flex items-center pointer-events-none">
        <div class="w-4 mx-2">
          <Icon src={Search} />
        </div>
      </div>
    </div>
</form>
