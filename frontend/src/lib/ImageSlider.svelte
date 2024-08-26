<script lang="ts">
    import { select } from "./stores/albumSliderSelection"
    const PLACEHOLDER_DELAY: number = 10 * 1000

    // All the images should have dimensions 300x300 px
    const HARDCODED_ALBUMS = [
        {
            "artist": "Daft Punk",
            "title": "Discovery",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e0248905438b9c1153978d9fbf4",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/2noRn2Aes5aoNVsU6iWThc?si=3ce15b3c26c34cdf",
        },
        {
            "artist": "Kendrick Lamar",
            "title": "good kid, m.A.A.d city",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e02d58e537cea05c2156792c53d",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/3DGQ1iZ9XKUQxAUWjfC34w?si=60e82aac04ed4fad",
        },
        {
            "artist": "Freddie Gibbs",
            "title": "Piñata",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e02d844f6b7311a69b9a08e7a0f",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/43uErencdmuTRFZPG3zXL1?si=76d825fec189404f",
        },
        {
            "artist": "MF Doom, Madlib",
            "title": "Madvillany",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e0274dc897ea75402db37ef239a",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/19bQiwEKhXUBJWY6oV3KZk?si=033c39316b9b4d6a",
        },
        {
            "artist": "JPEGMAFIA, Danny Brown",
            "title": "SCARING THE HOES",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e028cf4c85912fdeb106707fb4c",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/3u20OXh03DjCUzbf8XcGTq?si=1987e60a4ff841bc",
        },
        {
            "artist": "JPEGMAFIA",
            "title": "I LAY DOWN MY LIFE FOR YOU",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e02a3314be7ae643fefa32fbe08",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/1ezs1QD5SYQ6LtxpC9y5I2?si=8e434137c2bf460d",
        },
        {
            "artist": "J Dilla",
            "title": "Donuts",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e0283bb78285449998bb974da45",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "open.spotify.com/album/5fMlysqhFE0itGn4KezMBW?si=gttrki1HTsuYIi_5xT1Vqg",
        },
        {
            "artist": "Kendrick Lamar",
            "title": "To Pimp A Butterfly",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e02cdb645498cd3d8a2db4d05e1",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "https://open.spotify.com/album/7ycBtnsMtyVbbwTfJwRjSP?si=4iSSh4w8Q5u0VMFfTtjxxg",
        },
        {
            "artist": "De La Soul",
            "title": "3 Feet High and Rising",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e02fa8d314f6f91e81889335dfc",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "https://open.spotify.com/album/34LxHI9x14qXUOS8AWRrYD?si=6rbta2dzQs2h-WC13qLoLw",
        },
        {
            "artist": "Beastie Boys",
            "title": "Paul's Boutique",
            "coverImageUrl": "https://i.scdn.co/image/ab67616d00001e022288f4cd4bf3a8764624a0d2",
            "processingDuration": PLACEHOLDER_DELAY,
            "uri": "https://open.spotify.com/album/1kmyirVya5fRxdjsPFDM05?si=5JXw7MD2QuK06lAStmrrjQ",
        }
    ]
    
    const DEFAULT_SIZE = 150
    const EXPANDED_SIZE = 200
    let imageSizes = Array(HARDCODED_ALBUMS.length).fill(DEFAULT_SIZE)

    const expandSelf = (index: number) => {
        imageSizes[index] = EXPANDED_SIZE
        imageSizes = [...imageSizes]
    }

    const contractSelf = (index: number) => {
        imageSizes[index] = DEFAULT_SIZE
        imageSizes = [...imageSizes]
    }
</script>

<div id="sliding gallery container" class="flex flex-row overflow-auto h-60 items-center">
    {#each HARDCODED_ALBUMS as album, index}
        <div class="flex-shrink-0 w-48 flex items-center justify-center" >
            
            <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <img src={album["coverImageUrl"]} alt="Album art for {album["title"]} by {album["artist"]}" 
                title="{album["title"]} - {album["artist"]}"
                    class="rounded-md
                    h-40 w-40 hover:w-48 hover:h-48 ease-in-out duration-200"
                    on:mouseover={() => expandSelf(index)}
                    on:focus={() => expandSelf(index)}
                    on:mouseout={() => contractSelf(index)}
                    on:blur={() => contractSelf(index)}
                    
                    on:click={() => select(album["uri"])}
            />
        </div>
    {/each}
</div>