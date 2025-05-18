import classNames from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'
import { ArticleList, FollowProfileButton } from '../components'
import { useAuth, useProfileQuery } from '../hooks'

function Profile() {
    //3/23
const { data, error, isLoading } = useProfileQuery();

//   const { data } = useProfileQuery()
//end
  const { authUser } = useAuth()
  const [filters, setFilters] = React.useState({ author: '', favorited: '' })

//begin
  const setAuthorFilter = React.useCallback(() => {
    setFilters({ author: data?.profile?.username, favorited: '' });
  }, [data?.profile?.username]);

  React.useEffect(() => {
    if (data?.profile?.username) {
      setAuthorFilter();
    }
  }, [data?.profile?.username, setAuthorFilter]);


console.log("Fetched data:", data);
console.log("Profile error:", error);  // 打印是否有错误
console.log("Profile loading:", isLoading);  // 打印加载状态



  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error loading profile: {error.message}</div>;
  }

  if (!data || !data.profile) {
    console.log("No profile data found");
    return <div>No profile data found</div>;
  }


//   const { username, image, bio } = data.profile
const { username, bio, image } = data.profile;

//end
  const canUpdateProfile = authUser?.username === username
//   const setAuthorFilter = React.useCallback(() => {
//     setFilters({ author: username, favorited: '' })
//   }, [username])
//
//   React.useEffect(() => {
//     setAuthorFilter()
//   }, [username, setAuthorFilter])

  return (
    <div className="profile-page">
      <div className="user-info">
        <div className="container">
          <div className="row">
            <div className="col-xs-12 col-md-10 offset-md-1">
              <img src={image} className="user-img" />
              <h4>{username}</h4>
              <p>{bio}</p>
              {canUpdateProfile ? (
                <Link className="btn btn-sm btn-outline-secondary action-btn" to="/settings">
                  <i className="ion-gear-a" /> Edit Profile Settings
                </Link>
              ) : (
                <FollowProfileButton />
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        <div className="row">
          <div className="col-xs-12 col-md-10 offset-md-1">
            <div className="articles-toggle">
              <ul className="nav nav-pills outline-active">
                <li className="nav-item">
                  <button
                    onClick={setAuthorFilter}
                    type="button"
                    className={classNames('nav-link', {
                      active: filters?.author,
                    })}
                  >
                    My Articles
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    onClick={() => setFilters({ author: '', favorited: username })}
                    type="button"
                    className={classNames('nav-link', {
                      active: filters?.favorited,
                    })}
                  >
                    Favorited Articles
                  </button>
                </li>
              </ul>
            </div>
            <ArticleList filters={filters} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
