// import axios from 'axios'
// import { isEmpty } from 'lodash-es'
// import { useSnapshot } from 'valtio'
// import { proxyWithComputed } from 'valtio/utils'


// function getAuthUser() {
//   const jwt = window.localStorage.getItem('jwtToken')

//   if (!jwt) return {}

//   try {
//     return JSON.parse(window.localStorage.getItem('authUser') || '{}')
//   } catch (e) {
//     return {}
//   }
// }

// const state = proxyWithComputed(
//   {
//     authUser: getAuthUser(),
//   },
//   {
//     isAuth: (snap) => !isEmpty(snap.authUser),
//   }
// )

// const actions = {
//   login: (user) => {
//     state.authUser = user
    
//     // 分别存储用户信息和 token
//     window.localStorage.setItem('authUser', JSON.stringify(user))
//     window.localStorage.setItem('jwtToken', user.token)

//     // 设置认证头
//     axios.defaults.headers.common['Authorization'] = `Bearer ${user.token}`
//   },
//   logout: () => {
//     state.authUser = {}

//     window.localStorage.removeItem('authUser')
//     window.localStorage.removeItem('jwtToken')
//     delete axios.defaults.headers.common['Authorization']
//   },
//   checkAuth: () => {
//     const authUser = getAuthUser()
//     const token = window.localStorage.getItem('jwtToken')

//     if (!authUser || isEmpty(authUser) || !token) {
//       actions.logout()
//     } else {
//       // 确保在页面刷新后也设置认证头
//       axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
//     }
//   },
// }

// function useAuth() {
//   const snap = useSnapshot(state)

//   return {
//     ...snap,
//     ...actions,
//   }
// }

// export default useAuth

import axios from 'axios';
import { isEmpty } from 'lodash-es';
import { useSnapshot } from 'valtio';
import { proxyWithComputed } from 'valtio/utils';

// 获取本地存储的用户信息
function getAuthUser() {
  const jwt = window.localStorage.getItem('jwtToken');

  if (!jwt) return {};

  try {
    return JSON.parse(window.localStorage.getItem('authUser') || '{}');
  } catch (e) {
    return {};
  }
}

const state = proxyWithComputed(
  {
    authUser: getAuthUser(),
  },
  {
    isAuth: (snap) => !isEmpty(snap.authUser), // 判断用户是否已认证
  }
);

const actions = {
  // 用户登录：将用户信息存储在本地并设置认证头
  login: (user) => {
    state.authUser = user;

    // 存储用户信息和 token 到本地存储
    window.localStorage.setItem('authUser', JSON.stringify(user));
    window.localStorage.setItem('jwtToken', user.token);

    // 设置认证头
    axios.defaults.headers.common['Authorization'] = `Bearer ${user.token}`;
  },

  // 用户退出登录：清除用户信息及 token
  logout: () => {
    state.authUser = {};

    window.localStorage.removeItem('authUser');
    window.localStorage.removeItem('jwtToken');
    delete axios.defaults.headers.common['Authorization']; // 清除认证头
  },

  // 检查用户认证状态：如果本地存储中没有用户信息或 token，则认为用户未登录
  checkAuth: () => {
    const authUser = getAuthUser();
    const token = window.localStorage.getItem('jwtToken');

    if (!authUser || isEmpty(authUser) || !token) {
      actions.logout(); // 如果没有认证信息，退出登录
    } else {
      // 确保在页面刷新后设置认证头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  },
};

// 提供对外接口
function useAuth() {
  const snap = useSnapshot(state);

  return {
    ...snap,
    ...actions,
  };
}

export default useAuth;