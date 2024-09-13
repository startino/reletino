<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable"
  import DataTable from "$lib/components/ui/data-table/data-table.svelte"
  import { LeadViewer } from "$lib/components/ui/lead-viewer"
  import type { Lead } from "$lib/types"

  export let data: { leads: Lead[] }
  let { leads } = data

  let activeLead: Lead = leads[0]

  async function markAsDone(id: string) {
    leads = leads.map((row) => {
      if (row.id === id) {
        row.done = true
      }
      return row
    })

    const res = await fetch(`?/markAsDone`, {
      method: "POST",
      body: JSON.stringify({ id }),
    })
    const { success } = await res.json()
  }
</script>

<Resizable.PaneGroup direction="horizontal" class="rounded-lg border">
  <Resizable.Pane defaultSize={50}>
    <div class="flex items-center justify-center p-6">
      {#key leads}
        <DataTable bind:activeLead data={leads} {markAsDone} />
      {/key}
    </div>
  </Resizable.Pane>
  <Resizable.Handle withHandle />
  <Resizable.Pane defaultSize={50}>
    <LeadViewer bind:lead={activeLead} />
  </Resizable.Pane>
</Resizable.PaneGroup>
