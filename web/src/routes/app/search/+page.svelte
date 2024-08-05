<!-- This is just to test the function is working or not -->
<script>
  /** @type {import('./$types').PageData} */
  export let data;
</script>

<style>
  .post-container {
      max-width: 600px;
      margin: 20px auto;
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      background-color: #f9f9f9;
  }

  .post-title {
      font-size: 1.5em;
      color: #333;
      margin-bottom: 10px;
  }

  .post-author {
      font-size: 0.9em;
      color: #555;
      margin-bottom: 10px;
  }

  .post-selftext {
      font-size: 1em;
      color: #444;
      line-height: 1.5;
  }

  .post {
      margin-bottom: 20px;
  }
</style>

{#if data.fetch}
  <div class="post-container">
      {#each data.fetch as posts}
          <div class="post">
              <h2 class="post-title">{posts.post.title}</h2>
              <h2 class="post-title">Subreddit: {posts.post.subreddit}</h2>
              <p class="post-author">Posted by: {posts.post.author}</p>
              <p class="post-selftext">Post: {posts.post.selftext}</p>
              <p class="post-selftext">Is relevant: {posts.isRelevant}</p>
              <p class="post-selftext">Why: {posts.reason}</p>
              <p class="post-selftext">Aligment score: {posts.alignmentScore}</p>
                        </div>
      {/each}
  </div>
{/if}