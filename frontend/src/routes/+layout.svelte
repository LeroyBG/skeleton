<script>
    import "../app.css";
    import { PUBLIC_PROJECT_GITHUB_LINK } from "$env/static/public";
</script>

<header class="h-14 flex justify-center items-center text-puissantPurple-100 text-base">
    <p>to use this app with any album, song, or playlist, <a class="text-irishJig-300 underline"
        href={PUBLIC_PROJECT_GITHUB_LINK}>run it locally</a> :)</p>
</header>
<div class="flex flex-col items-center gap-32">
    <div id="top-title-container" class="flex w-full justify-center items-center text-7xl mt-5 text-irishJig-300">
        <h1 id="title" class="text-center">skeleton</h1>
    </div>
    <slot />
</div>