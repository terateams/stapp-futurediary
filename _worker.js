export default {
    async fetch(request, env) {
        let url = new URL(request.url);
        const newHost = 'https://futurediary.streamlit.app';
        let newUrl = newHost + url.pathname + url.search;
        let new_request = new Request(newUrl, request);

        // 发送新请求并获取响应
        let response = await fetch(new_request);

        // 检查是否为重定向响应
        if (response.status >= 300 && response.status < 400) {
            // 可以选择修改响应或不处理重定向
            // 如下行可注释掉，使得重定向不被浏览器处理
            // return response;
            return new Response(response.body, {
                status: 200, // 或其他非重定向状态码
                headers: response.headers
            });
        }

        return response;
    },
};
