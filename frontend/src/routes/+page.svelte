<script lang="ts">

    import { PUBLIC_SERVER_URL } from "$env/static/public";
	import ImageSlider from "$lib/ImageSlider.svelte";
    import { onMount } from "svelte";
    import { select, selection } from "$lib/stores/albumSliderSelection"





    const URIorURLPattern = /\/(?<resourceType>(track)|(album)|(playlist))(:|\/)(?<id>\w+)?/ig

    let resourceTypeChoices: string[] = ["playlist", "album", "track"]
    let resourceTypeIndexChoice: number = 0
    let resourceTypeIntervalId: number | null = null
    
    onMount(()=>{
        // Rotate Spotify resource type
        // @ts-ignore
        resourceTypeIntervalId = setInterval(()=> {
            resourceTypeIndexChoice = (resourceTypeIndexChoice + 1) % resourceTypeChoices.length
        }, 5000)

        return () => resourceTypeIntervalId ? clearInterval(resourceTypeIntervalId) : null
    })

    let resourceURIInputDisabled = false
    let resourceURIInputVisible = true
    let GOButtonEnabled: boolean = false
    let inputResourceType: 'track' | 'album' | 'playlist' | null = null
    let inputId: string | null = null
    
    let extractingLink: boolean = false
    let originalURIInput: string | null = null
    let handlingSubmission: boolean = false
    let typeLiteralText: string = ''
    let typeText: string = ''
    let idLiteralText: string = ''
    let idText: string = ''

    const delay = (ms: number) => new Promise((res) => setTimeout((res), ms))

    const randDelay = async (ms: number, varianceRatio: number) => {
        const maxOffset = (ms * varianceRatio)
        await delay(ms - maxOffset + Math.floor(Math.random() * 2 * maxOffset))
    }

    const typingDelay = async () => await randDelay(100, .3)
    const shortTypingDelay = async () => await randDelay(30, .3)
    const deletingDelay = async () => await delay(55)

    let activeResponseAnimation: boolean = false // Whether we got a response from Skeleton server
    let loadingText = ''

    type samplesReport = {
        name: string;
        song_samples_report: {
            track_name: string;
            artist: string;
            uri: string | null
        }[];
    }[]

    let newPlaylistNameAnimationText: string | null = null
    let reportAnimationDataStructure: {
        og_track_name: string
        samples: Array<{
            text: string,
            uri: string | null
        }>
    }[]

    let emptySamplesReport: boolean = false
    let emptySamplesReportAnimationText: string | null = null

    const loadingTextOptions = [
        "doing some crate digging",
        "talking to some music nerds",
        "practicing active listening",
        "adding some of these to my playlist",
        "trusting user5340345's sample-recognition skills",
        "consulting the gods of musical wisdom"
    ]


    const handleGOButtonPRess = async () => {
        console.log("Go button pressed")
        handlingSubmission = true
        resourceURIInputDisabled = true
        GOButtonEnabled = false
        const originalResourceURIInput = $selection

        // reset state if we're getting another one
        activeResponseAnimation = false
        emptySamplesReportAnimationText = null
        emptySamplesReport = false

        // Async function that should execute until gotResponse != false 
        // WILL MUTATE resourceURIInput!!!!(!!!!) use originalPlaylistURIInput!
        await playLinkExtractionAnimation()
        playLoadingTextAnimations()

        let playlistURI: string | null = null
        let samplesReport: samplesReport | null = null
        let originalResourceName: string | null = null
        let newPlaylistName: string | null = null
        const get_url = `/?uri=${originalResourceURIInput}`
        console.log("sending a request to", get_url)
        try {
            const res = await fetch(get_url, {
                credentials: 'include'
            })
            if (!res.ok) {
                throw new Error(res.statusText)
            }
            const data = await res.json()
            playlistURI = data["playlist_uri"]
            samplesReport  = data["samples_report"]
            originalResourceName = data["original_resource_name"]
            newPlaylistName =  data["playlist_name"]
            activeResponseAnimation = false // Should halt playLoadingTextAnimations

        } catch (err) {
            // ugugusdogisdogosdmf
            console.log(err)
        }

        activeResponseAnimation = true
        await playSampleReportTextAnimations(playlistURI, samplesReport || [], newPlaylistName || originalResourceName!)
        handlingSubmission = false
        resourceURIInputDisabled = false
        select("")
        resourceURIInputVisible = true

        inputResourceType  = null
        inputId = null
        
        typeLiteralText = ''
        typeText  = ''
        idLiteralText  = ''
        idText = ''
    }

    const playLinkExtractionAnimation = async () => {
                /*
        <h3>new playlist name</h3>
        <ul>
            <li>
                <ul>song 1 name
                    <li>song 1 sample 1 name</li> <!-- could be a link if sample was found -->
                    <li>song 1 sample 2 name</li>
                </ul>
            </li>
            <li>
                <ul>song 2 name
                    <!-- no samples for this song ? -->
                </ul>
            </li>
        </ul>
        */

        /* - - - - - strip away html - - - - - 
        new playlist name
        song 1 name
            song 1 sample 1 name
            song 1 sample 2 name
        song 2 name
        */

        extractingLink = true
        // assume we have valid input in the resource input thingy
        // inputResourceType won't be null due to regex
        if (!inputResourceType || !inputId) {
            console.error("Didn't get resource type from uri despite successful regex")
            return // should reset state or something
        }
        
        clearInterval(resourceTypeIntervalId!)
        resourceTypeIndexChoice = resourceTypeChoices.indexOf(inputResourceType)

        while ($selection.length != 1) {
            select($selection.slice(0,  $selection.length - 1))
            await randDelay(20, .34)
        }

        resourceURIInputVisible = false


        await delay(30)
        select(' ')
        await delay(20)
        let currEl: 'type literal' | 'type' | 'id literal' | 'id' | 'done' = 'type literal'
        while (currEl !== 'done') {
            // console.log(typeLiteralText + typeText + idLiteralText + idText)
            switch(currEl){
                case 'type literal':
                    typeLiteralText += 'type: '[typeLiteralText.length]
                    if (typeLiteralText.length == 'type: '.length)
                        currEl = 'type'
                    break
                // @ts-ignore
                case 'type':
                    typeText += inputResourceType[typeText.length]
                    if (typeText.length == inputResourceType.length)
                        currEl = 'id literal'
                    break
                // @ts-ignore
                case 'id literal':
                    idLiteralText += ' id: '[idLiteralText.length]
                    if (idLiteralText.length == ' id: '.length)
                        currEl = 'id'
                    break
                // @ts-ignore
                case 'id':
                    idText += inputId[idText.length]
                    if (idText.length == inputId.length)
                        currEl = 'done'
                    break
            }
            await delay(75)
        }
        extractingLink = false
    }

    const playLoadingTextAnimations = async () => {
        let currLoadingTextChoice: number = -1
        let previousTextChoices: Set<number> = new Set([-1])
        // TODO: Error handling
        while (!activeResponseAnimation) {
            if (previousTextChoices.size == loadingTextOptions.length)
                previousTextChoices = new Set()
            // Get a new loading text that hasn't been seen
            while (previousTextChoices.has(currLoadingTextChoice = 
                    Math.floor(Math.random() * loadingTextOptions.length))){}
            previousTextChoices.add(currLoadingTextChoice)

            let typeUpCycleDone = false
            while (!typeUpCycleDone) {
                if (loadingText.length == loadingTextOptions[currLoadingTextChoice].length)
                    typeUpCycleDone = true
                else {
                    loadingText = loadingText + 
                        loadingTextOptions[currLoadingTextChoice][loadingText.length]
                }
                await typingDelay()
            }
            await delay(1000)
            let deleteCycleDone = false
            while (!deleteCycleDone) {
                if (loadingText.length == 0)
                    deleteCycleDone = true
                else {
                    loadingText = loadingText.slice(0, loadingText.length - 1)
                }
                await deletingDelay()
            }
        }
    }
        
    const playSampleReportTextAnimations = async (
        playlistURI: string | null, 
        samplesReport: samplesReport, 
        newPlaylistName: string
    ) => {
        console.log("Animation time!")
        console.log("samplesReport", samplesReport)
        console.log("newPlaylistName", newPlaylistName)
        newPlaylistNameAnimationText = ''
        reportAnimationDataStructure = []
        console.log("Animating playlist name")
        while (newPlaylistNameAnimationText.length < newPlaylistName.length) {
            newPlaylistNameAnimationText += newPlaylistName[newPlaylistNameAnimationText.length]
            await typingDelay()
            // console.log(newPlaylistNameAnimationText)
        }
        console.log(samplesReport)
        if (samplesReport.length == 0) {
            console.log("No samples. Animating thingy")
            const bodyAnimationText = 
                `couldn't find any samples for this ${resourceTypeChoices[resourceTypeIndexChoice]} :(`
            emptySamplesReportAnimationText = ''
            let curr_len: number
            emptySamplesReport = true
            while ((curr_len = emptySamplesReportAnimationText.length) < bodyAnimationText.length) {
                emptySamplesReportAnimationText += bodyAnimationText[curr_len]
                await shortTypingDelay()
                // console.log(emptySamplesReportAnimationText)
            }
            return
        }
        emptySamplesReport = false
        console.log("Animating samples report")
        let og_song_index = 0
        while (reportAnimationDataStructure.length < samplesReport.length) {
            const referenceSong = samplesReport[og_song_index]
            const newEntry = {
                og_track_name: '',
                samples: []
            }
            console.log("is this never?", newEntry)
            console.log(reportAnimationDataStructure)
            reportAnimationDataStructure = [...reportAnimationDataStructure, newEntry]
            console.log(reportAnimationDataStructure)
            while (newEntry.og_track_name.length < referenceSong.name.length) {
                const newChar = referenceSong.name[newEntry.og_track_name.length]
                newEntry.og_track_name += newChar
                // Propagate state update to reassign data structure
                reportAnimationDataStructure = [...reportAnimationDataStructure]
                await shortTypingDelay()
                // console.log(reportAnimationDataStructure)
            }
            let sample_index = 0
            while (newEntry.samples.length < referenceSong.song_samples_report.length) {
                const newSample = {
                    text: "",
                    uri: referenceSong.song_samples_report[sample_index].uri
                }
                const referenceSampleText = referenceSong.song_samples_report[sample_index].track_name
                    + ' - ' + referenceSong.song_samples_report[sample_index].artist
                newEntry.samples = [...newEntry.samples, newSample]
                while (newSample.text.length < referenceSampleText.length) {
                    newSample.text += referenceSampleText[newSample.text.length]
                    reportAnimationDataStructure = [...reportAnimationDataStructure]
                    await shortTypingDelay()
                    // console.log(reportAnimationDataStructure)
                }
                sample_index++
            }
            og_song_index++
        }

    }

    $: if (!extractingLink) {
        const match = URIorURLPattern.exec($selection) // reactive value!
        console.log("Input triggered!", $selection, URIorURLPattern, URIorURLPattern.exec($selection))
        GOButtonEnabled = !!match
        //@ts-ignore -- regex ensures type will match, i think
        inputResourceType = match?.groups?.resourceType || null
        inputId = match?.groups?.id || null
    }

    console.log("Button enabled: ", GOButtonEnabled)
</script>


<div id="skeleton-container" class="w-3/4 text-puissantPurple-100">
    <h3
        style="caret-shape: underscore;"
        class="text-4xl text-center font-medium text-theme-darkLight w-full caret-lagoBlue-400">
        enter spotify 
        <code class="text-heartwarming-300">{resourceTypeChoices[resourceTypeIndexChoice]}</code> 
        link
    </h3>
    <ImageSlider />
    {#if resourceURIInputVisible} <!-- just display an input thing -->
        <form class="flex flex-col items-center">
            <input type="text" class="my-10 h-20 font-light bg-transparent border-none w-full text-4xl text-irishJig-300 font-mono
                focus:outline-none"
                bind:value={$selection}
                disabled
                placeholder="open.spotify.com/{resourceTypeChoices[resourceTypeIndexChoice]}/...">
            <button
                disabled={!GOButtonEnabled}
                on:click|preventDefault={handleGOButtonPRess}
                type="submit"
                class="bg-puissantPurple-600 text-lagoBlue-300 text-2xl px-4 py-1
                hover:bg-puissantPurple-700
                disabled:opacity-30 disabled:bg-puissantPurple-600 disabled:text-theme-dark"
            >GO</button>
        </form>
    {:else}
        <div class="mt-10">
            <div id="processing-input-holder" class="flex flex-row items-center justify-center">
                <p class="text-left font-light w-3/5s text-2xl text-lagoBlue-200 font-mono truncate my-10 p-0 h-20">
                    {typeLiteralText}
                    <span 
                        class='text-heartwarming-300'>
                        {typeText}
                    </span>
                    {idLiteralText}
                    <span class="text-irishJig-300">
                        {idText}
                    </span>
                </p>
            </div>   
            {#if !activeResponseAnimation}
                <code>
                    <p class="my-10 text-irishJig-300 block text-2xl mb-10 text-center"
                    >{loadingText}</p>
                </code>
            {/if}
        </div>
    {/if}            
    {#if activeResponseAnimation}
        <div id="samples-report-container" class="text-left mt-5">
            <h3 class="text-3xl text-heartwarming-300 text-center">
                {newPlaylistNameAnimationText}
            </h3>
            {#if !emptySamplesReport}
                {#each reportAnimationDataStructure as animationText}
                    <ul>
                        <span id="original-track-name" class="text-2xl text-purple-400">
                            {animationText.og_track_name}
                        </span>
                        {#each animationText.samples as sample}
                            <li class="ml-8 my-2 text-xl text-purple-300">
                                {#if sample.uri}
                                    <a href={sample.uri}
                                        class="underline decoration-lagoBlue-200 visited:decoration-lagoBlue-50">
                                        {sample.text}
                                    </a>
                                {:else}
                                    {sample.text}
                                {/if}
                            </li>
                        {/each}
                    </ul>
                {/each}
            {:else}
                <code>
                    <p class="text-center my-10 text-purple-400"
                    >
                        {emptySamplesReportAnimationText}
                    </p>
                </code>
            {/if}
        </div>
    {/if}
</div>