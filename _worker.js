
const hostname = "https://futurediary.streamlit.app"
function handleRequest(request) {
    let url = new URL(request.url);
    return fetch(new Request(hostname + url.pathname, request));
}

addEventListener("fetch", event => {
    event.respondWith(handleRequest(event.request));
})
