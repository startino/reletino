<!-- this is just to test the function is working or not -->
<script>
    /** @type {import('./$types').PageData} */
    export let data;
  </script>
  
  {#if data.result}
    <pre>{JSON.stringify(data.result, null, 2)}</pre>
  {/if}
