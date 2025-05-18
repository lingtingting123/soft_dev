import React from 'react'
import { ArticleMeta, ArticleComments } from '../components'
import { useArticleQuery } from '../hooks'

function Article() {
  const { data } = useArticleQuery()
  const { title, description, body } = data.article

  React.useEffect(() => {
    const hasReloaded = sessionStorage.getItem('hasReloadedArticlePage');
    if (!hasReloaded) {
      sessionStorage.setItem('hasReloadedArticlePage', 'true');
      window.location.reload();
    }
  }, []);

  React.useEffect(() => {
    return () => {
      sessionStorage.removeItem('hasReloadedArticlePage');
    };
  }, []);

  if (!data || !data.article) {
    return <div>Loading...</div>;
  }

  return (
    <div className="article-page">
      <div className="banner">
        <div className="container">
          <h1>{title}</h1>
          <ArticleMeta />
        </div>
      </div>
      <div className="container page">
        <div className="row article-content">
          <div className="col-md-12">
            <p>{description}</p>
            <p>{body}</p>
          </div>
        </div>
        <hr />
        <div className="article-actions">
          <ArticleMeta />
        </div>
        <div className="row">
          <div className="col-xs-12 col-md-8 offset-md-2">
            <ArticleComments />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Article
