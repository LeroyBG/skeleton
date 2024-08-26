import { writable } from "svelte/store";

export let selection = writable<string>('')

export const select = (uri: string) => selection.set(uri)