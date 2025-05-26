import axios from 'axios'

// 判断是否已登录
export const isAuthenticated = () => {
  return !!localStorage.getItem('accessToken')
}

// 获取当前用户信息
export const getCurrentUser = () => {
  const userJson = localStorage.getItem('user')
  return userJson ? JSON.parse(userJson) : null
}

// 判断用户是否是管理员
export const isAdmin = () => {
  const user = getCurrentUser()
  return user && user.is_admin
}

// 调试函数，检查认证状态
export const debugAuth = () => {
  const token = localStorage.getItem('accessToken')
  const tokenType = localStorage.getItem('tokenType')
  const userJson = localStorage.getItem('user')
  let user = null
  
  try {
    user = userJson ? JSON.parse(userJson) : null
  } catch (e) {
    console.error('Failed to parse user JSON:', e)
  }
  
  console.log('==== Auth Debug Info ====')
  console.log(`Token exists: ${!!token}`)
  console.log(`Token type: ${tokenType || 'not set'}`)
  console.log(`User data exists: ${!!userJson}`)
  console.log(`Is admin: ${user && user.is_admin}`)
  console.log(`Current path: ${window.location.pathname}`)
  console.log('========================')
  
  return { token, tokenType, user, isAuthenticated: !!token, isAdmin: user && user.is_admin }
}

// 添加认证请求拦截器
export const setupAxiosInterceptors = () => {
  // 更具体的URL模式匹配函数，同时处理有无尾部斜杠的情况
  const isProtectedUrl = (url) => {
    if (!url) return false;
    
    // 标准化URL，移除可能的尾部斜杠
    const normalizedUrl = url.endsWith('/') ? url.slice(0, -1) : url;
    
    return (
      normalizedUrl.includes('/api/auth') || 
      normalizedUrl.includes('/api/resources')
    );
  }

  axios.interceptors.request.use(
    config => {
      // 打印请求详情以便调试
      console.log(`请求URL: ${config.url}`, config);
      
      // 使用更健壮的URL匹配
      if (isProtectedUrl(config.url)) {
        const token = localStorage.getItem('accessToken')
        const tokenType = localStorage.getItem('tokenType') || 'Bearer'
        
        if (token) {
          config.headers['Authorization'] = `${tokenType} ${token}`
          console.log(`Added auth headers to: ${config.url}`)
        } else {
          console.log(`No token available for: ${config.url}`)
        }
      }
      return config
    },
    error => {
      console.error('请求拦截器错误:', error);
      return Promise.reject(error)
    }
  )
  
  // 响应拦截器处理401错误
  axios.interceptors.response.use(
    response => {
      console.log(`响应成功 - ${response.config.url}:`, response.status);
      return response;
    },
    error => {
      // 详细记录错误信息
      console.error('响应错误:', error);
      
      if (error.response) {
        console.error(`状态码: ${error.response.status}`);
        console.error(`响应头:`, error.response.headers);
        console.error(`响应数据:`, error.response.data);
      } else if (error.request) {
        console.error('没有收到响应', error.request);
      } else {
        console.error('错误信息:', error.message);
      }
      console.error('错误配置:', error.config);
      
      // 对于需要管理员权限的API，如果返回401，重定向到登录页
      if (error.response && error.response.status === 401) {
        const requestUrl = error.config.url || '';
        console.log(`401 Unauthorized for URL: ${requestUrl}`);
        
        // 使用相同的URL匹配逻辑
        if (isProtectedUrl(requestUrl)) {
          console.log('Authentication failed, redirecting to login page');
          
          // 清除登录信息
          localStorage.removeItem('accessToken')
          localStorage.removeItem('tokenType')
          localStorage.removeItem('user')
          
          // 如果不是登录页，则重定向到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
      }
      return Promise.reject(error)
    }
  )
  
  // 添加响应拦截器处理重定向，确保认证头在重定向中被保留
  axios.interceptors.response.use(
    response => {
      return response;
    },
    async error => {
      // 处理重定向 (307/302)
      if (error.response && (error.response.status === 307 || error.response.status === 302)) {
        const originalRequest = error.config;
        const redirectUrl = error.response.headers.location;
        
        if (redirectUrl && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true;
          
          // 保留原始请求的认证头
          if (originalRequest.headers && originalRequest.headers['Authorization']) {
            console.log(`Handling redirect to ${redirectUrl} with auth preserved`);
          }
          
          // 重新发送请求到新URL
          try {
            return await axios(originalRequest);
          } catch (redirectError) {
            return Promise.reject(redirectError);
          }
        }
      }
      return Promise.reject(error);
    }
  );
}

// 登出
export const logout = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('tokenType')
  localStorage.removeItem('user')
  window.location.href = '/'
} 