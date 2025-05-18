import { omit } from 'lodash-es'
import { useQuery } from 'react-query'

function useArticlesQuery({ filters }) {
  return useQuery([`/articles${filters.feed ? '/feed' : ''}`, { limit: 10, ...omit(filters, ['feed']) }], {
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
