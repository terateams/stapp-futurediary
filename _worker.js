export default {
    async fetch(request, env) {
        // 创建一个函数来递归处理请求
        async function handleRequest(url) {
            let newRequest = new Request(url, request);
            let response = await fetch(newRequest);

            // 检查是否为重定向响应
            if (response.status >= 300 && response.status < 400 && response.headers.has("Location")) {
                // 获取重定向的URL
                let location = response.headers.get("Location");
                // 递归调用函数以跟随重定向
                return await handleRequest(new URL(location, url));
            }

            // 如果不是重定向，直接返回响应
            return response;
        }

        // 获取初始的URL
        let url = new URL(request.url);
        const newHost = 'https://futurediary.streamlit.app';
        let newUrl = newHost + url.pathname + url.search;

        // 开始处理请求
        return await handleRequest(newUrl);
    },
};
