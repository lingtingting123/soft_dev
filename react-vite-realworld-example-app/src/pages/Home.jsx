import classNames from 'classnames'
import React from 'react'
import { ArticleList, PopularTags } from '../components'
import { useAuth } from '../hooks'

const initialFilters = { tag: '', offset: null, title: '', feed: false }

function Home() {
  const { isAuth } = useAuth()
  const [filters, setFilters] = React.useState({ ...initialFilters, feed: isAuth })

  React.useEffect(() => {
    setFilters({ ...initialFilters, feed: isAuth })
  }, [isAuth])

  function onTagClick(tag) {
    setActiveTitle('')
    setFilters({ ...initialFilters, tag })
  }

  function onGlobalFeedClick() {
    setActiveTitle('')
    setFilters(initialFilters)
  }

  function onFeedClick() {
    setActiveTitle('')
    setFilters({ ...initialFilters, feed: true })
  }

  const [search, setSearch] = React.useState('')  // 5/18
  const [activeTitle, setActiveTitle] = React.useState('')

  return (
    <div className="home-page">
      <div className="banner">
        <div className="container">
          <h1 className="logo-font">Personal Blog</h1> {/*修改标题名称*/}
          <p>A place to share your knowledge.</p>
        </div>
      </div>
      <div className="container page">
        <div className="row">
          <div className="col-md-9">
            <div className="feed-toggle">
              <ul className="nav nav-pills outline-active">
                {isAuth && (
                  <li className="nav-item">
                    <button
                      onClick={onFeedClick}
                      type="button"
                      className={classNames('nav-link', {
                        active: filters.feed && !filters.title,
                      })}
                    >
                      Your Feed
                    </button>
                  </li>
                )}
                <li className="nav-item">
                  <button
                    type="button"
                    className={classNames('nav-link', {
                      active: !filters?.tag && !filters.feed && !filters.title,
                    })}
                    onClick={onGlobalFeedClick}
                  >
                    Global Feed
                  </button>
                </li>
                {filters?.tag && (
                  <li className="nav-item">
                    <a className="nav-link active"># {filters?.tag}</a>
                  </li>
                )}
                {activeTitle && (
                  <li className="nav-item">
                  <a className="nav-link active"># {activeTitle}</a>
                  </li>
                )}
              </ul>
            </div>
            <ArticleList filters={filters} />
          </div>
          <div className="col-md-3">
            <PopularTags onTagClick={onTagClick} />
            <div style={{ marginTop: '10px' }}>
              <input
                type="text"
                placeholder="Search by title..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    setFilters({ ...initialFilters, title: search, feed: false })
                    setActiveTitle(search)
                  }
                }}
                className="form-control"
                style={{ maxWidth: '300px', display: 'inline-block', marginLeft: '10px' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
