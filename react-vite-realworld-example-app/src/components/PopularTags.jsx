import React from 'react'
import { useQuery } from 'react-query'

function PopularTags({ onTagClick }) {
  const { data, isFetching, isError } = useQuery('/tags', { placeholderData: { tags: [] } })

  function content() {
    if (isFetching) return <p>Loading tags...</p>
    if (isError) return <p>Loading tags failed :(</p>

    // 确保 data.tags 是一个数组
    if (!Array.isArray(data.tags) || data.tags.length === 0) {
      return <p>No tags available</p>;
    }

    return data.tags.map((tag) => (
      <a
        href="#"
        key={tag}
        className="tag-pill tag-default"
        onClick={(e) => {
          e.preventDefault()
          onTagClick(tag)
        }}
      >
        {tag}
      </a>
    ))
  }

  return (
    <div className="sidebar">
      <p>Popular Tags</p>
      <div className="tag-list">{content()}</div>
    </div>
  )
}

export default PopularTags
