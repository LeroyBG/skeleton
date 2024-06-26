<script>
import EmbedSkeleton from './lib/EmbedSkeleton.svelte'
// Example credentials. In a SvelteKit project, these would be loaded from
// environment variables.
const PUBLIC_SKELETON_SERVER_URL = "[your skeleton server url]"
const PUBLIC_SKELETON_CLIENT_ID = "[Spotify developer project client id]"
const PUBLIC_SKELETON_REDIRECT_URI = "[Spotify developer project redirect uri]"

</script>
    
<EmbedSkeleton 
    SERVER_URL={PUBLIC_SKELETON_SERVER_URL}
    CLIENT_ID={PUBLIC_SKELETON_CLIENT_ID}
    REDIRECT_URI={PUBLIC_SKELETON_REDIRECT_URI} 
/>
