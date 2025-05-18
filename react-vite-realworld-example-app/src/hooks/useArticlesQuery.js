import { omit } from 'lodash-es'
import { useQuery } from 'react-query'

function useArticlesQuery({ filters }) {
  //  4/15
  const isViewed = filters?.viewed === true

  const queryKey = isViewed
    ? [`/api/articles/viewed`]
    : [`/articles${filters.feed ? '/feed' : ''}`, { limit: 10, ...omit(filters, ['feed']) }]

  return useQuery(queryKey, {
    placeholderData: {
      articles: [],
      articlesCount: 0,
    },
    keepPreviousData: true,
    retry: false,
    onError: (error) => {
      console.error('Failed to fetch articles:', error)
    }
  })
}

export default useArticlesQuery
