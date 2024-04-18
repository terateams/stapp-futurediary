export default {
    async fetch(request, env) {
        let url = new URL(request.url);
        url.hostname = 'https://futurediary.streamlit.app'
        let new_request = new Request(url, request);
        return env.ASSETS.fetch(new_request);
    },
};

