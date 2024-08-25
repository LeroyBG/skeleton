import { redirect } from "@sveltejs/kit";

export function load({ cookies }) {
    console.log('cookies:', cookies)
    console.log('getAll', cookies.getAll())
    const hasToken = cookies.get('AIOHTTP_SESSION')
    console.log(hasToken)
    if (!hasToken) {
        redirect(302, '/sign-in')
    }
}