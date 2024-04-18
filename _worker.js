export default {
    async fetch(request, env) {
        let url = new URL(request.url);
        const newHost = 'https://futurediary.streamlit.app';
        // 确保包括完整的路径和查询字符串
        let newUrl = newHost + url.pathname + url.search;
        let new_request = new Request(newUrl, request);
        return fetch(new_request); // 如果目标是转发请求，应使用 fetch 而非 env.ASSETS.fetch
    },
};
