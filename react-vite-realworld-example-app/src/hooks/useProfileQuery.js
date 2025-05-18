// import { useQuery } from 'react-query'
// import { useParams } from 'react-router-dom'

// function useProfileQuery() {
//   const { username } = useParams()

//   return useQuery(`/profiles/${username}`, { placeholderData: { profile: {} } })
// }

// export default useProfileQuery

import { useQuery } from 'react-query'
import { useParams } from 'react-router-dom'
import { useAuth } from '../hooks'

function useProfileQuery() {
  const { authUser } = useAuth(); // 获取当前用户
  const token = authUser?.token;  // 假设 token 存储在 authUser 中

  return useQuery('profile', async () => {
    if (!token) {
      throw new Error('Authentication credentials were not provided.');
    }

    const response = await fetch(`http://localhost:8000/api/profiles/${authUser?.username}`, {
      headers: {
        'Authorization': `Bearer ${token}`, // 将 JWT token 添加到请求头
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }

    const data = await response.json();
    //begin
    console.log("Fetched profile data:", data);
    //end
    return data;  // 确保返回的数据结构是正确的
  }, {
    onError: (error) => {
      console.error('Error fetching profile:', error); // 打印错误
    }
  });
}

export default useProfileQuery