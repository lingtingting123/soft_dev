import React from 'react'
import { isEmpty, isNil } from 'lodash-es'
import useDeepCompareEffect from 'use-deep-compare-effect'
import { useArticlesQuery } from '../hooks'
import ArticlePreview from './ArticlePreview'

/**
 * @typedef {object} Filters
 * @property {string} [Filter.author]
 * @property {string} [Filter.favorited]
 * @property {string} [Filter.tag]
 * @property {number} [Filter.offset]
 * @property {string} [Filter.title]
 * @property {boolean} [Filter.feed]
 * @property {boolean} [Filter.viewed]  // 4/14
 */

/** @type {Filters} */
const initialFilters = { author: null, favorited: null, tag: null, offset: null, feed: false, viewed: false }  //  4/14
const limit = 10

function ArticleList({ filters = initialFilters }) {
  const [offset, setOffset] = React.useState(0)
  const { data, isFetching, isError, isSuccess } = useArticlesQuery({ filters: { ...filters, offset } })
  const pages = Math.ceil(data.articlesCount / limit)

  useDeepCompareEffect(() => {
    if (!isNil(filters.offset)) {
      setOffset(filters.offset)
    }
  }, [filters])

  if (isFetching) return <p className="article-preview">Loading articles...</p>
  if (isError) return <p className="article-preview">Loading articles failed :(</p>
  if (isSuccess && isEmpty(data?.articles)) return <p className="article-preview">No articles are here... yet.</p>

  // 过滤出 scheduledAt 为空或为 None 的文章
  // const filteredArticles = data?.articles?.filter(article => isNil(article.scheduledAt)) || []

  // 添加对标题过滤的处理
  const filteredArticles =
  (data?.articles?.filter(article => {
    const matchTitle = filters.title
      ? article.title.toLowerCase().includes(filters.title.toLowerCase())
      : true
    return isNil(article.scheduledAt) && matchTitle
  })) || []


  return (
    <>
      {filteredArticles.map((article) => (
        <ArticlePreview key={article.slug} article={article} />
      ))}
      {pages > 1 && (
        <nav>
          <ul className="pagination">
            {Array.from({ length: pages }, (_, i) => (
              <li className={offset === i ? 'page-item active' : 'page-item'} key={i}>
                <button type="button" className="page-link" onClick={() => setOffset(i)}>
                  {i + 1}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </>
  )
}

export default ArticleList
