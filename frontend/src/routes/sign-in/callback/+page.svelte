<script lang="ts">
    import { page } from '$app/stores'
	import { onMount } from 'svelte';
    import { PUBLIC_BASE_URL, PUBLIC_SERVER_URL } from '$env/static/public'
    import { authorizationRequestLink } from '$lib/SpotifyAuthLink';

    let code: string | null = $page.url.searchParams.get("code")

    let fetchingToken: boolean = false
    let codeExchangeError: boolean = false

    onMount(async () => {
        try {
            if (code) {
                fetchingToken = true
                const res = await fetch(
                    `${PUBLIC_SERVER_URL}/token-from-code?code=${code}`,
                    {
                        credentials: 'include'
                    }
                )
                console.log(res)
                if (!res.ok) {
                    throw Error("Exchange failed")
                } else {
                    // Send back to skeleton homepage
                    window.location.href = PUBLIC_BASE_URL
                }
            }
        } catch (error) {
            codeExchangeError = true
        }
        
    })
</script>

{#if code && !codeExchangeError}
<p class="text-lagoBlue-200">
    got a code in the URL! exchanging it for a token
</p>
{:else}
<p class="text-heartwarming-300">
    {#if codeExchangeError}
        something went wrong. 
    {:else}
        couldn't find a Spotify auth code in the URL. 
    {/if}
    <a class="text-lagoBlue-200 underline underline-offset-4 decoration-irishJig-300"
        href={authorizationRequestLink}>try again
    </a>?
</p>
{/if}