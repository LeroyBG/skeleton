<script>
import EmbedSkeleton from './lib/EmbedSkeleton.svelte'
// Example credentials. In a SvelteKit project, these would be loaded from
// environment variables.
const SKELETON_SERVER_URL = "[your skeleton server url]"
const SKELETON_CLIENT_ID = "[Spotify developer project client id]"
const SKELETON_REDIRECT_URI = "[Spotify developer project redirect uri]"

</script>
    
<EmbedSkeleton 
    SERVER_URL={SKELETON_SERVER_URL}
    CLIENT_ID={SKELETON_CLIENT_ID}
    REDIRECT_URI={SKELETON_REDIRECT_URI} 
/>
