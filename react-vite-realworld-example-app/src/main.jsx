import React from 'react'
import ReactDOM from 'react-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { createServer } from 'miragejs'
import axios from 'axios'
import App from './App'
import makeServer from './server'

if (process.env.NODE_ENV === 'production')
axios.defaults.baseURL = 'http://localhost:8000/api'

//begin
// 添加默认请求头
axios.defaults.headers.common['Content-Type'] = 'application/json'
// 如果有 token，添加到请求头
const token = localStorage.getItem('jwtToken')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}
//end

const defaultQueryFn = async ({ queryKey }) => {
  try {
    const { data } = await axios.get(queryKey[0], { params: queryKey[1] })
    return data
  } catch (error) {
    if (error.response?.status === 401) {
      // 如果是未授权错误，返回空数据而不是抛出错误
      return {
        articles: [],
        articlesCount: 0
      }
    }
    throw error
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: defaultQueryFn,
      staleTime: 300000,
    },
  },
})

if (window.Cypress && process.env.NODE_ENV === 'test') {
  const cyServer = createServer({
    routes() {
      ;['get', 'put', 'patch', 'post', 'delete'].forEach((method) => {
        this[method]('/*', (schema, request) => window.handleFromCypress(request))
      })
    },
  })
  cyServer.logging = false
} else if(process.env.NODE_ENV === 'development') {
  makeServer({ environment: 'development' })
}

ReactDOM.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} containerElement="div" />
    </QueryClientProvider>
  </React.StrictMode>,
  document.getElementById('root')
)
