// Defines routes for getting samples so those big JSON files can be loaded
// on-demand

// This thing is horrible

import DiscoveryDaftPunk from '$lib/hard-coded_sample_reports/Disovery-Daft_Punk.json'
import goodkidmAAdcityKendrickLamar from '$lib/hard-coded_sample_reports/good_kid_mAAd_city-Kendrick_Lamar.json'
import PinataFreddieGibbs from '$lib/hard-coded_sample_reports/Pinata-Freddie_Gibbs.json'
import MadvillanyMFDoom from '$lib/hard-coded_sample_reports/Madvillany-MF_Doom.json'
import SCARINGTHEHOES_JPEGMAFIA from '$lib/hard-coded_sample_reports/SCARING_THE_HOES-JPEGMAFIA_DANNY_BROWN.json'
import ILAYDOWNMYLIFEFORYOU_JPEGMAFIA from '$lib/hard-coded_sample_reports/I_LAY_DOWN_MY_LIFE_FOR_YOU-JPEGMAFIA.json'
import DonutsJDilla from '$lib/hard-coded_sample_reports/Donuts-J_Dilla.json'
import ToPimpAButterflyKendrickLamar from '$lib/hard-coded_sample_reports/To_Pimp_a_Butterfly-Kendrick_Lamar.json'
import ThreeFeetHighAndRisingDeLaSoul from '$lib/hard-coded_sample_reports/3_Feet_High_and_Rising-De_La_Soul.json'
import PaulsBoutiqueBeastieBoys from '$lib/hard-coded_sample_reports/Pauls_Boutique-Beastie_Boys.json'

export function GET({ url }) {
    console.log('got a request', url.searchParams.get('uri'))
    switch(url.searchParams.get('uri')) {
        case 'open.spotify.com/album/2noRn2Aes5aoNVsU6iWThc?si=3ce15b3c26c34cdf':
            return new Response(JSON.stringify(DiscoveryDaftPunk))
        case 'open.spotify.com/album/3DGQ1iZ9XKUQxAUWjfC34w?si=60e82aac04ed4fad':
            return new Response(JSON.stringify(goodkidmAAdcityKendrickLamar))
        case 'open.spotify.com/album/43uErencdmuTRFZPG3zXL1?si=76d825fec189404f':
            return new Response(JSON.stringify(PinataFreddieGibbs))
        case 'open.spotify.com/album/19bQiwEKhXUBJWY6oV3KZk?si=033c39316b9b4d6a':
            console.log('let me give you Madvillany')
            return new Response(JSON.stringify(MadvillanyMFDoom))
        case 'open.spotify.com/album/3u20OXh03DjCUzbf8XcGTq?si=1987e60a4ff841bc':
            return new Response(JSON.stringify(SCARINGTHEHOES_JPEGMAFIA))
        case 'open.spotify.com/album/1ezs1QD5SYQ6LtxpC9y5I2?si=8e434137c2bf460d':
            return new Response(JSON.stringify(ILAYDOWNMYLIFEFORYOU_JPEGMAFIA))
        case 'open.spotify.com/album/5fMlysqhFE0itGn4KezMBW?si=gttrki1HTsuYIi_5xT1Vqg':
            return new Response(JSON.stringify(DonutsJDilla))
        case 'https://open.spotify.com/album/7ycBtnsMtyVbbwTfJwRjSP?si=4iSSh4w8Q5u0VMFfTtjxxg':
            return new Response(JSON.stringify(ToPimpAButterflyKendrickLamar))
        case 'https://open.spotify.com/album/34LxHI9x14qXUOS8AWRrYD?si=6rbta2dzQs2h-WC13qLoLw':
            return new Response(JSON.stringify(ThreeFeetHighAndRisingDeLaSoul))
        case 'https://open.spotify.com/album/1kmyirVya5fRxdjsPFDM05?si=5JXw7MD2QuK06lAStmrrjQ':
            return new Response(JSON.stringify(PaulsBoutiqueBeastieBoys))
    }
}