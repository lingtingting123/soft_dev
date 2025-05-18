import axios from 'axios'
import { isEmpty } from 'lodash-es'
import { useSnapshot } from 'valtio'
import { proxyWithComputed } from 'valtio/utils'

function getAuthUser() {
  const jwt = window.localStorage.getItem('jwtToken')

  if (!jwt) return {}

  try {
    return JSON.parse(window.localStorage.getItem('authUser') || '{}')
  } catch (e) {
    return {}
  }
}

const state = proxyWithComputed(
  {
    authUser: getAuthUser(),
  },
  {
    isAuth: (snap) => !isEmpty(snap.authUser),
  }
)

const actions = {
  login: (user) => {
    state.authUser = user
    
    // 分别存储用户信息和 token
    window.localStorage.setItem('authUser', JSON.stringify(user))
    window.localStorage.setItem('jwtToken', user.token)

    // 设置认证头
    axios.defaults.headers.common['Authorization'] = `Bearer ${user.token}`
  },
  logout: () => {
    state.authUser = {}

    window.localStorage.removeItem('authUser')
    window.localStorage.removeItem('jwtToken')
    delete axios.defaults.headers.common['Authorization']
  },
  checkAuth: () => {
    const authUser = getAuthUser()
    const token = window.localStorage.getItem('jwtToken')

    if (!authUser || isEmpty(authUser) || !token) {
      actions.logout()
    } else {
      // 确保在页面刷新后也设置认证头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  },
}

function useAuth() {
  const snap = useSnapshot(state)

  return {
    ...snap,
    ...actions,
  }
}

export default useAuth
