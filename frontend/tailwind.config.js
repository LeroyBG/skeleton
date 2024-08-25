/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				theme: {
					light: "#f2f2e6",
					dark: "#2c002c"
				},
				puissantPurple: {
					50: "#f1cbed",
					100: "#efb1ee",
					200: "#db7fea",
					300: "#bc52e1",
					400: "#962ed4",
					500: "#7116c1",
					600: "#510aa6",
					700: "#390685",
					800: "#26065f",
					900: "#160535",
				},
				heartwarming: {
					50: "#f1d9cb",
					100: "#efc6b1",
					200: "#ea9c7f",
					300: "#e16e52",
					400: "#d4412e",
					500: "#c11c16",
					600: "#a60a12",
					700: "#850618",
					800: "#5f061a",
					900: "#350515",
				},
				irishJig: {
					50: "#d8f1cb",
					100: "#c5efb1",
					200: "#a2ea7f",
					300: "#84e152",
					400: "#70d42e",
					500: "#66c116",
					600: "#62a60a",
					700: "#5d8506",
					800: "#4f5f06",
					900: "#353505",
				},
				lagoBlue: {
					50: "#cbd3f1",
					100: "#b1c5ef",
					200: "#7fb8ea",
					300: "#52b9e1",
					400: "#2ebed4",
					500: "#16bbc1",
					600: "#0aa6a1",
					700: "#06857e",
					800: "#065f5b",
					900: "#053535",
				},
			},
		},
	},
	plugins: [],
}